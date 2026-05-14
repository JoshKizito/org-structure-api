from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status

from app.core.config import settings
from app.models.department import Department
from app.models.employee import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.department import DepartmentCreate, DepartmentTree, DepartmentUpdate, EmployeeReadBrief, DepartmentRead


class DepartmentService:
    def __init__(
        self,
        dept_repo: DepartmentRepository,
        emp_repo: EmployeeRepository,
    ) -> None:
        self._dept_repo = dept_repo
        self._emp_repo = emp_repo

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create_department(self, payload: DepartmentCreate) -> Department:
        # Validate parent exists
        if payload.parent_id is not None:
            if not await self._dept_repo.exists(payload.parent_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent department {payload.parent_id} not found.",
                )

        # Unique name within the same parent
        if await self._dept_repo.name_exists_in_parent(payload.name, payload.parent_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"A department named '{payload.name}' already exists "
                    f"under parent_id={payload.parent_id}."
                ),
            )

        return await self._dept_repo.create(name=payload.name, parent_id=payload.parent_id)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_department_tree(
        self,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTree:
        depth = max(1, min(depth, settings.MAX_TREE_DEPTH))

        dept = await self._dept_repo.get_by_id(department_id)
        if dept is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department {department_id} not found.",
            )

        return await self._build_tree(dept, depth, include_employees)

    async def _build_tree(
        self,
        dept: Department,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTree:
        employees: list[EmployeeReadBrief] = []
        if include_employees:
            raw_emps = await self._emp_repo.get_by_department(dept.id)
            employees = [EmployeeReadBrief.model_validate(e) for e in raw_emps]

        children: list[DepartmentTree] = []
        if depth > 1:
            for child in sorted(dept.children, key=lambda c: c.name):
                child_tree = await self._build_tree(child, depth - 1, include_employees)
                children.append(child_tree)

        return DepartmentTree(
            department=DepartmentRead.model_validate(dept),
            employees=employees,
            children=children,
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update_department(
        self, department_id: int, payload: DepartmentUpdate
    ) -> Department:
        dept = await self._dept_repo.get_by_id(department_id)
        if dept is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department {department_id} not found.",
            )

        new_parent_id = payload.parent_id
        new_name = payload.name

        # Prevent self-parenting
        if new_parent_id is not None and new_parent_id == department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A department cannot be its own parent.",
            )

        # Prevent cycle: new parent must not be a descendant of this dept
        if new_parent_id is not None:
            descendant_ids = await self._dept_repo.get_descendant_ids(department_id)
            if new_parent_id in descendant_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Setting parent_id={new_parent_id} would create a cycle "
                        f"in the department hierarchy."
                    ),
                )
            # Ensure target parent exists
            if not await self._dept_repo.exists(new_parent_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent department {new_parent_id} not found.",
                )

        # Unique name check (in new or existing parent scope)
        effective_parent = new_parent_id if new_parent_id is not None else dept.parent_id
        effective_name = new_name if new_name is not None else dept.name

        if await self._dept_repo.name_exists_in_parent(
            effective_name, effective_parent, exclude_id=department_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"A department named '{effective_name}' already exists "
                    f"under parent_id={effective_parent}."
                ),
            )

        # Determine whether to clear parent_id
        clear_parent = payload.model_fields_set and "parent_id" in payload.model_fields_set and new_parent_id is None

        return await self._dept_repo.update(
            dept,
            name=new_name,
            parent_id=new_parent_id,
            clear_parent=clear_parent,
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_department_cascade(self, department_id: int) -> None:
        """Delete department and all descendants + their employees (via DB cascade)."""
        dept = await self._dept_repo.get_by_id(department_id)
        if dept is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department {department_id} not found.",
            )
        await self._dept_repo.delete(dept)

    async def delete_department_reassign(
        self, department_id: int, reassign_to_id: int
    ) -> None:
        """
        Move employees from the department (and all descendants) to
        reassign_to_id, then delete the department tree.
        """
        dept = await self._dept_repo.get_by_id(department_id)
        if dept is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department {department_id} not found.",
            )

        if not await self._dept_repo.exists(reassign_to_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target department {reassign_to_id} not found.",
            )

        if reassign_to_id == department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot reassign employees to the department being deleted.",
            )

        # Collect all IDs in the subtree (including the root being deleted)
        descendant_ids = await self._dept_repo.get_descendant_ids(department_id)
        all_source_ids = [department_id, *descendant_ids]

        # Ensure target is not inside the subtree being deleted
        if reassign_to_id in all_source_ids:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Department {reassign_to_id} is a descendant of "
                    f"{department_id} and will be deleted. Choose a different target."
                ),
            )

        await self._emp_repo.bulk_reassign(all_source_ids, reassign_to_id)
        await self._dept_repo.delete(dept)

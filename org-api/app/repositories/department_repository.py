from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.department import Department


class DepartmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _deep_load_opts(depth: int):
        """Build nested selectinload options up to `depth` levels."""
        if depth <= 0:
            return []
        opt = selectinload(Department.employees)
        child_opt = selectinload(Department.children)
        # Recursively nest child loading
        current = child_opt
        for _ in range(depth - 1):
            current = current.selectinload(Department.children)
            current = current.selectinload(Department.employees)
        return [opt, child_opt]

    async def get_by_id(self, department_id: int, load_depth: int = 5) -> Optional[Department]:
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(
                selectinload(Department.employees),
                selectinload(Department.children).selectinload(Department.employees),
                selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.employees),
                selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.employees),
                selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.children)
                .selectinload(Department.employees),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> Sequence[Department]:
        result = await self._session.execute(select(Department))
        return result.scalars().all()

    async def exists(self, department_id: int) -> bool:
        result = await self._session.execute(
            select(Department.id).where(Department.id == department_id)
        )
        return result.scalar_one_or_none() is not None

    async def name_exists_in_parent(
        self,
        name: str,
        parent_id: Optional[int],
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Check uniqueness of name within a given parent scope."""
        stmt = select(Department.id).where(Department.name == name)
        if parent_id is None:
            stmt = stmt.where(Department.parent_id.is_(None))
        else:
            stmt = stmt.where(Department.parent_id == parent_id)
        if exclude_id is not None:
            stmt = stmt.where(Department.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_ancestor_ids(self, department_id: int) -> list[int]:
        """
        Return all ancestor IDs for a given department using a recursive CTE.
        Useful for cycle detection.
        """
        cte = (
            select(Department.id, Department.parent_id)
            .where(Department.id == department_id)
            .cte(name="ancestors", recursive=True)
        )
        parent_alias = cte.alias()
        dept_alias = Department.__table__.alias()
        cte = cte.union_all(
            select(dept_alias.c.id, dept_alias.c.parent_id).where(
                dept_alias.c.id == parent_alias.c.parent_id
            )
        )
        stmt = select(cte.c.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_descendant_ids(self, department_id: int) -> list[int]:
        """Return all descendant IDs using a recursive CTE."""
        cte = (
            select(Department.id, Department.parent_id)
            .where(Department.id == department_id)
            .cte(name="descendants", recursive=True)
        )
        parent_alias = cte.alias()
        dept_alias = Department.__table__.alias()
        cte = cte.union_all(
            select(dept_alias.c.id, dept_alias.c.parent_id).where(
                dept_alias.c.parent_id == parent_alias.c.id
            )
        )
        stmt = select(cte.c.id)
        result = await self._session.execute(stmt)
        ids = list(result.scalars().all())
        # Exclude the root node itself
        return [i for i in ids if i != department_id]

    async def create(self, name: str, parent_id: Optional[int]) -> Department:
        dept = Department(name=name, parent_id=parent_id)
        self._session.add(dept)
        await self._session.flush()
        refreshed = await self.get_by_id(dept.id)
        return refreshed  # type: ignore[return-value]

    async def update(
        self,
        department: Department,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
        clear_parent: bool = False,
    ) -> Department:
        if name is not None:
            department.name = name
        if clear_parent:
            department.parent_id = None
        elif parent_id is not None:
            department.parent_id = parent_id
        self._session.add(department)
        await self._session.flush()
        # Re-fetch with eager loading to return fresh data
        refreshed = await self.get_by_id(department.id)
        return refreshed  # type: ignore[return-value]

    async def delete(self, department: Department) -> None:
        await self._session.delete(department)
        await self._session.flush()

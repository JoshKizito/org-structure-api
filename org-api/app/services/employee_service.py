from __future__ import annotations

from fastapi import HTTPException, status

from app.models.employee import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate


class EmployeeService:
    def __init__(
        self,
        dept_repo: DepartmentRepository,
        emp_repo: EmployeeRepository,
    ) -> None:
        self._dept_repo = dept_repo
        self._emp_repo = emp_repo

    async def create_employee(
        self, department_id: int, payload: EmployeeCreate
    ) -> Employee:
        if not await self._dept_repo.exists(department_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department {department_id} not found.",
            )

        return await self._emp_repo.create(
            department_id=department_id,
            full_name=payload.full_name,
            position=payload.position,
            hired_at=payload.hired_at,
        )

    async def delete_employee(self, employee_id: int) -> None:
        from fastapi import HTTPException, status
        emp = await self._emp_repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found.",
            )
        await self._emp_repo.delete(emp)

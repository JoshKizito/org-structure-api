from __future__ import annotations

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        return await self._session.get(Employee, employee_id)

    async def get_by_department(self, department_id: int) -> Sequence[Employee]:
        result = await self._session.execute(
            select(Employee)
            .where(Employee.department_id == department_id)
            .order_by(Employee.full_name)
        )
        return result.scalars().all()

    async def create(
        self,
        department_id: int,
        full_name: str,
        position: str,
        hired_at: Optional[date],
    ) -> Employee:
        emp = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )
        self._session.add(emp)
        await self._session.flush()
        await self._session.refresh(emp)
        return emp

    async def reassign_to_department(
        self, from_department_id: int, to_department_id: int
    ) -> int:
        """Move all employees from one department to another. Returns affected count."""
        await self._session.execute(
            update(Employee)
            .where(Employee.department_id == from_department_id)
            .values(department_id=to_department_id)
        )
        return 0

    async def bulk_reassign(self, from_ids: list[int], to_department_id: int) -> int:
        """Move all employees from multiple departments to a single target."""
        if not from_ids:
            return 0
        await self._session.execute(
            update(Employee)
            .where(Employee.department_id.in_(from_ids))
            .values(department_id=to_department_id)
        )
        # Expire the identity map so subsequent queries see the updated rows
        self._session.expire_all()
        return 0  # row count not needed by callers

    async def delete(self, employee: Employee) -> None:
        await self._session.delete(employee)
        await self._session.flush()

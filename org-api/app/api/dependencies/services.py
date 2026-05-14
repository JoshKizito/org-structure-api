from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService


async def get_department_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> DepartmentRepository:
    return DepartmentRepository(session)


async def get_employee_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> EmployeeRepository:
    return EmployeeRepository(session)


async def get_department_service(
    dept_repo: Annotated[DepartmentRepository, Depends(get_department_repo)],
    emp_repo: Annotated[EmployeeRepository, Depends(get_employee_repo)],
) -> DepartmentService:
    return DepartmentService(dept_repo=dept_repo, emp_repo=emp_repo)


async def get_employee_service(
    dept_repo: Annotated[DepartmentRepository, Depends(get_department_repo)],
    emp_repo: Annotated[EmployeeRepository, Depends(get_employee_repo)],
) -> EmployeeService:
    return EmployeeService(dept_repo=dept_repo, emp_repo=emp_repo)

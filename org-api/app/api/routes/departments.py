from __future__ import annotations

from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.services import get_department_service, get_employee_service
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentTree, DepartmentUpdate
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/", response_model=list[DepartmentRead], summary="List all departments")
async def list_departments(
    service: Annotated[DepartmentService, Depends(get_department_service)],
) -> list[DepartmentRead]:
    depts = await service._dept_repo.get_all()
    return [DepartmentRead.model_validate(d) for d in depts if d.parent_id is None]

@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED, summary="Create a department")
async def create_department(payload: DepartmentCreate, service: Annotated[DepartmentService, Depends(get_department_service)]) -> DepartmentRead:
    dept = await service.create_department(payload)
    return DepartmentRead.model_validate(dept)


@router.get("/{department_id}", response_model=DepartmentTree, summary="Get a department with its recursive tree")
async def get_department(
    department_id: int,
    service: Annotated[DepartmentService, Depends(get_department_service)],
    depth: int = Query(default=1, ge=1, le=5),
    include_employees: bool = Query(default=False),
) -> DepartmentTree:
    return await service.get_department_tree(department_id=department_id, depth=depth, include_employees=include_employees)


@router.patch("/{department_id}", response_model=DepartmentRead, summary="Update a department")
async def update_department(department_id: int, payload: DepartmentUpdate, service: Annotated[DepartmentService, Depends(get_department_service)]) -> DepartmentRead:
    dept = await service.update_department(department_id, payload)
    return DepartmentRead.model_validate(dept)


@router.delete("/{department_id}", status_code=status.HTTP_200_OK, summary="Delete a department")
async def delete_department(
    department_id: int,
    service: Annotated[DepartmentService, Depends(get_department_service)],
    mode: Literal["cascade", "reassign"] = Query(default="cascade"),
    reassign_to_department_id: Optional[int] = Query(default=None),
) -> dict:
    if mode == "reassign":
        if reassign_to_department_id is None:
            raise HTTPException(status_code=422, detail="reassign_to_department_id is required when mode=reassign.")
        await service.delete_department_reassign(department_id, reassign_to_department_id)
    else:
        await service.delete_department_cascade(department_id)
    return {"deleted": True}


@router.post("/{department_id}/employees/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED, summary="Create an employee")
async def create_employee(department_id: int, payload: EmployeeCreate, service: Annotated[EmployeeService, Depends(get_employee_service)]) -> EmployeeRead:
    emp = await service.create_employee(department_id, payload)
    return EmployeeRead.model_validate(emp)


@router.delete("/{department_id}/employees/{employee_id}", status_code=status.HTTP_200_OK, summary="Delete an employee")
async def delete_employee(
    department_id: int,
    employee_id: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> dict:
    await service.delete_employee(employee_id)
    return {"deleted": True}

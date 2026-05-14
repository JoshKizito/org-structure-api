"""Tests for the departments API."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_dept(client: AsyncClient, name: str, parent_id: int | None = None) -> dict:
    payload: dict = {"name": name}
    if parent_id is not None:
        payload["parent_id"] = parent_id
    resp = await client.post("/api/v1/departments/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Create department
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_department_success(client: AsyncClient) -> None:
    data = await _create_dept(client, "Engineering")
    assert data["name"] == "Engineering"
    assert data["id"] is not None
    assert data["parent_id"] is None


@pytest.mark.asyncio
async def test_create_department_with_parent(client: AsyncClient) -> None:
    parent = await _create_dept(client, "Tech")
    child = await _create_dept(client, "Backend", parent_id=parent["id"])
    assert child["parent_id"] == parent["id"]


@pytest.mark.asyncio
async def test_create_department_blank_name_rejected(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/departments/", json={"name": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_department_name_trimmed(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/departments/", json={"name": "  HR  "})
    assert resp.status_code == 201
    assert resp.json()["name"] == "HR"


@pytest.mark.asyncio
async def test_create_department_duplicate_name_same_parent(client: AsyncClient) -> None:
    await _create_dept(client, "Sales")
    resp = await client.post("/api/v1/departments/", json={"name": "Sales"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_department_nonexistent_parent(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/departments/", json={"name": "Ghost", "parent_id": 99999})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 2. Create employee
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_employee_success(client: AsyncClient) -> None:
    dept = await _create_dept(client, "Finance")
    resp = await client.post(
        f"/api/v1/departments/{dept['id']}/employees/",
        json={"full_name": "Alice Smith", "position": "Accountant", "hired_at": "2024-03-01"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["full_name"] == "Alice Smith"
    assert data["department_id"] == dept["id"]


@pytest.mark.asyncio
async def test_create_employee_nonexistent_department(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/departments/99999/employees/",
        json={"full_name": "Nobody", "position": "Ghost"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_employee_blank_name_rejected(client: AsyncClient) -> None:
    dept = await _create_dept(client, "QA")
    resp = await client.post(
        f"/api/v1/departments/{dept['id']}/employees/",
        json={"full_name": "  ", "position": "Tester"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. Get department tree
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_department_tree_depth_and_employees(client: AsyncClient) -> None:
    root = await _create_dept(client, "Root")
    child = await _create_dept(client, "Child", parent_id=root["id"])
    # Add an employee to child
    await client.post(
        f"/api/v1/departments/{child['id']}/employees/",
        json={"full_name": "Bob Jones", "position": "Dev"},
    )
    resp = await client.get(
        f"/api/v1/departments/{root['id']}",
        params={"depth": 2, "include_employees": "true"},
    )
    assert resp.status_code == 200
    tree = resp.json()
    assert tree["department"]["id"] == root["id"]
    assert len(tree["children"]) == 1
    child_tree = tree["children"][0]
    assert child_tree["department"]["id"] == child["id"]
    assert len(child_tree["employees"]) == 1
    assert child_tree["employees"][0]["full_name"] == "Bob Jones"


@pytest.mark.asyncio
async def test_get_department_not_found(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/departments/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_department_depth_capped_at_5(client: AsyncClient) -> None:
    dept = await _create_dept(client, "DepthTest")
    resp = await client.get(f"/api/v1/departments/{dept['id']}", params={"depth": 100})
    assert resp.status_code == 422  # FastAPI clamps via Query(le=5)


# ---------------------------------------------------------------------------
# 4. Update department (cycle prevention)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_department_name(client: AsyncClient) -> None:
    dept = await _create_dept(client, "OldName")
    resp = await client.patch(f"/api/v1/departments/{dept['id']}", json={"name": "NewName"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "NewName"


@pytest.mark.asyncio
async def test_prevent_self_parent(client: AsyncClient) -> None:
    dept = await _create_dept(client, "SelfRef")
    resp = await client.patch(
        f"/api/v1/departments/{dept['id']}",
        json={"parent_id": dept["id"]},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_prevent_cycle(client: AsyncClient) -> None:
    """
    A → B → C: trying to set A's parent to C must be rejected.
    """
    a = await _create_dept(client, "CycleA")
    b = await _create_dept(client, "CycleB", parent_id=a["id"])
    c = await _create_dept(client, "CycleC", parent_id=b["id"])

    # Attempt: make A a child of C (would create A→B→C→A)
    resp = await client.patch(f"/api/v1/departments/{a['id']}", json={"parent_id": c["id"]})
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# 5. Delete cascade
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_cascade(client: AsyncClient) -> None:
    root = await _create_dept(client, "CascadeRoot")
    child = await _create_dept(client, "CascadeChild", parent_id=root["id"])
    # Add employee to child
    await client.post(
        f"/api/v1/departments/{child['id']}/employees/",
        json={"full_name": "Eve", "position": "PM"},
    )

    resp = await client.delete(f"/api/v1/departments/{root['id']}?mode=cascade")
    assert resp.status_code == 204

    # Both departments should be gone
    assert (await client.get(f"/api/v1/departments/{root['id']}")).status_code == 404
    assert (await client.get(f"/api/v1/departments/{child['id']}")).status_code == 404


# ---------------------------------------------------------------------------
# 6. Delete reassign
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_reassign(client: AsyncClient) -> None:
    source = await _create_dept(client, "ReassignSource")
    target = await _create_dept(client, "ReassignTarget")

    # Add employee to source
    emp_resp = await client.post(
        f"/api/v1/departments/{source['id']}/employees/",
        json={"full_name": "Charlie", "position": "Dev"},
    )
    emp_id = emp_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/departments/{source['id']}",
        params={"mode": "reassign", "reassign_to_department_id": target["id"]},
    )
    assert resp.status_code == 204

    # Source gone
    assert (await client.get(f"/api/v1/departments/{source['id']}")).status_code == 404

    # Target still exists
    tree = (
        await client.get(
            f"/api/v1/departments/{target['id']}",
            params={"include_employees": "true"},
        )
    ).json()
    employee_ids = [e["id"] for e in tree["employees"]]
    assert emp_id in employee_ids


@pytest.mark.asyncio
async def test_delete_reassign_missing_target(client: AsyncClient) -> None:
    dept = await _create_dept(client, "OrphanSource")
    resp = await client.delete(
        f"/api/v1/departments/{dept['id']}",
        params={"mode": "reassign", "reassign_to_department_id": 99999},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_reassign_no_target_id(client: AsyncClient) -> None:
    dept = await _create_dept(client, "MissingParam")
    resp = await client.delete(f"/api/v1/departments/{dept['id']}?mode=reassign")
    assert resp.status_code == 422

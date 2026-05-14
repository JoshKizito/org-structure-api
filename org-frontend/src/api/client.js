const BASE = 'http://localhost:8000/api/v1'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const message = data?.detail || `HTTP ${res.status}`
    const err = new Error(typeof message === 'string' ? message : JSON.stringify(message))
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  listRoots: () => request('/departments/'),

  getDeptTree: (id, depth = 5, includeEmployees = true) =>
    request(`/departments/${id}?depth=${depth}&include_employees=${includeEmployees}`),

  createDept: (body) =>
    request('/departments/', { method: 'POST', body: JSON.stringify(body) }),

  updateDept: (id, body) =>
    request(`/departments/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),

  deleteDeptCascade: (id) =>
    request(`/departments/${id}?mode=cascade`, { method: 'DELETE' }),

  deleteDeptReassign: (id, reassignTo) =>
    request(`/departments/${id}?mode=reassign&reassign_to_department_id=${reassignTo}`, { method: 'DELETE' }),

  createEmployee: (deptId, body) =>
    request(`/departments/${deptId}/employees/`, { method: 'POST', body: JSON.stringify(body) }),

  deleteEmployee: (deptId, empId) =>
    request(`/departments/${deptId}/employees/${empId}`, { method: 'DELETE' }),
}
import { useState, useEffect, useCallback } from 'react'
import { Building2, RefreshCw, Zap } from 'lucide-react'
import { api } from './api/client'
import { Sidebar } from './components/Sidebar'
import { DeptDetail } from './components/DeptDetail'
import { DeptModal } from './components/modals/DeptModal'
import { EmployeeModal } from './components/modals/EmployeeModal'
import { DeleteModal } from './components/modals/DeleteModal'
import { ConfirmDeleteEmployee } from './components/modals/ConfirmDeleteEmployee'
import { ToastContainer } from './components/Toast'
import { useToast } from './hooks/useToast'
import styles from './App.module.css'

function flattenTree(nodes) {
  const result = []
  function walk(node) {
    result.push(node.department)
    node.children?.forEach(walk)
  }
  nodes.forEach(walk)
  return result
}

function findNode(nodes, id) {
  for (const node of nodes) {
    if (node.department.id === id) return node
    const found = findNode(node.children ?? [], id)
    if (found) return found
  }
  return null
}

export default function App() {
  const [roots, setRoots] = useState([])
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)
  const { toasts, toast } = useToast()
  const [modal, setModal] = useState(null)
  // modal types: 'create' | 'edit' | 'employee' | 'delete' | 'delete_employee'

  const smartLoad = useCallback(async (keepSelectedId = undefined) => {
  setLoading(true)
  try {
    const rootDepts = await api.listRoots()
    const trees = await Promise.all(
      rootDepts.map((d) => api.getDeptTree(d.id, 5, true))
    )
    const validTrees = trees.filter(Boolean)
    setRoots(validTrees)

    if (keepSelectedId === null) {
      // Suppression : vider la sélection
      setSelected(null)
    } else if (keepSelectedId !== undefined) {
      // Ajout/modif : retrouver et mettre à jour le nœud
      const refreshed = findNode(validTrees, keepSelectedId)
      setSelected(refreshed ?? null)
    }
  } catch (err) {
    console.error('Erreur chargement:', err)
  } finally {
    setLoading(false)
  }
}, []) // ← tableau vide, plus de dépendance sur selected

  async function handleCreateDept({ name }) {
    const parentId = modal?.parentDept?.id ?? null
    const dept = await api.createDept({ name, parent_id: parentId })
    toast.success(`Отдел «${dept.name}» создан`)
    await smartLoad()
  }

  async function handleEditDept({ name }) {
    await api.updateDept(selected.department.id, { name })
    toast.success('Отдел обновлён')
    await smartLoad()
  }

  async function handleDeleteDept(mode, reassignTo) {
  const name = selected.department.name
  const deletedId = selected.department.id

  if (mode === 'cascade') {
    await api.deleteDeptCascade(deletedId)
  } else {
    await api.deleteDeptReassign(deletedId, reassignTo)
  }
  toast.success(`«${name}» удалён`)
  await smartLoad(null) // ← null = vider la sélection après refresh
}

  async function handleCreateEmployee({ full_name, position, hired_at }) {
  const deptId = selected.department.id
  const emp = await api.createEmployee(deptId, { full_name, position, hired_at })
  toast.success(`${emp.full_name} добавлен`)
  await smartLoad(deptId)  // ← passe l'ID pour garder la sélection
}

async function handleDeleteEmployee() {
  const emp = modal?.employee
  const deptId = selected.department.id
  await api.deleteEmployee(deptId, emp.id)
  toast.success(`${emp.full_name} удалён`)
  await smartLoad(deptId)  // ← passe l'ID pour garder la sélection
}

  function closeModal() { setModal(null) }

  const allDepts = flattenTree(roots)

  return (
    <div className={styles.app}>
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <Zap size={16} style={{ color: 'var(--accent)' }} />
          <span className={styles.brandName}>ОргСтруктура</span>
          <span className={styles.brandTag}>Панель управления</span>
        </div>
        <div className={styles.topMeta}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-muted)' }}>
            {allDepts.length} {allDepts.length === 1 ? 'отдел' : allDepts.length < 5 ? 'отдела' : 'отделов'}
          </span>
          <button className="btn-icon" onClick={smartLoad} disabled={loading} title="Обновить">
            <RefreshCw size={14} style={loading ? { animation: 'spin 0.8s linear infinite' } : {}} />
          </button>
          <div className={styles.apiDot} title="API: http://localhost:8001" />
        </div>
      </header>

      <div className={styles.body}>
        <Sidebar
          roots={roots}
          selectedId={selected?.department?.id}
          onSelect={setSelected}
          onAddRoot={() => setModal({ type: 'create', parentDept: null })}
          onAddChild={(dept) => setModal({ type: 'create', parentDept: dept })}
          loading={loading}
        />
        <main className={styles.main}>
          <DeptDetail
            node={selected}
            onEdit={() => setModal({ type: 'edit' })}
            onDelete={() => setModal({ type: 'delete' })}
            onAddEmployee={() => setModal({ type: 'employee' })}
            onSelectChild={(childNode) => setSelected(childNode)}
            onDeleteEmployee={(emp) => setModal({ type: 'delete_employee', employee: emp })}
          />
        </main>
      </div>

      {modal?.type === 'create' && (
        <DeptModal mode="create" parentDept={modal.parentDept} onConfirm={handleCreateDept} onClose={closeModal} />
      )}
      {modal?.type === 'edit' && (
        <DeptModal mode="edit" initial={selected?.department} onConfirm={handleEditDept} onClose={closeModal} />
      )}
      {modal?.type === 'employee' && (
        <EmployeeModal deptName={selected?.department?.name} onConfirm={handleCreateEmployee} onClose={closeModal} />
      )}
      {modal?.type === 'delete' && (
        <DeleteModal dept={selected?.department} allDepts={allDepts} onConfirm={handleDeleteDept} onClose={closeModal} />
      )}
      {modal?.type === 'delete_employee' && (
        <ConfirmDeleteEmployee employee={modal.employee} onConfirm={handleDeleteEmployee} onClose={closeModal} />
      )}

      <ToastContainer toasts={toasts} />
    </div>
  )
}

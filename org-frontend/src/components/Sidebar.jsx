import { useState } from 'react'
import { ChevronRight, ChevronDown, Building2, Plus, Search } from 'lucide-react'
import styles from './Sidebar.module.css'

function DeptNode({ node, depth, selectedId, onSelect, onAddChild }) {
  const [open, setOpen] = useState(depth === 0)
  const hasChildren = node.children?.length > 0
  const isSelected = selectedId === node.department.id

  return (
    <div className={styles.node} style={{ '--depth': depth }}>
      <div
        className={`${styles.row} ${isSelected ? styles.selected : ''}`}
        onClick={() => onSelect(node)}
      >
        <button
          className={styles.toggle}
          onClick={(e) => { e.stopPropagation(); setOpen((o) => !o) }}
          style={{ visibility: hasChildren ? 'visible' : 'hidden' }}
        >
          {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </button>

        <Building2
          size={13}
          className={styles.icon}
          style={{ color: isSelected ? 'var(--accent)' : 'var(--text-muted)' }}
        />

        <span className={`${styles.name} truncate`}>{node.department.name}</span>

        {node.employees?.length > 0 && (
          <span className={styles.count}>{node.employees.length}</span>
        )}

        <button
          className={`${styles.addBtn} btn-icon`}
          onClick={(e) => { e.stopPropagation(); onAddChild(node.department) }}
          title="Добавить подотдел"
        >
          <Plus size={12} />
        </button>
      </div>

      {open && hasChildren && (
        <div className={styles.children}>
          {node.children.map((child) => (
            <DeptNode
              key={child.department.id}
              node={child}
              depth={depth + 1}
              selectedId={selectedId}
              onSelect={onSelect}
              onAddChild={onAddChild}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function Sidebar({ roots, selectedId, onSelect, onAddRoot, onAddChild, loading }) {
  const [search, setSearch] = useState('')

  const filtered = search
    ? roots.filter((r) => r.department.name.toLowerCase().includes(search.toLowerCase()))
    : roots

  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <span className={styles.title}>
          <Building2 size={14} style={{ color: 'var(--accent)' }} />
          Отделы
        </span>
        <button className="btn btn-icon" onClick={onAddRoot} title="Новый корневой отдел">
          <Plus size={14} />
        </button>
      </div>

      <div className={styles.search}>
        <Search size={12} className={styles.searchIcon} />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Поиск отделов…"
          className={styles.searchInput}
        />
      </div>

      <div className={styles.tree}>
        {loading && <div className={styles.loading}><span className="spinner" /></div>}

        {!loading && filtered.length === 0 && (
          <div className="empty-state" style={{ padding: '32px 16px' }}>
            <Building2 size={28} style={{ opacity: 0.3 }} />
            <span style={{ fontSize: 12 }}>Нет отделов</span>
          </div>
        )}

        {!loading && filtered.map((root) => (
          <DeptNode
            key={root.department.id}
            node={root}
            depth={0}
            selectedId={selectedId}
            onSelect={onSelect}
            onAddChild={onAddChild}
          />
        ))}
      </div>
    </aside>
  )
}

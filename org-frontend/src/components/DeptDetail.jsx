import { Building2, Edit2, Trash2, UserPlus, Users, Calendar, ChevronRight, GitBranch } from 'lucide-react'
import styles from './DeptDetail.module.css'

function StatCard({ label, value, icon: Icon, accent }) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statIcon} style={accent ? { color: 'var(--accent)' } : {}}>
        <Icon size={16} />
      </div>
      <div>
        <div className={styles.statValue}>{value}</div>
        <div className={styles.statLabel}>{label}</div>
      </div>
    </div>
  )
}

function EmployeeRow({ emp, deptId, onDelete }) {
  const initials = emp.full_name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase()

  return (
    <tr className={styles.empRow}>
      <td className={styles.empCell}>
        <div className={styles.avatar}>{initials}</div>
        <div>
          <div className={styles.empName}>{emp.full_name}</div>
        </div>
      </td>
      <td className={styles.empCell}>
        <span className="badge badge-muted">{emp.position}</span>
      </td>
      <td className={`${styles.empCell} mono`} style={{ color: 'var(--text-muted)', fontSize: 12 }}>
        {emp.hired_at ?? '—'}
      </td>
      <td className={styles.empCell} style={{ textAlign: 'right' }}>
        <button
          className="btn-icon danger"
          title="Удалить сотрудника"
          onClick={() => onDelete(emp)}
        >
          <Trash2 size={13} />
        </button>
      </td>
    </tr>
  )
}

export function DeptDetail({ node, onEdit, onDelete, onAddEmployee, onSelectChild, onDeleteEmployee }) {
  if (!node) {
    return (
      <div className={styles.empty}>
        <Building2 size={40} style={{ opacity: 0.15 }} />
        <p>Выберите отдел из боковой панели</p>
        <p style={{ fontSize: 12 }}>или создайте новый с помощью кнопки +</p>
      </div>
    )
  }

  const { department: dept, employees = [], children = [] } = node

  const countDescendantEmployees = (n) => {
    let total = n.employees?.length ?? 0
    for (const c of n.children ?? []) total += countDescendantEmployees(c)
    return total
  }

  const totalEmployees = countDescendantEmployees(node)

  return (
    <div className={`${styles.detail} fade-in`}>
      {/* Заголовок */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.deptIcon}>
            <Building2 size={20} />
          </div>
          <div>
            <h1 className={styles.deptName}>{dept.name}</h1>
            <div className={styles.meta}>
              <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                ID #{dept.id}
              </span>
              {dept.parent_id && (
                <>
                  <span style={{ color: 'var(--text-muted)' }}>·</span>
                  <ChevronRight size={10} style={{ color: 'var(--text-muted)' }} />
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    родитель #{dept.parent_id}
                  </span>
                </>
              )}
              <span style={{ color: 'var(--text-muted)' }}>·</span>
              <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {new Date(dept.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.actions}>
          <button className="btn btn-ghost" onClick={onAddEmployee}>
            <UserPlus size={14} />
            Добавить сотрудника
          </button>
          <button className="btn btn-ghost" onClick={onEdit}>
            <Edit2 size={14} />
            Изменить
          </button>
          <button className="btn btn-danger" onClick={onDelete}>
            <Trash2 size={14} />
            Удалить
          </button>
        </div>
      </div>

      <hr className="divider" />

      {/* Статистика */}
      <div className={styles.stats}>
        <StatCard label="Сотрудников в отделе" value={employees.length} icon={Users} accent />
        <StatCard label="Всего (вкл. подотделы)" value={totalEmployees} icon={Users} />
        <StatCard label="Подотделов" value={children.length} icon={GitBranch} />
        <StatCard
          label="Дата создания"
          value={new Date(dept.created_at).toLocaleDateString('ru-RU')}
          icon={Calendar}
        />
      </div>

      {/* Подотделы */}
      {children.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>
            <GitBranch size={13} /> Подотделы
          </h2>
          <div className={styles.chips}>
            {children.map((c) => (
              <button
                key={c.department.id}
                className={styles.chip}
                onClick={() => onSelectChild(c)}
              >
                <Building2 size={11} />
                {c.department.name}
                {c.employees?.length > 0 && (
                  <span className={styles.chipCount}>{c.employees.length}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Таблица сотрудников */}
      <div className={styles.section} style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <h2 className={styles.sectionTitle}>
          <Users size={13} /> Сотрудники
          {employees.length > 0 && (
            <span className="badge badge-muted" style={{ marginLeft: 8 }}>
              {employees.length}
            </span>
          )}
        </h2>

        {employees.length === 0 ? (
          <div className="empty-state" style={{ padding: '32px' }}>
            <Users size={28} style={{ opacity: 0.2 }} />
            <span style={{ fontSize: 12 }}>В этом отделе нет сотрудников</span>
            <button className="btn btn-ghost" style={{ marginTop: 4 }} onClick={onAddEmployee}>
              <UserPlus size={13} /> Добавить первого сотрудника
            </button>
          </div>
        ) : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Имя</th>
                  <th>Должность</th>
                  <th>Принят</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {employees.map((e) => (
                  <EmployeeRow
                    key={e.id}
                    emp={e}
                    deptId={dept.id}
                    onDelete={onDeleteEmployee}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

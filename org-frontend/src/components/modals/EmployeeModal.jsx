import { useState } from 'react'
import { UserPlus, X } from 'lucide-react'

export function EmployeeModal({ deptName, onConfirm, onClose }) {
  const [form, setForm] = useState({ full_name: '', position: '', hired_at: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.full_name.trim()) { setError('ФИО обязательно'); return }
    if (!form.position.trim())  { setError('Должность обязательна'); return }
    setBusy(true); setError('')
    try {
      await onConfirm({ full_name: form.full_name.trim(), position: form.position.trim(), hired_at: form.hired_at || null })
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div style={{ padding: '20px 20px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <UserPlus size={16} style={{ color: 'var(--accent)' }} />
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Новый сотрудник</h2>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>
        <div style={{ padding: '6px 20px 0', fontSize: 12, color: 'var(--text-muted)' }}>
          Отдел: <span style={{ color: 'var(--text-secondary)' }}>{deptName}</span>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="field">
            <label>ФИО</label>
            <input value={form.full_name} onChange={set('full_name')} placeholder="Иванов Иван Иванович" autoFocus maxLength={200} />
          </div>
          <div className="field">
            <label>Должность</label>
            <input value={form.position} onChange={set('position')} placeholder="Старший разработчик" maxLength={200} />
          </div>
          <div className="field">
            <label>Дата приёма <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(необязательно)</span></label>
            <input type="date" value={form.hired_at} onChange={set('hired_at')} />
          </div>

          {error && <span style={{ fontSize: 12, color: 'var(--danger)' }}>{error}</span>}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 4 }}>
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={busy}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? <span className="spinner" /> : 'Добавить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

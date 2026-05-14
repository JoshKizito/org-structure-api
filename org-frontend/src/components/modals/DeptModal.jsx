import { useState, useEffect } from 'react'
import { Building2, X } from 'lucide-react'

export function DeptModal({ mode, initial, parentDept, onConfirm, onClose }) {
  const [name, setName] = useState(initial?.name ?? '')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => { setName(initial?.name ?? ''); setError('') }, [initial])

  const isEdit = mode === 'edit'
  const title = isEdit
    ? 'Редактировать отдел'
    : parentDept ? `Новый подотдел` : 'Новый корневой отдел'

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = name.trim()
    if (!trimmed) { setError('Название обязательно'); return }
    setBusy(true); setError('')
    try {
      await onConfirm({ name: trimmed })
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
            <Building2 size={16} style={{ color: 'var(--accent)' }} />
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>{title}</h2>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>

        {parentDept && (
          <div style={{ padding: '8px 20px 0', color: 'var(--text-muted)', fontSize: 12 }}>
            Родительский отдел: <span style={{ color: 'var(--text-secondary)' }}>{parentDept.name}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="field">
            <label htmlFor="dept-name">Название отдела</label>
            <input
              id="dept-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="напр. Бэкенд, Маркетинг…"
              autoFocus
              maxLength={200}
            />
            {error && <span style={{ fontSize: 12, color: 'var(--danger)' }}>{error}</span>}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={busy}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? <span className="spinner" /> : isEdit ? 'Сохранить' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

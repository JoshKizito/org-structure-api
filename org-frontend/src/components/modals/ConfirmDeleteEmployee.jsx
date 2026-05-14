import { useState } from 'react'
import { UserX, X, AlertTriangle } from 'lucide-react'

export function ConfirmDeleteEmployee({ employee, onConfirm, onClose }) {
  const [busy, setBusy] = useState(false)

  async function handleConfirm() {
    setBusy(true)
    try {
      await onConfirm()
      onClose()
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <div style={{ padding: '20px 20px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <UserX size={16} style={{ color: 'var(--danger)' }} />
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Удалить сотрудника</h2>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>

        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{
            background: 'var(--danger-dim)', border: '1px solid rgba(248,113,113,0.25)',
            borderRadius: 'var(--radius-md)', padding: '12px 14px',
            display: 'flex', alignItems: 'flex-start', gap: 8
          }}>
            <AlertTriangle size={14} style={{ color: 'var(--danger)', flexShrink: 0, marginTop: 1 }} />
            <span style={{ fontSize: 13, color: 'var(--danger)' }}>
              Удалить <strong>{employee?.full_name}</strong> из системы? Это действие необратимо.
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button className="btn btn-ghost" onClick={onClose} disabled={busy}>Отмена</button>
            <button className="btn btn-danger" onClick={handleConfirm} disabled={busy}>
              {busy ? <span className="spinner" /> : 'Удалить'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

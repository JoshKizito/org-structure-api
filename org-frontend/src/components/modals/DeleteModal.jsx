import { useState } from 'react'
import { Trash2, X, AlertTriangle } from 'lucide-react'

export function DeleteModal({ dept, allDepts, onConfirm, onClose }) {
  const [mode, setMode] = useState('cascade')
  const [reassignId, setReassignId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const targets = allDepts.filter((d) => d.id !== dept.id)

  async function handleSubmit(e) {
    e.preventDefault()
    if (mode === 'reassign' && !reassignId) { setError('Выберите отдел назначения'); return }
    setBusy(true); setError('')
    try {
      await onConfirm(mode, mode === 'reassign' ? Number(reassignId) : null)
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
            <Trash2 size={16} style={{ color: 'var(--danger)' }} />
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Удалить отдел</h2>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{
            background: 'var(--danger-dim)', border: '1px solid rgba(248,113,113,0.25)',
            borderRadius: 'var(--radius-md)', padding: '10px 12px',
            display: 'flex', alignItems: 'flex-start', gap: 8
          }}>
            <AlertTriangle size={14} style={{ color: 'var(--danger)', flexShrink: 0, marginTop: 1 }} />
            <span style={{ fontSize: 12, color: 'var(--danger)' }}>
              Вы собираетесь удалить <strong>«{dept.name}»</strong>. Это действие необратимо.
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Режим удаления
            </span>
            {[
              { value: 'cascade', label: 'Каскадное удаление', desc: 'Удалить отдел, все подотделы и всех сотрудников' },
              { value: 'reassign', label: 'Перевод сотрудников', desc: 'Переместить всех сотрудников в другой отдел перед удалением' },
            ].map((opt) => (
              <label key={opt.value} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10, cursor: 'pointer',
                background: mode === opt.value ? 'var(--bg-hover)' : 'var(--bg-surface)',
                border: `1px solid ${mode === opt.value ? 'var(--border-bright)' : 'var(--border)'}`,
                borderRadius: 'var(--radius-md)', padding: '10px 12px',
                transition: 'all var(--transition)'
              }}>
                <input type="radio" name="mode" value={opt.value} checked={mode === opt.value}
                  onChange={() => setMode(opt.value)} style={{ marginTop: 2 }} />
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{opt.label}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{opt.desc}</div>
                </div>
              </label>
            ))}
          </div>

          {mode === 'reassign' && (
            <div className="field">
              <label>Перевести сотрудников в</label>
              <select value={reassignId} onChange={(e) => setReassignId(e.target.value)}>
                <option value="">— Выберите отдел —</option>
                {targets.map((d) => (
                  <option key={d.id} value={d.id}>{d.name} (#{d.id})</option>
                ))}
              </select>
            </div>
          )}

          {error && <span style={{ fontSize: 12, color: 'var(--danger)' }}>{error}</span>}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={busy}>Отмена</button>
            <button type="submit" className="btn btn-danger" disabled={busy}>
              {busy ? <span className="spinner" /> : 'Подтвердить удаление'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

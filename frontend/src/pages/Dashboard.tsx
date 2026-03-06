import { useEffect, useState } from 'react'
import { getSummary } from '../api/reports'
import type { ReportSummary } from '../api/reports'

const cards: { key: keyof ReportSummary; label: string; className: string }[] = [
  { key: 'total_assets', label: 'Total assets', className: 'text-cyan-400' },
  { key: 'active_assets', label: 'Active assets', className: 'text-emerald-400' },
  { key: 'total_repairs', label: 'Repairs', className: 'text-amber-400' },
  { key: 'maintenance_plans', label: 'Maintenance plans', className: 'text-violet-400' },
  { key: 'verification_scans', label: 'Verification scans', className: 'text-rose-400' },
]

export default function Dashboard() {
  const [data, setData] = useState<ReportSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getSummary()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-[var(--muted)]">Loading dashboard…</p>
  if (error) return <p className="text-red-400">{error}</p>
  if (!data) return null

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {cards.map(({ key, label, className }) => (
          <div
            key={key}
            className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5"
          >
            <p className="text-sm text-[var(--muted)] mb-1">{label}</p>
            <p className={`text-2xl font-semibold ${className}`}>
              {data[key] ?? 0}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

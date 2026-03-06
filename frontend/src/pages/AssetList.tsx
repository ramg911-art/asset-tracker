import { useEffect, useState } from 'react'
import { getAssets } from '../api/assets'
import type { Asset, Paginated } from '../api/assets'

export default function AssetList() {
  const [data, setData] = useState<Paginated<Asset> | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    getAssets({ page, size: 20 })
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [page])

  if (loading && !data) return <p className="text-[var(--muted)]">Loading…</p>
  if (error) return <p className="text-red-400">{error}</p>

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-6">Assets</h1>
      {data && (
        <>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="px-4 py-3 text-sm font-medium text-[var(--muted)]">Tag</th>
                  <th className="px-4 py-3 text-sm font-medium text-[var(--muted)]">Name</th>
                  <th className="px-4 py-3 text-sm font-medium text-[var(--muted)]">Status</th>
                  <th className="px-4 py-3 text-sm font-medium text-[var(--muted)]">Category ID</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((a) => (
                  <tr key={a.id} className="border-b border-[var(--border)] last:border-0">
                    <td className="px-4 py-3 text-white">{a.asset_tag}</td>
                    <td className="px-4 py-3 text-white">{a.name}</td>
                    <td className="px-4 py-3">
                      <span className="rounded-full px-2 py-0.5 text-xs bg-zinc-700 text-zinc-200">
                        {a.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[var(--muted)]">{a.category_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm text-[var(--muted)]">
            <span>
              Page {data.page} of {data.pages || 1} ({data.total} total)
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={data.page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="text-[var(--accent)] hover:underline disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={data.page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
                className="text-[var(--accent)] hover:underline disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

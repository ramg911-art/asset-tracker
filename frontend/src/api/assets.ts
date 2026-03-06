import { apiGet } from './client'

export interface Asset {
  id: number
  asset_tag: string
  name: string
  category_id: number
  serial_number: string | null
  manufacturer: string | null
  model: string | null
  purchase_date: string | null
  purchase_cost: string | null
  current_location_id: number | null
  department_id: number | null
  status: string
  warranty_start: string | null
  warranty_end: string | null
  amc_start: string | null
  amc_end: string | null
  vendor_id: number | null
  criticality: string | null
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export function getAssets(params?: { page?: number; size?: number; search?: string; status?: string }) {
  const searchParams: Record<string, string> = {}
  if (params?.page) searchParams.page = String(params.page)
  if (params?.size) searchParams.size = String(params.size)
  if (params?.search) searchParams.search = params.search
  if (params?.status) searchParams.status = params.status
  return apiGet<Paginated<Asset>>('/assets', Object.keys(searchParams).length ? searchParams : undefined)
}

export function getAsset(id: number) {
  return apiGet<Asset>(`/assets/${id}`)
}

import { apiGet, apiPost, apiPatch, apiDelete } from './client'

export interface Location {
  id: number
  name: string
  parent_id: number | null
  location_type: string | null
  latitude: number | null
  longitude: number | null
  radius_meters: number | null
  address: string | null
  created_at: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export function getLocations(params?: { page?: number; size?: number; parent_id?: number }) {
  const searchParams: Record<string, string> = {}
  if (params?.page) searchParams.page = String(params.page)
  if (params?.size) searchParams.size = String(params.size)
  if (params?.parent_id != null) searchParams.parent_id = String(params.parent_id)
  return apiGet<Paginated<Location>>('/locations', Object.keys(searchParams).length ? searchParams : undefined)
}

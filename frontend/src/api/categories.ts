import { apiGet } from './client'

export interface AssetCategory {
  id: number
  name: string
  code: string | null
  description: string | null
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export function getCategories(params?: { page?: number; size?: number }) {
  const searchParams: Record<string, string> = {}
  if (params?.page) searchParams.page = String(params.page)
  if (params?.size) searchParams.size = String(params.size)
  return apiGet<Paginated<AssetCategory>>('/categories', Object.keys(searchParams).length ? searchParams : undefined)
}

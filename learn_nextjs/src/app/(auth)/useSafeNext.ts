'use client'

import { useSearchParams } from 'next/navigation'
import { getSafeNextPath } from './getSafeNextPath'

export { getSafeNextPath }

export const useSafeNext = () => {
  const searchParams = useSearchParams()
  return getSafeNextPath(searchParams.get('next') ?? undefined)
}

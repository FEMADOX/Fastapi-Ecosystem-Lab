import { useSearchParams } from 'next/navigation'

export const getSafeNextPath = (
  requestedNext?: string | string[]
): string => {
  const nextPath = Array.isArray(requestedNext)
    ? requestedNext[0]
    : requestedNext

  if (
    nextPath &&
    nextPath.startsWith('/') &&
    !nextPath.startsWith('//')
  ) {
    return nextPath
  }

  return '/'
}

export const useSafeNext = (): string => {
  const searchParams = useSearchParams()
  return getSafeNextPath(searchParams.get('next') ?? undefined)
}

export const getSafeNextPath = (requestedNext?: string | string[]): string => {
  const nextPath = Array.isArray(requestedNext)
    ? requestedNext[0]
    : requestedNext

  if (nextPath && nextPath.startsWith('/') && !nextPath.startsWith('//')) {
    return nextPath
  }

  return '/'
}

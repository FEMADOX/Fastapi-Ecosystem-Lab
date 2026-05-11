import { cookies } from 'next/headers'
import { getItem, getMe } from '@/app/api/server-endpoints'

export const getAuthenticatedUser = async () => {
  const accessToken = (await cookies()).get('access_token')?.value
  if (!accessToken) {
    return {
      success: false,
      error: 'Authentication required. Please log in again.'
    } as const
  }

  const { data: me, error } = await getMe(accessToken)
  if (error || !me) {
    return {
      success: false,
      error: `Failed to verify authentication: ${error ?? 'Unknown error'}.`
    } as const
  }

  return {
    success: true,
    accessToken,
    me
  } as const
}

export const checkItemAuthorization = async (
  itemId: string,
  currentUserId: string,
  isSuperuser: boolean,
  accessToken: string
) => {
  const { data: item, error } = await getItem(itemId)
  if (error || !item) {
    return {
      success: false,
      error: `Failed to load item: ${error ?? 'Unknown error'}.`
    } as const
  }

  if (!isSuperuser && item.user_id !== currentUserId) {
    return {
      success: false,
      error: 'You are not allowed to modify this item.'
    } as const
  }

  return {
    success: true,
    item,
    accessToken
  } as const
}

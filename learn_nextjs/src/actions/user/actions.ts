'use server'

import { updateTag } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { z } from 'zod'

import {
  deleteCurrentUser,
  deleteItem,
  getItem,
  getMe,
  updateCurrentUser,
  updateItem
} from '@/app/api/server-endpoints'
import type { PatchItemRequest } from '@/app/api/types'
import type { MeActionState } from '@/app/me/types'
import { itemPatchFormSchema } from '@/schemas/items/forms'

const profileEmailSchema = z.object({
  email: z.email({
    pattern: z.regexes.email,
    message: 'Invalid email address'
  }),
  currentPassword: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long' })
})

const profilePasswordSchema = z
  .object({
    currentPassword: z
      .string()
      .min(8, { message: 'Password must be at least 8 characters long' }),
    newPassword: z
      .string()
      .min(8, { message: 'Password must be at least 8 characters long' }),
    confirmPassword: z
      .string()
      .min(1, { message: 'Please confirm your password' })
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'New password and confirmation must match',
    path: ['confirmPassword']
  })

const getAuthenticatedUser = async () => {
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

const checkItemAuthorization = async (
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

export const updateProfileEmailAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const authResult = await getAuthenticatedUser()
  if (!authResult.success) {
    return { error: authResult.error }
  }

  const parseResult = profileEmailSchema.safeParse({
    email: formData.get('email'),
    currentPassword: formData.get('currentPassword')
  })

  if (!parseResult.success) {
    return {
      error: parseResult.error.issues[0]?.message ?? 'Invalid form data.'
    }
  }

  const { data: updatedUser, error } = await updateCurrentUser(
    authResult.accessToken,
    {
      email: parseResult.data.email,
      current_password: parseResult.data.currentPassword
    }
  )

  if (error || !updatedUser) {
    return {
      error: `Failed to update profile email: ${error ?? 'Unknown error'}.`
    }
  }

  updateTag('items')

  return { success: 'Email updated successfully.' }
}

export const updateProfilePasswordAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const authResult = await getAuthenticatedUser()
  if (!authResult.success) {
    return { error: authResult.error }
  }

  const parseResult = profilePasswordSchema.safeParse({
    currentPassword: formData.get('currentPassword'),
    newPassword: formData.get('newPassword'),
    confirmPassword: formData.get('confirmPassword')
  })

  if (!parseResult.success) {
    return {
      error: parseResult.error.issues[0]?.message ?? 'Invalid form data.'
    }
  }

  const { data: updatedUser, error } = await updateCurrentUser(
    authResult.accessToken,
    {
      current_password: parseResult.data.currentPassword,
      new_password: parseResult.data.newPassword
    }
  )

  if (error || !updatedUser) {
    return {
      error: `Failed to update password: ${error ?? 'Unknown error'}.`
    }
  }

  return { success: 'Password updated successfully.' }
}

export const deleteAccountAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const confirmDelete = formData.get('confirmDelete')
  if (confirmDelete !== 'DELETE') {
    return { error: 'Type DELETE to confirm account deletion.' }
  }

  const authResult = await getAuthenticatedUser()
  if (!authResult.success) {
    return { error: authResult.error }
  }

  const { error } = await deleteCurrentUser(authResult.accessToken)

  if (error) {
    return {
      error: `Failed to delete account: ${error}.`
    }
  }

  const cookieStore = await cookies()
  cookieStore.delete('access_token')
  cookieStore.delete('refresh_token')
  cookieStore.delete('csrf_token')

  redirect('/signup')
}

export const updateOwnedItemAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const itemId = formData.get('itemId')
  if (typeof itemId !== 'string' || itemId.length === 0) {
    return { error: 'Item ID is required.' }
  }

  const authResult = await getAuthenticatedUser()
  if (!authResult.success) {
    return { error: authResult.error }
  }

  const itemAuthResult = await checkItemAuthorization(
    itemId,
    authResult.me.id,
    authResult.me.is_superuser,
    authResult.accessToken
  )
  if (!itemAuthResult.success) {
    return { error: itemAuthResult.error }
  }

  const rawFormData = Object.fromEntries(formData.entries())
  const parseResult = itemPatchFormSchema.safeParse(rawFormData)
  if (!parseResult.success) {
    return {
      error: parseResult.error.issues[0]?.message ?? 'Invalid form data.'
    }
  }

  const rawImageUrl = formData.get('imageUrl')
  const imageUrl =
    typeof rawImageUrl === 'string' && rawImageUrl.trim().length > 0
      ? rawImageUrl.trim()
      : undefined

  const patchData: PatchItemRequest = {
    user_id: itemAuthResult.item.user_id,
    name: parseResult.data.name,
    description: parseResult.data.description,
    price: parseResult.data.price,
    tax: parseResult.data.tax,
    image_url: imageUrl
  }

  const hasAnyEditableValue =
    patchData.name !== undefined ||
    patchData.description !== undefined ||
    patchData.price !== undefined ||
    patchData.tax !== undefined ||
    patchData.image_url !== undefined

  if (!hasAnyEditableValue) {
    return { error: 'Please provide at least one field to update.' }
  }

  const { error } = await updateItem(itemId, patchData, authResult.accessToken)

  if (error) {
    return {
      error: `Failed to update item: ${error}.`
    }
  }

  updateTag('items')
  updateTag(`item-${itemId}`)

  return { success: 'Item updated successfully.' }
}

export const deleteOwnedItemAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const itemId = formData.get('itemId')
  if (typeof itemId !== 'string' || itemId.length === 0) {
    return { error: 'Item ID is required.' }
  }

  const authResult = await getAuthenticatedUser()
  if (!authResult.success) {
    return { error: authResult.error }
  }

  const itemAuthResult = await checkItemAuthorization(
    itemId,
    authResult.me.id,
    authResult.me.is_superuser,
    authResult.accessToken
  )
  if (!itemAuthResult.success) {
    return { error: itemAuthResult.error }
  }

  const { error } = await deleteItem(itemId, authResult.accessToken)
  if (error) {
    return {
      error: `Failed to delete item: ${error}.`
    }
  }

  updateTag('items')
  updateTag(`item-${itemId}`)

  return { success: 'Item deleted successfully.' }
}

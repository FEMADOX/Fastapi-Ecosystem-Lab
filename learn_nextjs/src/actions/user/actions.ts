'use server'

import { updateTag } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import {
  deleteCurrentUser,
  deleteItem,
  updateCurrentUser,
  updateItem,
  uploadItemImage
} from '@/app/api/server-endpoints'
import type { PatchItemRequest } from '@/app/api/types'
import type { MeActionState } from '@/app/me/types'
import { itemPatchFormSchema } from '@/schemas/items/forms'
import { checkItemAuthorization, getAuthenticatedUser } from './actions.helpers'
import { profileEmailSchema, profilePasswordSchema } from './schemas'

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
      new_email: parseResult.data.email,
      current_password: parseResult.data.currentPassword
    },
    authResult.me?.id
  )

  if (error || !updatedUser) {
    return {
      error: `Failed to update profile email: ${error ?? 'Unknown error'}.`
    }
  }

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
    },
    authResult.me?.id
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

  const { error } = await deleteCurrentUser(
    authResult.accessToken,
    authResult.me?.id
  )

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

  const patchData: PatchItemRequest = {
    user_id: itemAuthResult.item.user_id,
    name: parseResult.data.name,
    description: parseResult.data.description,
    price: parseResult.data.price,
    tax: parseResult.data.tax
  }

  const hasAnyEditableValue =
    patchData.name !== undefined ||
    patchData.description !== undefined ||
    patchData.price !== undefined ||
    patchData.tax !== undefined

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
  updateTag(`owner-items-${authResult.me.id}`)

  return { success: 'Item updated successfully.' }
}

export const updateOwnedItemImageAction = async (
  _prevState: MeActionState,
  formData: FormData
): Promise<MeActionState> => {
  const itemId = formData.get('itemId')
  if (typeof itemId !== 'string' || itemId.length === 0) {
    return { error: 'Item ID is required.' }
  }

  const imageFile = formData.get('image_file')
  if (!(imageFile instanceof File) || imageFile.size === 0) {
    return { error: 'Image file is required.' }
  }

  if (!imageFile.type.startsWith('image/')) {
    return { error: 'Selected file must be an image.' }
  }

  const maxImageSize = 5 * 1024 * 1024
  if (imageFile.size > maxImageSize) {
    return { error: 'Image file must be 5 MB or smaller.' }
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

  const imageFormData = new FormData()
  imageFormData.set('image_file', imageFile)
  imageFormData.set('caption', itemAuthResult.item.description)

  const { data: updatedItem, error } = await uploadItemImage(
    itemId,
    imageFormData,
    authResult.accessToken
  )

  if (error || !updatedItem) {
    return {
      error: `Failed to update item image: ${error ?? 'Unknown error'}.`
    }
  }

  updateTag('items')
  updateTag(`item-${itemId}`)
  updateTag(`owner-items-${authResult.me.id}`)

  return { success: 'Item image updated successfully.' }
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
  updateTag(`owner-items-${authResult.me.id}`)

  return { success: 'Item deleted successfully.' }
}

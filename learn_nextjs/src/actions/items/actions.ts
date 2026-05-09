'use server'

import { revalidateTag, updateTag } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { z } from 'zod'

import { createItem, getMe, updateItem } from '@/app/api/server-endpoints'
import type { CreateItemRequest, PatchItemRequest } from '@/app/api/types'
import {
  ItemPatchSchema,
  ItemSchema,
  UserSchema
} from '@/common/schemas/api/resources'
import {
  itemCreateFormSchema,
  itemPatchFormSchema
} from '@/schemas/items/forms'
import type { ItemActionState } from '@/types/items/types'
import type { ItemBaseResult, itemFormSchemas } from '../types'

const itemBaseAction = async <T extends itemFormSchemas>(
  formData: FormData,
  itemSchema: T
): Promise<ItemBaseResult<T>> => {
  const accessToken = (await cookies()).get('access_token')?.value
  if (!accessToken) {
    return { success: false, error: 'Authentication required. Please log in.' }
  }

  const { data: meData, error: meError } = await getMe(accessToken)
  if (meError || !meData) {
    return {
      success: false,
      error: `Failed to verify authentication: ${meError ?? 'Unknown error'}.`
    }
  }

  const userResult = UserSchema.safeParse(meData)
  if (!userResult.success) {
    return { success: false, error: 'Failed to verify user identity.' }
  }

  const userId = userResult.data.id
  const rawFormData = Object.fromEntries(formData.entries())
  const parseResult = itemSchema.safeParse(rawFormData)
  if (!parseResult.success) {
    const flatErrors = z.flattenError(parseResult.error).fieldErrors
    const firstError = Object.values(flatErrors).flat()[0]
    return { success: false, error: firstError ?? 'Invalid form data.' }
  }

  if (itemSchema === itemCreateFormSchema) {
    return {
      success: true,
      userId,
      itemData: {
        user_id: userId,
        ...parseResult.data
      } as CreateItemRequest,
      accessToken
    } as ItemBaseResult<T>
  }

  return {
    success: true,
    userId,
    itemData: {
      user_id: userId,
      ...parseResult.data
    } as PatchItemRequest,
    accessToken
  } as ItemBaseResult<T>
}

export const createItemAction = async (
  _prevState: ItemActionState,
  formData: FormData
): Promise<ItemActionState> => {
  const baseResult = await itemBaseAction(formData, itemCreateFormSchema)

  if (!baseResult.success) {
    return { error: baseResult.error ?? 'Failed to process item data.' }
  }

  const { data: newItem, error: createError } = await createItem(
    baseResult.itemData,
    baseResult.accessToken
  )
  if (createError || !newItem) {
    return {
      error: `Failed to create item: ${createError ?? 'Unknown error'}.`
    }
  }

  const { success, error } = ItemSchema.safeParse(newItem)
  revalidateTag('items', 'max')

  if (!success) {
    return {
      error: `Item created but failed to parse item data: ${
        JSON.stringify(error?.message) ?? 'Unknown error'
      }.`
    }
  }

  redirect(`/items/${newItem.id}`)
}

export const updateItemAction = async (
  _prevState: ItemActionState,
  formData: FormData,
  itemId: string
): Promise<ItemActionState> => {
  const baseResult = await itemBaseAction(formData, itemPatchFormSchema)

  if (!baseResult.success) {
    return { error: baseResult.error ?? 'Failed to process item data.' }
  }

  const { data: updatedItem, error: updateError } = await updateItem(
    itemId,
    baseResult.itemData,
    baseResult.accessToken
  )

  if (updateError || !updatedItem) {
    return {
      error: `Failed to update item: ${updateError ?? 'Unknown error'}.`
    }
  }

  const { success, error } = ItemPatchSchema.safeParse(updatedItem)
  updateTag('items')
  updateTag(`item-${itemId}`)

  if (!success) {
    return {
      error: `Item updated but failed to parse updated item data: ${
        JSON.stringify(error?.message) ?? 'Unknown error'
      }.`
    }
  }

  redirect(`/items/${itemId}`)
}

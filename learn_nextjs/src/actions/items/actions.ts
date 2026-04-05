'use server'

import { ItemSchema, UserSchema } from '@/common/schemas/api/resources'
import { serverGet, serverPost } from '@/app/api/server-fetch'
import { Item, User } from '@/common/types/api/resources'
import { revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'
import { z } from 'zod'
import { ItemActionState } from '@/types/items/types'
import { itemFormSchema } from '@/schemas/items/forms'

export const createItemAction = async (
  _prevState: ItemActionState,
  formData: FormData
): Promise<ItemActionState> => {
  const { data: meData, error: meError } = await serverGet<User>('/latest/users/me')
  if (meError || !meData) {
    return { error: 'Authentication required. Please log in again.' }
  }

  const userResult = UserSchema.safeParse(meData)
  if (!userResult.success) {
    return { error: 'Failed to verify user identity.' }
  }

  const userId = userResult.data.id
  const rawFormData = Object.fromEntries(formData.entries())
  const parseResult = itemFormSchema.safeParse(rawFormData)

  if (!parseResult.success) {
    const flatErrors = z.flattenError(parseResult.error).fieldErrors
    const firstError = Object.values(flatErrors).flat()[0]
    return { error: firstError ?? 'Invalid form data.' }
  }

  const { name, description, price, tax, image_url: imageUrl } = parseResult.data

  const { data: newItem, error } = await serverPost<Item>('/latest/items', {
    user_id: userId,
    name,
    description,
    price,
    tax,
    image_url: imageUrl ?? undefined
  })

  if (error || !newItem) {
    return { error: error ?? 'Failed to create item. Please try again.' }
  }

  const itemResult = ItemSchema.safeParse(newItem)
  revalidateTag('items', 'max')

  if (itemResult.success) {
    redirect(`/items/${itemResult.data.id}`)
  }

  console.error(`Unexpectedly created item but failed to parse it: ${JSON.stringify(itemResult.error.message)}`)
  redirect('/items')
}

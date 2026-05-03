'use server'

import { revalidateTag } from 'next/cache'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { z } from 'zod'

import { createItem, getMe } from '@/app/api/server-endpoints'
import { ItemSchema, UserSchema } from '@/common/schemas/api/resources'
import { itemFormSchema } from '@/schemas/items/forms'
import type { ItemActionState } from '@/types/items/types'

export const createItemAction = async (
  _prevState: ItemActionState,
  formData: FormData
): Promise<ItemActionState> => {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get('access_token')?.value
  if (!accessToken) {
    return { error: 'Authentication required. Please log in.' }
  }

  const { data: meData, error: meError } = await getMe(accessToken)
  if (meError || !meData) {
    return {
      error: `Failed to verify authentication: ${meError ?? 'Unknown error'}.`
    }
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

  const itemData = { user_id: userId, ...parseResult.data }

  const { data: newItem, error } = await createItem(itemData, accessToken)
  if (error || !newItem) {
    return {
      error: `Failed to create item: ${error ?? 'Unknown error'}.`
    }
  }

  const itemResult = ItemSchema.safeParse(newItem)
  revalidateTag('items', 'max')

  if (itemResult.success) {
    redirect(`/items/${itemResult.data.id}`)
  }

  console.error(
    `Unexpectedly created item but failed to parse it: ${JSON.stringify(itemResult.error.message)}`
  )
  redirect('/items')
}

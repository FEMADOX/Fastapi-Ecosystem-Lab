'use server'

import { updateTag } from 'next/cache'

export const revalidateItemsAction = async (tagToUpdate: string) => {
  updateTag(tagToUpdate)
}

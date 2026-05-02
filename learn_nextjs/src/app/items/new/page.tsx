import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { serverGet } from '@/app/api/server-fetch'
import { UserSchema } from '@/common/schemas/api/resources'
import type { User } from '@/common/types/api/resources'

import { NewItemForm } from './NewItemForm'

const ItemNewPage = async () => {
  const cookieStore = await cookies()
  if (!cookieStore.has('access_token')) {
    redirect('/login?next=/items/new')
  }

  const accessToken = cookieStore.get('access_token')?.value
  const { data: meData, error } = await serverGet<User>(
    '/latest/users/me',
    accessToken
  )
  if (error || !meData) {
    redirect('/login?next=/items/new')
  }

  const { success, data: parsedData } = UserSchema.safeParse(meData)
  if (!success) {
    redirect('/login?next=/items/new')
  }

  return (
    <>
      <h1 className="mb-8 text-3xl font-bold">New Item</h1>
      <NewItemForm userId={parsedData.id} />
    </>
  )
}

export default ItemNewPage

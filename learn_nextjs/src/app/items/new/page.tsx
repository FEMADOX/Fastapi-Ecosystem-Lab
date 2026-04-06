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

  const { data: meData, error } = await serverGet<User>('/latest/users/me')
  if (error || !meData) {
    redirect('/login?next=/items/new')
  }

  const userResult = UserSchema.safeParse(meData)
  if (!userResult.success) {
    redirect('/login?next=/items/new')
  }

  return (
    <>
      <h1 className="mb-8 text-3xl font-bold">New Item</h1>
      <NewItemForm userId={userResult.data.id} />
    </>
  )
}

export default ItemNewPage

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { UserSchema } from '@/common/schemas/api/resources'

import { getMe } from '../../api/server-endpoints'
import { NewItemForm } from './NewItemForm'

const ItemNewPage = async () => {
  const cookieStore = await cookies()
  if (!cookieStore.has('access_token')) {
    redirect('/login?next=/items/new')
  }

  const accessToken = cookieStore.get('access_token')?.value
  if (!accessToken) {
    redirect('/login?next=/items/new')
  }

  const { data: meData, error } = await getMe(accessToken)
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

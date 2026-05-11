import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { getMe, getOwnerItems } from '@/app/api/server-endpoints'
import { RetryCard } from '@/app/items/RetryCard'
import { MePageClient } from './MePageClient'

const MePage = async () => {
  const accessToken = (await cookies()).get('access_token')?.value
  const redirectPath = '/login?next=%2Fme'

  if (!accessToken) {
    redirect(redirectPath)
  }

  const { data: me, error: meError } = await getMe(accessToken)
  if (meError || !me) {
    redirect(redirectPath)
  }

  const { data: ownedItems, error: itemsError } = await getOwnerItems(
    me.id,
    accessToken
  )

  if (itemsError || !ownedItems) {
    return (
      <RetryCard
        cardTitle="My Account"
        error={itemsError ?? 'Failed to load your items. Please try again.'}
        tagToUpdate="items"
      />
    )
  }

  return <MePageClient user={me} ownedItems={ownedItems} />
}

export default MePage

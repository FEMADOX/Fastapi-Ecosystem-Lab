import { cacheTag } from 'next/cache'
import { cookies } from 'next/headers'

import { serverGet } from '@/app/api/server-fetch'
import type { Item } from '@/common/types/api/resources'
import type { PromiseIdProp } from '@/common/types/routing'

const fetchItem = async (id: string, accessToken?: string) => {
  'use cache'
  cacheTag(`item-${id}`)
  return serverGet<Item>(`/latest/items/${id}`, accessToken)
}

const ItemPage = async ({ params }: PromiseIdProp) => {
  const [{ id }, cookieStore] = await Promise.all([params, cookies()])
  const accessToken = cookieStore.get('access_token')?.value
  const { data: item, error } = await fetchItem(id, accessToken)

  if (error) {
    throw new Error(`Failed to fetch item: ${error}`)
  }

  return (
    <div>
      {item && (
        <>
          <h1 className="mb-8 text-3xl font-bold">Item: {item.name}</h1>
          <p className="mb-5 text-xl font-bold">
            ID: <span className="font-normal">{item.id}</span>
          </p>
          <p className="mb-5 text-xl font-bold">
            Name: <span className="font-normal">{item.name}</span>
          </p>
          <p className="mb-5 text-xl font-bold">
            Description: <span className="font-normal">{item.description}</span>
          </p>
          <p className="mb-5 text-xl font-bold">
            Price: <span className="font-normal">{item.price}</span>
          </p>
          <p className="mb-5 text-xl font-bold">
            Tax: <span className="font-normal">{item.tax}</span>
          </p>
        </>
      )}
    </div>
  )
}

export default ItemPage

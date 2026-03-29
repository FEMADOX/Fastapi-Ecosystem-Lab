import { getItem } from '@/app/api/endpoints'
import { PromiseIdProp, IdProp } from '@/common/types'
import { Suspense } from 'react'

// Layer 3: stable id in, data out — cacheable
const ItemDetail = async ({ id }: IdProp) => {
  'use cache'
  const item = await getItem(id)

  return (
    <>
      <h1 className="text-3xl mb-8 font-bold">Item: {item.name}</h1>
      <p className="text-xl mb-5 font-bold">
        ID: <span className="font-normal">{item.id}</span>
      </p>
      <p className="text-xl mb-5 font-bold">
        Name: <span className="font-normal">{item.name}</span>
      </p>
      <p className="text-xl mb-5 font-bold">
        Description: <span className="font-normal">{item.description}</span>
      </p>
      <p className="text-xl mb-5 font-bold">
        Price: <span className="font-normal">{item.price}</span>
      </p>
      <p className="text-xl mb-5 font-bold">
        Tax: <span className="font-normal">{item.tax}</span>
      </p>
    </>
  )
}

// Layer 2: awaits params inside Suspense, passes plain id down
const ItemResolver = async ({ params }: PromiseIdProp) => {
  const { id } = await params
  return <ItemDetail id={id} />
}

// Layer 1: non-async page — Suspense wraps the params access
const ItemPage = ({ params }: PromiseIdProp) => (
  <Suspense fallback={<p>Loading item...</p>}>
    <ItemResolver params={params} />
  </Suspense>
)

export default ItemPage

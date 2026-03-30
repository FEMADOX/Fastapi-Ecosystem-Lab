import { getItem } from '@/app/api/endpoints'
import { PromiseIdProp } from '@/common/types'

const ItemPage = async ({ params }: PromiseIdProp) => {
  'use cache'
  const { id } = await params
  const { data: item, error } = await getItem(id)

  if (error) {
    throw new Error(`Failed to fetch item: ${error}`)
  }

  return (
    <div>
      {item && (
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
      )}
    </div>
  )
}

export default ItemPage

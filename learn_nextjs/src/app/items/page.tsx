import { getItems } from '@/app/api/endpoints'
import Link from 'next/dist/client/link'

const ItemsPage = async () => {
  'use cache'
  const items = await getItems()

  return (
    <>
      <h1 className="text-3xl mb-8 font-bold">Items</h1>
      <p className="text-xl mb-5">List of all the items</p>
      <ul>
        {items.map((item) => (
          <Link
            className="block hover:text-blue-500 transition-colors mt-2"
            href={`/items/${item.id}`}
            key={item.id}
          >
            <strong>{item.name}</strong>: {item.description} - ${item.price} -
            Tax: ${item.tax}
          </Link>
        ))}
      </ul>
      <Link
        href="/items/new"
        className="inline-block mt-8 py-2 px-4 border border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white transition-colors rounded-md"
      >
        Add New Item
      </Link>
    </>
  )
}

export default ItemsPage

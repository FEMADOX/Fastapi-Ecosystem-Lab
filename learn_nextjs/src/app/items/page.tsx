import { cacheTag } from 'next/cache'
import Link from 'next/link'
import { getItems } from '../api/endpoints'
import { ItemsComponent } from './components/Items'
import { RetryCard } from './components/RetryCard'

const ItemsPage = async () => {
  'use cache'
  cacheTag('items')
  const { data: items, error } = await getItems()
  const badge = {
    text: 'Badge',
    color: 'red'
  }

  if (error)
    return <RetryCard cardTitle="Items" error={error} tagToUpdate="items" />

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold">Items</h1>
      <Link
        href="/items/new"
        className="border-primary text-primary hover:bg-primary mb-8 inline-block rounded-md border px-4 py-2 transition-colors hover:text-white"
      >
        Add New Item
      </Link>
      <ItemsComponent items={items ?? []} badge={badge} />
    </div>
  )
}

export default ItemsPage

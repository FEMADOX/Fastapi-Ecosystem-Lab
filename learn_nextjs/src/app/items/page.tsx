import { cacheTag } from 'next/cache'
import Image from 'next/image'
import Link from 'next/link'
import { NO_IMAGE_AVAILABLE_URL } from '@/common/const'
import { Price, PriceValue } from '@/components/price'
import { AspectRatio } from '@/components/ui/aspect-ratio'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { getItems } from '../api/endpoints'
import { RetryCard } from './RetryCard'

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
      <ul className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-6">
        {items?.map((item) => (
          <Link
            className="opacity-animation block h-full w-full max-w-md"
            href={`/items/${item.id}`}
            key={item.id}
          >
            <Card className="h-full overflow-hidden p-0 shadow-sm">
              <CardHeader className="relative block p-0">
                <AspectRatio ratio={1.268115942} className="overflow-hidden">
                  <Image
                    // TODO (FENYXZ): fetch real image URL for item, fallback to placeholder if not available
                    src={NO_IMAGE_AVAILABLE_URL}
                    alt={item.description}
                    className="block size-full object-cover object-center"
                    width={500}
                    height={500}
                    loading="eager"
                  />
                </AspectRatio>
                {badge && (
                  <Badge
                    style={{
                      backgroundColor: badge.color
                    }}
                    className="absolute inset-s-4 top-4"
                  >
                    {badge.text}
                  </Badge>
                )}
              </CardHeader>

              <CardContent className="flex h-full flex-col gap-4 pb-6">
                <CardTitle className="text-xl font-semibold">
                  {item.name}
                </CardTitle>
                <CardDescription className="text-muted-foreground font-medium">
                  {item.description}
                </CardDescription>
                <div className="mt-auto">
                  <Price
                    onSale={item.price != null}
                    className="text-lg font-semibold"
                  >
                    <PriceValue
                      price={item.price ? item.price / 1.05 : 0}
                      currency="USD"
                      variant="sale"
                    />
                    <PriceValue
                      price={item.price}
                      currency="USD"
                      variant="regular"
                    />
                  </Price>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </ul>
    </div>
  )
}

export default ItemsPage

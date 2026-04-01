import { getItems } from '@/app/api/endpoints'
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
import Link from 'next/dist/client/link'

const ItemsPage = async () => {
  'use cache'
  const { data: items, error } = await getItems()
  const badge = {
    text: 'Badge',
    color: 'red'
  }

  if (error) {
    throw new Error(`Failed to fetch items: ${error}`)
  }

  return (
    <>
      <h1 className="text-3xl mb-8 font-bold">Items</h1>
      <ul className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-6">
        {items &&
          items.map((item) => (
            <Link
              className="block h-full w-full max-w-md transition-opacity hover:opacity-65"
              href={`/items/${item.id}`}
              key={item.id}
            >
              <Card className="h-full overflow-hidden p-0">
                <CardHeader className="relative block p-0">
                  <AspectRatio ratio={1.268115942} className="overflow-hidden">
                    <img
                      // TODO (FENYXZ): fetch real image URL for item, fallback to placeholder if not available
                      src={NO_IMAGE_AVAILABLE_URL}
                      alt={item.description}
                      className="block size-full object-cover object-center"
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
                  <CardDescription className="font-medium text-muted-foreground">
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
      <Link
        href="/items/new"
        className="inline-block mt-8 py-2 px-4 border border-primary text-primary hover:bg-primary hover:text-white transition-colors rounded-md"
      >
        Add New Item
      </Link>
    </>
  )
}

export default ItemsPage

import Link from 'next/link'
import type { Items } from '@/common/types/api/resources'
import { Price, PriceValue } from '@/components/price'
import { ProductImage } from '@/components/product-image'
import {
  AspectRatio,
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui'

interface ItemsComponentProps {
  items: Items
  badge: { text: string; color: string }
}

export const ItemsComponent = ({ items, badge }: ItemsComponentProps) => (
  <ul className="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-6">
    {items?.map((item) => (
      <Link
        className="opacity-animation block h-full w-full max-w-md"
        href={`/items/${item.id}`}
        key={item.id}
      >
        <Card className="h-full overflow-hidden p-0 shadow-sm">
          <CardHeader className="relative block p-0">
            <AspectRatio ratio={1.268115942} className="overflow-hidden flex">
              <ProductImage
                src={item.image_url}
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
            <CardTitle className="text-xl font-semibold">{item.name}</CardTitle>
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
)

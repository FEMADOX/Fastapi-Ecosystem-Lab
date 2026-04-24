import { CreditCardIcon, ShoppingCartIcon, Star, StarHalf } from 'lucide-react'
import { cacheTag } from 'next/cache'
import { cookies } from 'next/headers'
import Image from 'next/image'
import { serverGet } from '@/app/api/server-fetch'
import { NO_IMAGE_AVAILABLE_URL } from '@/common/const'
import type { Item } from '@/common/types/api/resources'
import type { PromiseIdProp } from '@/common/types/routing'
import { Button } from '@/components/ui/button'
import { RetryCard } from '../RetryCard'

const fetchItem = async (id: string, accessToken?: string) => {
  'use cache'
  cacheTag(`item-${id}`)
  return serverGet<Item>(`/latest/items/${id}`, accessToken)
}

const ItemPage = async ({ params }: PromiseIdProp) => {
  const [{ id }, cookieStore] = await Promise.all([params, cookies()])
  const accessToken = cookieStore.get('access_token')?.value
  const { data: item, error } = await fetchItem(id, accessToken)

  if (error)
    return (
      <RetryCard cardTitle="Item Details" error={error} tagToUpdate={`item-${id}`} />
    )

  return (
    <div>
      <div>
        {item && (
          <>
            <div className="border border-border rounded-2xl overflow-hidden">
              <Image
                src={NO_IMAGE_AVAILABLE_URL}
                alt={item.description}
                className="block size-full object-cover object-center"
                width={500}
                height={500}
                loading="eager"
              />
            </div>
            <div className="flex my-4">
              <div className="flex *:size-5 *:border-[#c9a74d] items-center *:stroke-1">
                <Star fill="#c9a74d" color="#c9a74d" />
                <Star fill="#c9a74d" color="#c9a74d" />
                <Star fill="#c9a74d" color="#c9a74d" />
                <Star fill="#c9a74d" color="#c9a74d" />
                <Star className="relative" color="#c9a74d">
                  <StarHalf
                    fill="#c9a74d"
                    color="#c9a74d"
                    className="absolute"
                  />
                </Star>
              </div>
              <span className="ml-2">4.8</span>
              <span className="ml-1">(124 reviews)</span>
            </div>
            <h1 className="mb-6 text-3xl font-bold">{item.name}</h1>
            <p className="mb-5 text-2xl font-bold">
              {/* Round total price (item.price + item.tax) */}${' '}
              {Math.round((item.price + item.tax) * 100) / 100}{' '}
              <span className="text-sm font-normal text-muted-foreground">
                (Tax included: $ {Math.round(item.tax * 100) / 100})
              </span>
            </p>
            <p className="mb-5 text-xl font-bold">
              <span className="font-normal">{item.description}</span>
            </p>
          </>
        )}
      </div>
      <div className="mt-15">
        <div className="flex flex-col gap-4 *:py-2 *:h-12 *:items-center">
          <Button
            variant="default"
            className="w-full text-md font-bold"
            disabled
          >
            <ShoppingCartIcon strokeWidth={4} />
            Add to Cart
          </Button>
          <Button
            variant="outline"
            className="w-full text-md font-thin border-primary text-primary hover:text-primary"
            disabled
          >
            <CreditCardIcon width={10} height={10} />
            Buy Now
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ItemPage

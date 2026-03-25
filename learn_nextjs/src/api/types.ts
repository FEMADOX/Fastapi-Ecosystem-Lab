export type Image = {
  name: string
  description: string
  contentType: string | null
  url: string
}

export type Item = {
  id: string
  userId: string
  name: string
  description: string
  price: number
  tax: number
  imageUrl: string | null
}

export type Items = Item[]

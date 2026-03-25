import type { ReactNode } from 'react'

export type Children = Readonly<{
  children: ReactNode
}>

export type PromiseIdProp = {
  params: Promise<{
    id: string
  }>
}

export type IdProp = {
  id: string
}

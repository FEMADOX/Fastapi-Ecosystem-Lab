import { Item } from './interfaces'

export type Items = Item[]

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export type LoginResponse = { loggedIn: boolean }

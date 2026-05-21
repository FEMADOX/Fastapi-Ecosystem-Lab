import type { SSEEventMap } from '@/app/api/sse/[channel]/types'

export const globalEventMap: SSEEventMap = {
  'item.created': {
    toastType: 'success',
    toastMessage: (event) => `New item created: ${event.payload.name}`
  }
}

export const userEventMap: SSEEventMap = {
  'item.created': {
    toastType: 'success',
    toastMessage: (event) => `You created a new item: ${event.payload.name}`
  },
  'item.updated': {
    toastType: 'info',
    toastMessage: (event) => `Your item was updated: ${event.payload.name}`
  },
  'item.deleted': {
    toastType: 'error',
    toastMessage: (event) => `Your item was deleted: ${event.payload.name}`
  },
  'item.image_updated': {
    toastType: 'info',
    toastMessage: (event) =>
      `Your item's image was updated: ${event.payload.name}`
  },
  'auth.registered': {
    toastType: 'success',
    toastMessage: () => `Welcome! Account created successfully.`
  },
  'auth.logged_in': {
    toastType: 'success',
    toastMessage: () => `Welcome back! You are now logged in.`
  },
  'auth.logged_out': {
    toastType: 'info',
    toastMessage: () => `You have been logged out.`
  },
  'user.account_updated': {
    toastType: 'info',
    toastMessage: (event) => {
      const fields = event.payload.changed_fields as string[] | undefined
      const fieldMessages = fields?.join(', ') || ''
      return `Your account was updated. Changed: ${fieldMessages}`
    }
  },
  'user.account_deleted': {
    toastType: 'warning',
    toastMessage: () => `Your account has been deleted.`
  }
}

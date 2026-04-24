'use client'

import { Button } from '@base-ui/react'
import { useRouter } from 'next/navigation'
import { revalidateItemsAction } from './actions'

interface RetryButtonProps {
  tagToUpdate: string
}

export const RetryButton = ({ tagToUpdate }: RetryButtonProps) => {
  const router = useRouter()

  const handleRetry = async () => {
    await revalidateItemsAction(tagToUpdate)
    router.refresh()
  }

  return (
    <Button
      onClick={handleRetry}
      className={`
        inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-opacity
        hover:opacity-80 hover:cursor-pointer
      `}
    >
      Retry now
    </Button>
  )
}

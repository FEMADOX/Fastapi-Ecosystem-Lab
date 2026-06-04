'use client'

import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { logoutAction } from '@/actions/auth/actions'
import { Button, ButtonGroup } from '@/components/ui'
import type { FormSubmitEvent } from '../items/new/types'

interface LogoutButtonProps {
  isLoggedIn: boolean
}

export const LogoutGroup = ({ isLoggedIn }: LogoutButtonProps) => {
  const router = useRouter()

  const handleSubmit = async (event: FormSubmitEvent) => {
    event.preventDefault()

    const { success } = await logoutAction()
    if (!success) {
      toast.error('Error while logout')
      return
    }

    router.refresh()
    toast.info('You have been logged out.')
  }

  return (
    <form onSubmit={handleSubmit}>
      <ButtonGroup className="px-1" hidden={!isLoggedIn}>
        <Button
          className="text-md cursor-pointer py-3.5 font-semibold transition-opacity hover:opacity-80"
          variant="default"
          type="submit"
          size="sm"
        >
          Logout
        </Button>
      </ButtonGroup>
    </form>
  )
}

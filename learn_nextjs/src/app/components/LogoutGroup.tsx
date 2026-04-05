'use client'

import { logoutAction } from '@/actions/auth/actions'
import { Button } from '@/components/ui/button'
import { ButtonGroup } from '@/components/ui/button-group'

interface LogoutButtonProps {
  isLoggedIn: boolean
}

export const LogoutGroup = ({ isLoggedIn }: LogoutButtonProps) => {
  return (
    <form action={logoutAction}>
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

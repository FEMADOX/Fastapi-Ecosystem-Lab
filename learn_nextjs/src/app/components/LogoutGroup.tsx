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
          className="text-md font-semibold cursor-pointer py-3.5 hover:opacity-80 transition-opacity"
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

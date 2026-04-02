'use client'

import { logout } from '@/app/api/endpoints'
import { Button } from '@/components/ui/button'
import { ButtonGroup } from '@/components/ui/button-group'
import { useRouter } from 'next/navigation'

interface LogoutButtonProps {
  isLoggedIn: boolean
}

export const LogoutGroup = ({ isLoggedIn }: LogoutButtonProps) => {
  const router = useRouter()

  const clickLogout = async () => {
    const { data, error } = await logout()

    if (error || data?.loggedOut !== true) {
      console.error(`Logout failed: ${error ?? 'Unknown error'}`)
      return
    }

    router.push('/login')
    router.refresh()
  }
  const handleLogout = () => {
    clickLogout().catch((error) => {
      console.error(`Logout failed: ${error ?? 'Unknown error'}`)
    })
  }

  return (
    <ButtonGroup
      hidden={!isLoggedIn}
      role="form"
      onClick={handleLogout}
    >
      <Button
        className="text-md font-semibold cursor-pointer py-3.5 hover:opacity-80 transition-opacity"
        variant="default"
        type="submit"
        size="sm"
      >
        Logout
      </Button>
    </ButtonGroup>
  )
}

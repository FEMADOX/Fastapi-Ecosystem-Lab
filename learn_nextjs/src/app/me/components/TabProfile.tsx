import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { DeleteAccountComponent } from './DeleteAccount'
import type { TabProfileProps } from './types'
import { UpdateAccountComponent } from './UpdateAccount'

export const TabProfileComponent = ({ user, isActive }: TabProfileProps) => {
  if (!isActive) return null

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Account Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm">
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          <p>
            <strong>Role:</strong> {user.is_superuser ? 'Superuser' : 'User'}
          </p>
          <p>
            <strong>Status:</strong> {user.is_active ? 'Active' : 'Inactive'}
          </p>
        </CardContent>
      </Card>

      <UpdateAccountComponent userEmail={user.email} />

      <DeleteAccountComponent />
    </div>
  )
}

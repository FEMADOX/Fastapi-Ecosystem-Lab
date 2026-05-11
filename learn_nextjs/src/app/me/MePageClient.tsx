'use client'

import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { TabItemsComponent, TabProfileComponent } from './components'
import type { MePageClientProps } from './types'

export const MePageClient = ({ user, ownedItems }: MePageClientProps) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'items'>('profile')

  return (
    <section className="mx-auto w-full max-w-4xl space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">My Account</h1>
        <p className="text-muted-foreground">
          Manage your profile settings and only your own items.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={activeTab === 'profile' ? 'default' : 'outline'}
          onClick={() => setActiveTab('profile')}
          className="cursor-pointer"
        >
          Profile
        </Button>
        <Button
          type="button"
          variant={activeTab === 'items' ? 'default' : 'outline'}
          onClick={() => setActiveTab('items')}
          className="cursor-pointer"
        >
          My Items ({ownedItems.length})
        </Button>
      </div>

      <TabProfileComponent user={user} isActive={activeTab === 'profile'} />

      <TabItemsComponent
        ownedItems={ownedItems}
        isActive={activeTab === 'items'}
      />
    </section>
  )
}

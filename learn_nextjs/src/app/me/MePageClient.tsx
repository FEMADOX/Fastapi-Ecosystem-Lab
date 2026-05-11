'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { TabItemsComponent, TabProfileComponent } from './components'
import type { MePageClientProps } from './types'

type TabKey = 'items' | null

export const MePageClient = ({ user, ownedItems }: MePageClientProps) => {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const tabParam = searchParams.get('tab')
  const activeTab: TabKey = tabParam === 'items' ? 'items' : null

  const setTab = (tab: TabKey) => {
    const params = new URLSearchParams(searchParams.toString())
    if (tab === null) {
      return router.replace(pathname)
    }
    params.set('tab', tab)
    router.replace(`${pathname}?${params.toString()}`, { scroll: false })
  }

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
          variant={activeTab === null ? 'default' : 'outline'}
          onClick={() => setTab(null)}
          className="cursor-pointer"
        >
          Profile
        </Button>
        <Button
          type="button"
          variant={activeTab === 'items' ? 'default' : 'outline'}
          onClick={() => setTab('items')}
          className="cursor-pointer"
        >
          My Items ({ownedItems.length})
        </Button>
      </div>

      <TabProfileComponent user={user} isActive={activeTab === null} />

      <TabItemsComponent
        ownedItems={ownedItems}
        isActive={activeTab === 'items'}
      />
    </section>
  )
}

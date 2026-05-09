'use client'

import { MenuIcon } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/app/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { ButtonGroup } from '@/components/ui/button-group'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from '@/components/ui/sheet'
import { LogoutGroup } from './LogoutGroup'

export const NavBar = () => {
  const { state } = useAuth()
  const isLoggedIn = state.status === 'authenticated'

  return (
    <nav className="border-b bg-white px-1 md:px-4">
      <div className="flex items-center py-3 *:text-black">
        <div className="mr-2 md:hidden">
          <Sheet>
            <SheetTrigger
              render={
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Open navigation menu"
                />
              }
            >
              <MenuIcon />
            </SheetTrigger>

            <SheetContent side="left">
              <SheetHeader>
                <SheetTitle>Menu</SheetTitle>
                <SheetDescription>
                  Navigate the app pages and auth routes.
                </SheetDescription>
              </SheetHeader>
              <div className="flex flex-col gap-5 px-4 pb-6">
                <SheetClose
                  render={
                    <Link className="text-lg font-semibold" href="/">
                      Home
                    </Link>
                  }
                  nativeButton={false}
                />
                <SheetClose
                  render={
                    <Link className="text-lg font-semibold" href="/items">
                      Items
                    </Link>
                  }
                  nativeButton={false}
                />
                {isLoggedIn && (
                  <SheetClose
                    render={
                      <Link className="text-lg font-semibold" href="/me">
                        My Account
                      </Link>
                    }
                    nativeButton={false}
                  />
                )}
                <SheetClose
                  render={
                    <Link className="text-lg font-semibold" href="/about">
                      About
                    </Link>
                  }
                  nativeButton={false}
                />
              </div>
            </SheetContent>
          </Sheet>
        </div>

        <Link
          className="text-md opacity-animation inline-block font-bold sm:text-lg"
          href="/"
        >
          FastAPI Ecosystem Lab
        </Link>

        <div className="m-auto hidden items-center justify-between gap-10 md:flex">
          <ul className="flex items-center gap-5 [&>li]:inline-block [&>li]:transition-colors [&>li:hover]:text-gray-800">
            <li>
              <Link className="text-lg font-semibold" href="/items">
                Items
              </Link>
            </li>
            {isLoggedIn && (
              <li>
                <Link className="text-lg font-semibold" href="/me">
                  My Account
                </Link>
              </li>
            )}
            <li>
              <Link className="text-lg font-semibold" href="/about">
                About
              </Link>
            </li>
          </ul>
        </div>
        <ButtonGroup className="ml-auto md:ml-0">
          <LogoutGroup isLoggedIn={isLoggedIn} />
          <ButtonGroup
            className="ml-auto flex items-center gap-2 px-1 md:ml-0"
            hidden={isLoggedIn}
          >
            <Link
              className="text-md opacity-animation font-semibold"
              href="/login"
            >
              Login
            </Link>
            <Link
              className="text-md bg-primary opacity-animation rounded-lg px-2 py-0.5 font-semibold text-white"
              href="/signup"
            >
              Signup
            </Link>
          </ButtonGroup>
        </ButtonGroup>
      </div>
    </nav>
  )
}

import Link from 'next/link'
import { MenuIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from '@/components/ui/sheet'

export const NavBar = () => (
  <nav className="bg-white px-1 md:px-4 border-b">
    <div className="flex items-center py-3 *:text-black">
      <div className="md:hidden mr-2">
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
              <Link className="text-lg font-semibold" href="/items">
                Items
              </Link>
              <Link className="text-lg font-semibold" href="/about">
                About
              </Link>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <Link className="inline-block text-md sm:text-lg font-bold" href="/">
        FastAPI Ecosystem Lab
      </Link>

      <div className="hidden md:flex items-center justify-between gap-10 m-auto">
        <ul className="flex items-center gap-5 [&>li:hover]:text-gray-800 [&>li]:transition-colors [&>li]:inline-block">
          <li>
            <Link className="text-lg font-semibold" href="/items">
              Items
            </Link>
          </li>
          <li>
            <Link className="text-lg font-semibold" href="/about">
              About
            </Link>
          </li>
        </ul>
      </div>
      <div className="flex gap-2 px-1 items-center ml-auto md:ml-0">
        <Link className="text-md font-semibold" href="/auth/login">
          Login
        </Link>
        <Link
          className="text-md text-white font-semibold bg-primary rounded-lg px-2 py-0.5"
          href="/auth/signup"
        >
          Signup
        </Link>
      </div>
    </div>
  </nav>
)

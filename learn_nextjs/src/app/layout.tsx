import type { Metadata } from 'next'
import { Suspense } from 'react'

import './globals.css'
import { Children } from '@/common/types'
import CurrentYear from '@/app/components/current-year'
import { NavBar } from './components/NavBar'

export const metadata: Metadata = {
  title: 'FastAPI Ecosystem Lab',
  description:
    'Pedagogical project showcasing FastAPI and its ecosystem through a practical example with a Next.js frontend.'
}

const RootLayout = ({ children }: Children) => (
  <html lang="en">
    <body className="container m-auto grid min-h-screen min-w-full grid-rows-[auto_1fr_auto]">
      <NavBar />
      <main className="py-8 px-8">{children}</main>
      <footer className="text-center leading-12 opacity-70">
        ©{' '}
        <Suspense fallback="2026">
          <CurrentYear />
        </Suspense>{' '}
        FastAPI Ecosystem Lab
      </footer>
    </body>
  </html>
)

export default RootLayout

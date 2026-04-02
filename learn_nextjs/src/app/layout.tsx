import type { Metadata } from 'next'
import { Suspense } from 'react'

import CurrentYear from '@/app/components/current-year'
import { Children } from '@/common/types'
import { cn } from '@/lib/utils'
import { Geist } from 'next/font/google'
import { AuthProvider } from './auth-provider'
import { NavBar } from './components/NavBar'
import './globals.css'

const geist = Geist({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = {
  title: 'FastAPI Ecosystem Lab',
  description:
    'Pedagogical project showcasing FastAPI and its ecosystem through a practical example with a Next.js frontend.'
}

const RootLayout = ({ children }: Children) => (
  <html lang="en" className={cn('font-sans', geist.variable)}>
    <body className="container m-auto grid min-h-screen min-w-full grid-rows-[auto_1fr_auto]">
      <Suspense fallback={<nav className="bg-white px-1 md:px-4 border-b" />}>
        <NavBar />
      </Suspense>
      <AuthProvider>
        <main className="py-8 px-8">{children}</main>
      </AuthProvider>
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

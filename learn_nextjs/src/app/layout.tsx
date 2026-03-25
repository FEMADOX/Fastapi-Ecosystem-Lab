import type { Metadata } from 'next'
import type { ReactNode } from 'react'

import './globals.css'

export const metadata: Metadata = {
  title: 'FastAPI Ecosystem Lab'
}

export default function RootLayout ({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="container m-auto grid min-h-screen grid-rows-[auto_1fr_auto] px-4">
        <header className="text-xl leading-[3rem] font-bold">FastAPI Ecosystem Lab</header>
        <main className="py-8">{children}</main>
        <footer className="text-center leading-[3rem] opacity-70">
          © {new Date().getFullYear()} FastAPI Ecosystem Lab
        </footer>
      </body>
    </html>
  )
}

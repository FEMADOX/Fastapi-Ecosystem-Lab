import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About - FastAPI Ecosystem Lab',
  description:
    'Learn what FastAPI Ecosystem Lab demonstrates across FastAPI, Next.js, Streamlit, authentication, caching, and item workflows.'
}

const Layout = ({ children }: { children: React.ReactNode }) => (
  <main className="mx-auto flex w-full max-w-6xl flex-col gap-20">
    {children}
  </main>
)

export default Layout

import { ArrowRight, DatabaseZap, ShieldCheck, Sparkles } from 'lucide-react'
import Link from 'next/link'

const featureCards = [
  {
    title: 'API-First Learning',
    description:
      'Explore a complete FastAPI workflow with practical examples and a typed Next.js frontend.',
    icon: DatabaseZap
  },
  {
    title: 'Auth and Security',
    description:
      'Test login, signup, protected routes, and safe redirects with realistic session flows.',
    icon: ShieldCheck
  },
  {
    title: 'Modern UI Patterns',
    description:
      'Reusable components, loading states, and forms designed for maintainability and speed.',
    icon: Sparkles
  }
]

const HomePage = () => {
  return (
    <section className="relative isolate overflow-hidden rounded-2xl border border-border bg-card p-5 sm:rounded-3xl sm:p-8 lg:p-12 shadow-sm">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-16 right-0 size-48 rounded-full bg-primary/10 blur-3xl sm:size-64"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-16 -left-8 size-48 rounded-full bg-primary/10 blur-3xl sm:size-64"
      />

      <div className="relative flex flex-col gap-8 sm:gap-10">
        <div className="space-y-5">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold tracking-wide text-primary uppercase">
            <span className="text-sm leading-none">+</span>
            FastAPI + Next.js Learning Lab
          </span>

          <div className="space-y-3">
            <h1 className="text-3xl leading-tight font-bold text-foreground sm:text-4xl lg:text-5xl">
              Build and understand a production-style full stack in one place.
            </h1>
            <p className="text-sm leading-relaxed text-muted-foreground sm:text-base lg:text-lg">
              This project demonstrates how a FastAPI backend and a Next.js
              frontend can work together with clean APIs, authentication,
              validation, and a practical item workflow.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/items"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80"
            >
              Explore Items
              <ArrowRight className="size-4" />
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background px-5 py-2.5 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
            >
              Create Account
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
          {featureCards.map(({ title, description, icon: Icon }) => (
            <article
              key={title}
              className="rounded-xl border border-border bg-background p-4 sm:rounded-2xl sm:p-5"
            >
              <div className="mb-3 inline-flex rounded-lg bg-primary/10 p-2 text-primary">
                <Icon className="size-4" />
              </div>
              <h2 className="mb-1.5 text-sm font-semibold text-foreground sm:text-base">
                {title}
              </h2>
              <p className="text-xs leading-relaxed text-muted-foreground sm:text-sm">
                {description}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HomePage

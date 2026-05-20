import Link from 'next/link'
import { RetryButton } from './RetryButton'

interface RetryCardProps {
  cardTitle: string
  error: string
  tagToUpdate: string
}

export const RetryCard = ({
  cardTitle,
  error,
  tagToUpdate
}: RetryCardProps) => (
  <section className="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm">
    <h1 className="mb-3 text-2xl font-bold text-foreground sm:text-3xl">
      {cardTitle}
    </h1>
    <p className="mb-2 text-sm text-muted-foreground sm:text-base">
      The backend is waking up and items are not available yet.
    </p>
    <p className="mb-6 text-xs text-muted-foreground">Details: {error}</p>
    <div className="flex flex-col gap-3 sm:flex-row">
      <RetryButton tagToUpdate={tagToUpdate} />
      <Link
        href="/"
        className="inline-flex items-center justify-center rounded-lg border border-border bg-background px-4 py-2 text-sm font-semibold text-foreground transition-colors hover:bg-muted"
      >
        Go to home
      </Link>
    </div>
  </section>
)

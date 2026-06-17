import { BoxesIcon, DatabaseIcon, SparklesIcon } from 'lucide-react'
import Link from 'next/link'
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui'
import { focusAreas, learningTrack, stackLayers } from './utils'

const AboutPage = () => (
  <>
    <section className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
      <div className="flex flex-col gap-6">
        <Badge className="w-fit" variant="secondary">
          <BoxesIcon data-icon="inline-start" />
          Project dossier
        </Badge>

        <div className="flex flex-col gap-4">
          <h1 className="max-w-3xl text-4xl leading-tight font-bold text-foreground sm:text-5xl">
            A practical lab for learning modern FastAPI through a real web app.
          </h1>
          <p className="max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
            FastAPI Ecosystem Lab connects a Python API, a production-style
            Next.js frontend, and a Streamlit dashboard so backend concepts can
            be tested through real UI workflows.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button
            render={<Link href="/items" />}
            size="lg"
            nativeButton={false}
          >
            Explore Items
          </Button>
          <Button
            render={<Link href="/signup" />}
            size="lg"
            variant="outline"
            nativeButton={false}
          >
            Create Account
          </Button>
        </div>
      </div>

      <section
        aria-label="Project architecture"
        className="rounded-xl border bg-card p-4 shadow-sm sm:p-5"
      >
        <div className="grid gap-3">
          {stackLayers.map(({ title, detail, icon: Icon }) => (
            <article
              className="grid grid-cols-[auto_1fr] gap-3 rounded-lg border bg-background p-4"
              key={title}
            >
              <div className="flex size-10 items-center justify-center rounded-lg bg-muted text-primary">
                <Icon aria-hidden className="size-5" />
              </div>
              <div className="flex flex-col gap-1">
                <h2 className="text-sm font-semibold text-foreground">
                  {title}
                </h2>
                <p className="text-sm leading-6 text-muted-foreground">
                  {detail}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </section>

    <section className="grid gap-4 md:grid-cols-2">
      {focusAreas.map(({ title, description, icon: Icon }) => (
        <Card key={title}>
          <CardHeader>
            <div className="mb-1 flex size-9 items-center justify-center rounded-lg bg-muted text-primary">
              <Icon aria-hidden className="size-4" />
            </div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
        </Card>
      ))}
    </section>

    <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
      <div className="flex flex-col gap-3">
        <Badge className="w-fit" variant="outline">
          <SparklesIcon data-icon="inline-start" />
          Learning focus
        </Badge>
        <h2 className="text-2xl font-semibold text-foreground">
          Built to make backend patterns visible.
        </h2>
        <p className="text-sm leading-6 text-muted-foreground">
          The app keeps the learning surface concrete: create items, manage
          accounts, inspect auth behavior, and compare frontend approaches
          without leaving the same ecosystem.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>What this project exercises</CardTitle>
          <CardDescription>
            The repository is organized as a lab, so each feature maps back to a
            backend or frontend concept worth practicing.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="grid gap-3 sm:grid-cols-2">
            {learningTrack.map((item) => (
              <li className="flex items-center gap-2 text-sm" key={item}>
                <DatabaseIcon aria-hidden className="size-4 text-primary" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </section>
  </>
)

export default AboutPage

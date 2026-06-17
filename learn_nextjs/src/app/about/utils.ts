import {
  CableIcon,
  GaugeIcon,
  LockKeyholeIcon,
  RouteIcon,
  ServerIcon,
  ShieldCheckIcon,
  SignalIcon
} from 'lucide-react'

export const stackLayers = [
  {
    title: 'FastAPI Backend',
    detail: 'Versioned APIs, async SQLAlchemy, PostgreSQL, Alembic, JWT auth.',
    icon: ServerIcon
  },
  {
    title: 'Next.js Frontend',
    detail: 'App Router, Server Actions, typed fetch boundaries, Tailwind CSS.',
    icon: RouteIcon
  },
  {
    title: 'Streamlit Dashboard',
    detail: 'A Python-first interface for quick data workflows and comparison.',
    icon: GaugeIcon
  }
]

export const focusAreas = [
  {
    title: 'Authentication',
    description:
      'Login, signup, refresh, logout, protected routes, and account updates are modeled as real user flows.',
    icon: LockKeyholeIcon
  },
  {
    title: 'Data Ownership',
    description:
      'Item operations respect user ownership while preserving a superuser path for administrative access.',
    icon: ShieldCheckIcon
  },
  {
    title: 'Typed Boundaries',
    description:
      'Schemas, API response types, and server-only fetch helpers keep frontend and backend contracts explicit.',
    icon: CableIcon
  },
  {
    title: 'Runtime Feedback',
    description:
      'Cache tags, image uploads, and server-sent events make the app feel closer to a deployed product.',
    icon: SignalIcon
  }
]

export const learningTrack = [
  'Backend module boundaries',
  'Database migrations',
  'Authentication and cookies',
  'Typed form validation',
  'Production frontend routing'
]

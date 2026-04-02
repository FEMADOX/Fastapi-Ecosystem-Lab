import dotenv from 'dotenv'
import path from 'path'

// Load the shared .env from the monorepo root (FastAPI-Ecosystem-Lab/)
// process.cwd() is always learn_nextjs/ when running `next dev` or `next build`
dotenv.config({ path: path.join(process.cwd(), '../.env') })

// Load local overrides (learn_nextjs/.env.local), if present
dotenv.config({ path: path.join(process.cwd(), '.env.local'), override: true })

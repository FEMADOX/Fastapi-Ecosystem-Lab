import Link from 'next/link'

export const NavBar = () => (
  <nav className="pl-8 bg-gray-700">
    <ul className="flex items-center gap-5 [&>li:hover]:text-gray-800 [&>li]:transition-colors [&>li]:inline-block py-3">
      <li>
        <Link className="inline-block text-xl font-bold" href="/">
          FastAPI Ecosystem Lab
        </Link>
      </li>
      <li>
        <Link className="inline-block text-xl" href="/items">
          Items
        </Link>
      </li>
      <li>
        <Link className="inline-block text-xl" href="/about">
          About
        </Link>
      </li>
    </ul>
  </nav>
)

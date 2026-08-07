import { Link, useLocation } from 'react-router-dom'
import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function Header() {
  const { t } = useLanguage()
  const { pathname } = useLocation()

  const linkClass = (path) =>
    `flex items-center gap-1.5 ${pathname === path ? 'text-navy-700 font-bold' : 'hover:text-navy-700'}`

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-navy-100">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
        {/* SIKIKA Megaphone Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-orange-600 flex items-center justify-center text-white shadow-sm">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m3 11 18-5v12L3 13v-2z" />
              <path d="M11.6 16.8 a3 3 0 1 1-5.8-1.6" />
              <path d="M22 9a4 4 0 0 1 0 6" />
            </svg>
          </div>
          <span className="font-extrabold text-xl tracking-tight text-navy-700">SIKIKA</span>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-navy-400">
          <Link to="/" className={linkClass('/')}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a1 1 0 01-1 1h-5v-7H9v7H4a1 1 0 01-1-1z" />
            </svg>
            {t('navHome')}
          </Link>
          <Link to="/dashboard" className={linkClass('/dashboard')}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="12" width="4" height="8" />
              <rect x="10" y="7" width="4" height="13" />
              <rect x="17" y="3" width="4" height="17" />
            </svg>
            {t('navDashboard')}
          </Link>
        </nav>
      </div>
    </header>
  )
}
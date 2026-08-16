import { useState, useEffect, useRef } from 'react'
import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function DashboardHero({ selected, onSelect }) {
  const { t } = useLanguage()
  const [subs, setSubs] = useState([])
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    fetch('/api/subcounties')
      .then((r) => r.json())
      .then((d) => setSubs(d.subcounties || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const onDoc = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const label = selected || t('allSubCounties')

  return (
    <div className="relative z-30 bg-gradient-to-br from-teal-700 via-teal-600 to-[#0F172A]">
      <div
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{ background: 'radial-gradient(circle at 75% 15%, white, transparent 40%)' }}
      />
      <div className="relative max-w-7xl mx-auto px-5 sm:px-8 pt-10 pb-12">
        <span className="inline-block text-xs font-bold text-white bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full mb-4">
          {t('dashPortalTag')}
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-3">{t('dashTitle')}</h1>
        <p className="text-white/80 max-w-xl mb-6 text-sm sm:text-base leading-relaxed">{t('dashSubtitle')}</p>

        <div className="flex flex-wrap gap-3">
          <div className="relative" ref={ref}>
            <button
              onClick={() => setOpen((o) => !o)}
              className="flex items-center gap-2 bg-white/10 border border-white/30 text-white text-sm font-semibold px-4 py-2.5 rounded-lg hover:bg-white/20 transition"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0118 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              {label}
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                className={`transition-transform ${open ? 'rotate-180' : ''}`}
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            {open && (
              <div className="absolute left-0 mt-2 w-72 max-w-[85vw] max-h-[70vh] overflow-auto bg-white rounded-xl shadow-2xl border border-slate-200 py-2 z-50">
                <p className="px-4 pt-1 pb-2 text-[11px] font-bold uppercase tracking-wide text-slate-400 border-b border-slate-100 mb-1">
                  {t('subCountyHeader')}
                </p>
                {[null, ...subs].map((s) => {
                  const active = selected === s
                  return (
                    <button
                      key={s ?? 'all'}
                      onClick={() => {
                        onSelect(s)
                        setOpen(false)
                      }}
                      className={`w-full flex items-center justify-between text-left px-4 py-3 text-[15px] transition ${
                        active ? 'font-bold text-[#EA580C] bg-orange-50' : 'text-[#0F172A] hover:bg-slate-50'
                      }`}
                    >
                      {s || t('allSubCounties')}
                      {active && (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                          <path d="M20 6L9 17l-5-5" />
                        </svg>
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

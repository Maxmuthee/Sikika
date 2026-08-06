import { useState, useEffect, useMemo } from 'react'
import { useLanguage } from '../../i18n/LanguageContext.jsx'

const AVATARS = ['bg-navy-100 text-navy-700', 'bg-brand-50 text-brand', 'bg-teal-50 text-teal-600']

function sentimentClass(s) {
  if (s === 'support') return 'text-emerald-600 bg-emerald-50'
  if (s === 'oppose') return 'text-orange-600 bg-orange-50'
  return 'text-navy-400 bg-navy-50'
}

function initialsOf(name) {
  if (!name) return '??'
  return name.split(' ').filter(Boolean).map((w) => w[0]).join('').slice(0, 2).toUpperCase()
}

export default function LiveFeed() {
  const { t } = useLanguage()
  const [query, setQuery] = useState('')
  const [items, setItems] = useState([])

  useEffect(() => {
    fetch('/api/dashboard-stats')
      .then((r) => r.json())
      .then((d) => setItems(d.feedback || []))
      .catch(() => {})
  }, [])

  const filtered = useMemo(() => {
    if (!query.trim()) return items
    const q = query.toLowerCase()
    return items.filter(
      (f) => (f.text || '').toLowerCase().includes(q) || (f.name || '').toLowerCase().includes(q)
    )
  }, [query, items])

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="flex items-center gap-2 font-bold text-navy-700">{t('liveFeedTitle')}</h3>
        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          {t('live')}
        </span>
      </div>
      <p className="text-xs text-navy-400 mb-4">{t('liveFeedSubtitle')}</p>

      <div className="space-y-4">
        {filtered.length === 0 && (
          <p className="text-xs text-navy-300 text-center py-6">
            {items.length === 0
              ? 'No feedback yet — it appears here as citizens send it by SMS or USSD.'
              : 'No matches.'}
          </p>
        )}
        {filtered.map((f, i) => (
          <div key={i} className={i === filtered.length - 1 ? '' : 'border-b border-navy-50 pb-4'}>
            <div className="flex items-center justify-between mb-1.5 gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className={`shrink-0 w-7 h-7 rounded-full ${AVATARS[i % AVATARS.length]} text-[10px] font-bold flex items-center justify-center`}
                >
                  {initialsOf(f.name)}
                </span>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-navy-700 truncate">{f.name}</p>
                  <p className="text-[10px] text-navy-300 truncate">{f.theme}</p>
                </div>
              </div>
              <span className={`shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full ${sentimentClass(f.sentiment)}`}>
                {f.sentiment}
              </span>
            </div>
            <p className="text-xs text-navy-600 leading-relaxed break-words">{f.text}</p>
          </div>
        ))}
      </div>

      <div className="relative mt-4">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 text-navy-300"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="11" cy="11" r="7" />
          <path d="M21 21l-4.3-4.3" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t('searchPlaceholder')}
          className="w-full text-xs border border-navy-100 rounded-lg pl-9 pr-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
      </div>
    </div>
  )
}

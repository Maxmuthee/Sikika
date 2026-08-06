import { useState, useMemo } from 'react'
import { useLanguage } from '../../i18n/LanguageContext.jsx'

function FeedItem({ initials, initialsBg, initialsColor, nameKey, locKey, msgKey, langLabel, t, isLast }) {
  return (
    <div className={isLast ? '' : 'border-b border-navy-50 pb-4'}>
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <span
            className={`w-7 h-7 rounded-full ${initialsBg} ${initialsColor} text-[10px] font-bold flex items-center justify-center`}
          >
            {initials}
          </span>
          <div>
            <p className="text-xs font-semibold text-navy-700">{t(nameKey)}</p>
            <p className="text-[10px] text-navy-300">{t(locKey)}</p>
          </div>
        </div>
        <span className="text-[10px] font-medium text-navy-400 flex items-center gap-1">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 8l6 6 6-6" />
          </svg>
          {langLabel}
        </span>
      </div>
      <p className="text-xs text-navy-600 leading-relaxed">{t(msgKey)}</p>
      <div className="flex items-center gap-4 mt-2 text-[11px] font-semibold text-navy-400">
        <button className="flex items-center gap-1">{t('verify')}</button>
        <button>{t('translate')}</button>
        <button className="ml-auto">⋮</button>
      </div>
    </div>
  )
}

export default function LiveFeed() {
  const { t } = useLanguage()
  const [query, setQuery] = useState('')

  const citizens = [
    { key: 'c1', initials: 'C1', bg: 'bg-navy-100', color: 'text-navy-700', nameKey: 'citizen1', locKey: 'citizen1Loc', msgKey: 'citizen1Msg', lang: 'English' },
    { key: 'c2', initials: 'C2', bg: 'bg-brand-50', color: 'text-brand', nameKey: 'citizen2', locKey: 'citizen2Loc', msgKey: 'citizen2Msg', lang: 'Swahili' },
    { key: 'c3', initials: 'C3', bg: 'bg-teal-50', color: 'text-teal-600', nameKey: 'citizen3', locKey: 'citizen3Loc', msgKey: 'citizen3Msg', lang: 'English' },
  ]

  const filtered = useMemo(() => {
    if (!query.trim()) return citizens
    const q = query.toLowerCase()
    return citizens.filter((c) => t(c.msgKey).toLowerCase().includes(q))
  }, [query, t])

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
        {filtered.map((c, i) => (
          <FeedItem
            key={c.key}
            initials={c.initials}
            initialsBg={c.bg}
            initialsColor={c.color}
            nameKey={c.nameKey}
            locKey={c.locKey}
            msgKey={c.msgKey}
            langLabel={c.lang}
            t={t}
            isLast={i === filtered.length - 1}
          />
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

import { useState, useEffect } from 'react'
import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function EngagementChart() {
  const { t } = useLanguage()
  const [data, setData] = useState([]) // [{ label, value }]

  useEffect(() => {
    fetch('/api/dashboard-stats')
      .then((r) => r.json())
      .then((d) => setData(d.engagement || []))
      .catch(() => setData([]))
  }, [])

  const max = Math.max(1, ...data.map((d) => d.value))
  const empty = data.length > 0 && data.every((d) => d.value === 0)

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('chartTitle')}</h3>
        <span className="flex items-center gap-1.5 text-xs font-semibold text-navy-400 border border-navy-100 px-3 py-1.5 rounded-lg">
          {t('chartRange')}
        </span>
      </div>
      <p className="text-xs text-navy-400 mb-6">{t('chartSubtitle')}</p>

      <div className="relative flex items-end justify-between gap-3 h-56 border-b border-navy-100 pb-1">
        {empty && (
          <p className="absolute inset-0 flex items-center justify-center text-xs text-navy-300 text-center px-4">
            {t('noActivity7d')}
          </p>
        )}
        {data.map((d, i) => {
          const pct = Math.round((d.value / max) * 100)
          return (
            <div key={i} className="flex-1 flex flex-col items-center justify-end h-full group">
              <span className="text-[10px] font-bold text-navy-400 mb-1 opacity-0 group-hover:opacity-100 transition">
                {d.value}
              </span>
              <div
                className="w-full max-w-[34px] bg-brand rounded-t-md bar-rise"
                style={{ height: `${pct}%`, animationDelay: `${i * 80}ms` }}
              />
            </div>
          )
        })}
      </div>

      <div className="flex justify-between mt-2 text-[11px] font-medium text-navy-400">
        {data.map((d, i) => (
          <span key={i} className="flex-1 text-center">{d.label}</span>
        ))}
      </div>
    </div>
  )
}

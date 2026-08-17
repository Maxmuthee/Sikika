import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useLanguage } from '../i18n/LanguageContext.jsx'

function activityLabel(a) {
  const area = a.area ? ` · ${a.area}` : ''
  if (a.kind === 'feedback') return `New feedback${area}`
  if (a.kind === 'registration') return `New registration${area}`
  if (a.kind === 'vote') return 'Vote recorded'
  return 'Activity'
}

export default function CTABanner() {
  const { t } = useLanguage()
  const [activity, setActivity] = useState(null)
  const [showJoin, setShowJoin] = useState(false)

  useEffect(() => {
    const load = () =>
      fetch('/api/activity')
        .then((r) => r.json())
        .then((d) => setActivity(d.activity || []))
        .catch(() => setActivity([]))
    load()
    const id = setInterval(load, 15000) // keep it live
    return () => clearInterval(id)
  }, [])

  return (
    <section className="max-w-7xl mx-auto px-5 sm:px-8 pb-20">
      <div className="relative overflow-hidden bg-navy-700 rounded-3xl px-6 sm:px-8 py-12 sm:py-14 grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
        <div
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{ background: 'radial-gradient(circle at 80% 20%, #EA580C 0%, transparent 45%)' }}
        />

        <div className="relative">
          <span className="inline-block text-xs font-semibold bg-brand-50/10 text-brand-100 border border-brand/30 px-3 py-1 rounded-full mb-5">
            {t('ctaBadge')}
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-4 leading-tight">{t('ctaTitle')}</h2>
          <p className="text-navy-100/70 mb-7 max-w-md">{t('ctaBody')}</p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 bg-brand hover:bg-brand-700 text-white font-semibold px-5 py-3 rounded-lg transition"
            >
              {t('ctaPrimary')}
            </Link>
            <button
              onClick={() => setShowJoin(true)}
              className="inline-flex items-center gap-2 border border-white/20 hover:bg-white/10 text-white font-semibold px-5 py-3 rounded-lg transition"
            >
              {t('ctaSecondary')}
            </button>
          </div>
        </div>

        <div className="relative bg-navy-800 rounded-2xl p-5 border border-white/10">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold text-white/80 tracking-wide">{t('liveStatus')}</span>
          </div>
          <div className="space-y-3">
            {activity === null && (
              <div className="text-sm text-white/40 px-4 py-3">Loading…</div>
            )}
            {activity && activity.length === 0 && (
              <div className="bg-white/5 rounded-lg px-4 py-3 text-sm text-white/50">
                System online - awaiting citizen activity.
              </div>
            )}
            {activity &&
              activity.map((a, i) => (
                <div key={i} className="flex items-center justify-between gap-3 bg-white/5 rounded-lg px-4 py-3">
                  <span className="text-sm text-white/90 truncate">{activityLabel(a)}</span>
                  <span className="text-xs text-white/40 shrink-0">{a.ago}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {showJoin && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50"
          onClick={() => setShowJoin(false)}
        >
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-extrabold text-navy-700 text-lg">{t('joinTitle')}</h3>
              <button
                onClick={() => setShowJoin(false)}
                aria-label="Close"
                className="text-navy-400 hover:text-navy-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            <p className="text-sm text-navy-500 leading-relaxed">
              {t('joinBody')}
            </p>
            <ul className="mt-3 space-y-2 text-sm text-navy-600">
              <li className="flex gap-2">
                <span className="font-bold text-brand">1.</span>
                {t('joinStep1')}
              </li>
              <li className="flex gap-2">
                <span className="font-bold text-brand">2.</span>
                {t('joinStep2')}
              </li>
            </ul>
            <button
              onClick={() => setShowJoin(false)}
              className="mt-5 w-full bg-brand text-white text-sm font-semibold py-2.5 rounded-lg hover:bg-brand-700 transition"
            >
              {t('joinGotIt')}
            </button>
          </div>
        </div>
      )}
    </section>
  )
}

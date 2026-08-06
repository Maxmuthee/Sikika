import { Link } from 'react-router-dom'
import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function CTABanner() {
  const { t } = useLanguage()

  const feeds = [
    { labelKey: 'feed1', timeKey: 'minAgo2' },
    { labelKey: 'feed2', timeKey: 'minAgo3' },
    { labelKey: 'feed3', timeKey: 'minAgo7' },
  ]

  return (
    <section className="max-w-7xl mx-auto px-5 sm:px-8 pb-20">
      <div className="relative overflow-hidden bg-navy-700 rounded-3xl px-8 py-14 grid lg:grid-cols-2 gap-10 items-center">
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
            <button className="inline-flex items-center gap-2 border border-white/20 hover:bg-white/10 text-white font-semibold px-5 py-3 rounded-lg transition">
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
            {feeds.map((f) => (
              <div key={f.labelKey} className="flex items-center justify-between bg-white/5 rounded-lg px-4 py-3">
                <span className="text-sm text-white/90">{t(f.labelKey)}</span>
                <span className="text-xs text-white/40">{t(f.timeKey)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

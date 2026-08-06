import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function DashboardHero() {
  const { t } = useLanguage()

  return (
    <div className="relative bg-gradient-to-br from-teal-700 via-teal-600 to-[#0F172A] overflow-hidden">
      <div
        className="absolute inset-0 opacity-20"
        style={{ background: 'radial-gradient(circle at 75% 15%, white, transparent 40%)' }}
      />
      <div className="relative max-w-7xl mx-auto px-5 sm:px-8 pt-10 pb-12">
        <span className="inline-block text-xs font-bold text-white bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full mb-4">
          {t('dashPortalTag')}
        </span>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-3">{t('dashTitle')}</h1>
        <p className="text-white/80 max-w-xl mb-6 text-sm sm:text-base leading-relaxed">{t('dashSubtitle')}</p>

        <div className="flex flex-wrap gap-3">
          <button className="flex items-center gap-2 bg-white text-[#0F172A] text-sm font-semibold px-4 py-2.5 rounded-lg shadow-sm hover:bg-slate-50 transition">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 100 20 10 10 0 000-20z" />
              <path d="M2 12h20M12 2a15 15 0 010 20 15 15 0 010-20z" />
            </svg>
            {t('filterSector')}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
          <button className="flex items-center gap-2 bg-white/10 border border-white/30 text-white text-sm font-semibold px-4 py-2.5 rounded-lg hover:bg-white/20 transition">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0118 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            {t('filterLocation')}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
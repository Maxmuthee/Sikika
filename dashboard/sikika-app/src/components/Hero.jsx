import { Link } from 'react-router-dom'
import { useLanguage } from '../i18n/LanguageContext.jsx'
import LanguageToggle from './LanguageToggle.jsx'

export default function Hero() {
  const { t } = useLanguage()

  return (
    <section id="home" className="max-w-7xl mx-auto px-5 sm:px-8 pt-14 pb-16 grid lg:grid-cols-2 gap-12 items-center">
      <div>
        <div className="flex flex-wrap items-center gap-2 mb-6">
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold bg-brand-50 text-brand-700 px-3 py-1.5 rounded-full">
            {t('badgeInitiative')}
          </span>
          <LanguageToggle />
        </div>

        <h1 className="text-4xl sm:text-5xl font-extrabold leading-[1.1] tracking-tight text-navy-700 mb-5">
          {t('heroTitle1')} <span className="text-brand">{t('heroTitle2')}</span>
        </h1>

        <p className="text-navy-400 text-base leading-relaxed mb-8 max-w-md">{t('heroBody')}</p>

        <div className="flex flex-wrap gap-3 mb-10">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 bg-brand hover:bg-brand-700 text-white font-semibold px-5 py-3 rounded-lg transition shadow-sm shadow-brand-200"
          >
            {t('heroCtaPrimary')}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </Link>
          <button className="inline-flex items-center gap-2 border border-navy-100 hover:bg-navy-50 text-navy-700 font-semibold px-5 py-3 rounded-lg transition">
            {t('heroCtaSecondary')}
          </button>
        </div>

        <div className="flex gap-8">
          <div>
            <p className="text-2xl font-extrabold text-navy-700">12.4k+</p>
            <p className="text-xs text-navy-400 font-medium">{t('statCitizens')}</p>
          </div>
          <div className="border-l border-navy-100 pl-8">
            <p className="text-2xl font-extrabold text-navy-700">45</p>
            <p className="text-xs text-navy-400 font-medium">{t('statBills')}</p>
          </div>
          <div className="border-l border-navy-100 pl-8">
            <p className="text-2xl font-extrabold text-navy-700">98%</p>
            <p className="text-xs text-navy-400 font-medium">{t('statSms')}</p>
          </div>
        </div>
      </div>

      <div className="relative">
        <div className="rounded-2xl overflow-hidden shadow-xl aspect-[4/3] bg-navy-50">
          <img
            src="/images/hero-village.jpg"
            alt="Community gathering in rural Nakuru County"
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </section>
  )
}

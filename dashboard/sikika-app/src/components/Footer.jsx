import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer className="border-t border-navy-100 bg-white">
      <div className="max-w-7xl mx-auto px-5 sm:px-8 py-14 grid sm:grid-cols-3 gap-10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-md bg-brand flex items-center justify-center text-white">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M3 12l18-8-8 18-2-8-8-2z" />
              </svg>
            </div>
            <span className="font-extrabold text-navy-700">SIKIKA</span>
          </div>
          <p className="text-sm text-navy-400 leading-relaxed max-w-xs">{t('footerBody')}</p>
        </div>

        <div>
          <p className="text-xs font-bold text-navy-700 tracking-wide mb-4">{t('contactUs')}</p>
          <ul className="space-y-3 text-sm text-navy-400">
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16v16H4z" />
                <path d="M4 4l8 8 8-8" />
              </svg>
              info@sikika.go.ke
            </li>
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.7a2 2 0 01-.4 2.1L8 9.9a16 16 0 006 6l1.5-1.3a2 2 0 012.1-.4c.9.3 1.8.5 2.7.6a2 2 0 011.7 2.1z" />
              </svg>
              +254 20 123 4567
            </li>
            <li className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0118 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              Nakuru City, Kenya
            </li>
          </ul>
        </div>

        <div>
          <p className="text-xs font-bold text-navy-700 tracking-wide mb-4">{t('legal')}</p>
          <ul className="space-y-3 text-sm text-navy-400">
            <li>
              <a href="#" className="hover:text-brand">
                {t('privacy')}
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-brand">
                {t('terms')}
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-brand">
                {t('accessibility')}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-navy-100 py-5">
        <p className="text-center text-xs text-navy-300">{t('copyright')}</p>
      </div>
    </footer>
  )
}

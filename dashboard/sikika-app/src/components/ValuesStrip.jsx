import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function ValuesStrip() {
  const { t } = useLanguage()

  const values = ['valAccountability', 'valTransparency', 'valInclusivity', 'valJustice']

  return (
    <section className="max-w-7xl mx-auto px-5 sm:px-8 pb-16">
      <div className="flex flex-wrap items-center justify-between gap-6 border-t border-b border-navy-100 py-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-brand flex items-center justify-center text-white">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
              <path d="M3 12l18-8-8 18-2-8-8-2z" />
            </svg>
          </div>
          <span className="font-bold text-navy-700 text-sm">SIKIKA</span>
          <span className="text-xs text-navy-400 ml-2">{t('partnering')}</span>
        </div>

        <div className="flex flex-wrap gap-6 text-xs font-semibold text-navy-400">
          {values.map((v) => (
            <span key={v} className="flex items-center gap-1.5">
              <svg width="13" height="13" className="text-brand" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <circle cx="12" cy="12" r="10" />
              </svg>
              {t(v)}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}

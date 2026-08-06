import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function CoreFunctions() {
  const { t } = useLanguage()

  const cards = [
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 17l6-6 4 4 8-8" />
          <path d="M21 7v6h-6" />
        </svg>
      ),
      titleKey: 'coreTrackerTitle',
      bodyKey: 'coreTrackerBody',
      tagKey: 'coreTrackerTag',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 00-3-3.87" />
          <path d="M16 3.13a4 4 0 010 7.75" />
        </svg>
      ),
      titleKey: 'coreFeedbackTitle',
      bodyKey: 'coreFeedbackBody',
      tagKey: 'coreFeedbackTag',
    },
    {
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z" />
        </svg>
      ),
      titleKey: 'coreVerifyTitle',
      bodyKey: 'coreVerifyBody',
      tagKey: 'coreVerifyTag',
    },
  ]

  return (
    <section className="py-20 max-w-7xl mx-auto px-5 sm:px-8">
      <h2 className="text-2xl sm:text-3xl font-extrabold text-navy-700 mb-2">{t('coreTitle')}</h2>
      <div className="w-14 h-1 bg-brand rounded-full mb-10" />

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((c) => (
          <div key={c.titleKey} className="border border-navy-100 rounded-2xl p-6 hover:shadow-md transition">
            <div className="w-10 h-10 rounded-lg bg-brand-50 text-brand flex items-center justify-center mb-4">
              {c.icon}
            </div>
            <h3 className="font-bold text-navy-700 mb-1.5">{t(c.titleKey)}</h3>
            <p className="text-sm text-navy-400 mb-4">{t(c.bodyKey)}</p>
            <div className="flex items-center justify-between border-t border-navy-100 pt-4 text-xs">
              <span className="font-semibold text-brand">{t(c.tagKey)}</span>
              <span className="font-semibold text-navy-400">{t('learnMore')}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

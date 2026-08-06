import { useLanguage } from '../i18n/LanguageContext.jsx'

const features = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4l3 2" />
      </svg>
    ),
    titleKey: 'featAccessTitle',
    bodyKey: 'featAccessBody',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M4 4h16v12H7l-3 3z" />
      </svg>
    ),
    titleKey: 'featSmsTitle',
    bodyKey: 'featSmsBody',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
      </svg>
    ),
    titleKey: 'featLangTitle',
    bodyKey: 'featLangBody',
  },
]

export default function Mission() {
  const { t } = useLanguage()

  return (
    <section className="bg-navy-50/60 py-20">
      <div className="max-w-7xl mx-auto px-5 sm:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="text-brand font-bold text-xs tracking-widest uppercase mb-3">{t('missionEyebrow')}</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-navy-700 mb-4">{t('missionTitle')}</h2>
          <p className="text-navy-400">{t('missionSubtitle')}</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-10 items-start">
          <div className="bg-white rounded-2xl p-3 shadow-sm border border-navy-100">
            <img
              src="/images/mission-illustration.jpg"
              alt="Illustration of an inclusive community network"
              className="w-full max-h-[420px] rounded-xl object-cover object-top"
            />
          </div>

          <div>
            <h3 className="text-xl font-bold text-navy-700 mb-2">{t('whyTitle')}</h3>
            <p className="text-navy-400 mb-6 leading-relaxed">{t('whyBody')}</p>

            <div className="space-y-3">
              {features.map((f) => (
                <div key={f.titleKey} className="flex gap-3 bg-white border border-navy-100 rounded-xl p-4">
                  <div className="w-9 h-9 shrink-0 rounded-lg bg-brand-50 text-brand flex items-center justify-center">
                    {f.icon}
                  </div>
                  <div>
                    <p className="font-semibold text-navy-700 text-sm">{t(f.titleKey)}</p>
                    <p className="text-xs text-navy-400 mt-1">{t(f.bodyKey)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
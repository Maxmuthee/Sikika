import { useLanguage } from '../../i18n/LanguageContext.jsx'

// Bar values for Mon–Sun. Swap these out for real data whenever you wire up an API.
const VALUES = [110, 390, 255, 680, 600, 175, 155]
const MAX = Math.max(...VALUES)

export default function EngagementChart() {
  const { t } = useLanguage()
  const days = t('days')

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('chartTitle')}</h3>
        <button className="flex items-center gap-1.5 text-xs font-semibold text-navy-400 border border-navy-100 px-3 py-1.5 rounded-lg">
          {t('chartRange')}
        </button>
      </div>
      <p className="text-xs text-navy-400 mb-6">{t('chartSubtitle')}</p>

      <div className="flex items-end justify-between gap-3 h-56 border-b border-navy-100 pb-1">
        {VALUES.map((v, i) => {
          const pct = Math.round((v / MAX) * 100)
          return (
            <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
              <div
                className="w-full max-w-[34px] bg-brand rounded-t-md bar-rise"
                style={{ height: `${pct}%`, animationDelay: `${i * 80}ms` }}
              />
            </div>
          )
        })}
      </div>

      <div className="flex justify-between mt-2 text-[11px] font-medium text-navy-400">
        {days.map((d) => (
          <span key={d}>{d}</span>
        ))}
      </div>
    </div>
  )
}

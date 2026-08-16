import { useLanguage } from '../../i18n/LanguageContext.jsx'

// Round a value up to a "nice" ceiling (1/2/5 × 10^n) for clean axis ticks.
function niceMax(v) {
  const pow = Math.pow(10, Math.floor(Math.log10(Math.max(v, 1))))
  const n = v / pow
  const step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10
  return step * pow
}

export default function EngagementChart({ engagement }) {
  const { t } = useLanguage()
  const data = engagement || []

  const max = niceMax(Math.max(1, ...data.map((d) => d.value)))
  const empty = data.length > 0 && data.every((d) => d.value === 0)
  // 4 evenly spaced ticks (0, 1/3, 2/3, max) so bar values can be read exactly.
  const ticks = [0, max / 3, (2 * max) / 3, max].map((v) => Math.round(v))

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('chartTitle')}</h3>
        <span className="flex items-center gap-1.5 text-xs font-semibold text-navy-400 border border-navy-100 px-3 py-1.5 rounded-lg">
          {t('chartRange')}
        </span>
      </div>
      <p className="text-xs text-navy-400 mb-6">{t('chartSubtitle')}</p>

      <div className="flex">
        {/* Y-axis scale */}
        <div className="relative h-56 w-8 shrink-0 mr-2 text-[10px] font-medium text-navy-400">
          {ticks.map((v) => (
            <span
              key={v}
              className="absolute right-0 leading-none -translate-y-1/2"
              style={{ bottom: `${(v / max) * 100}%` }}
            >
              {v}
            </span>
          ))}
        </div>

        <div className="relative flex-1 flex items-end justify-between gap-3 h-56 border-b border-navy-100 pb-1">
          {empty && (
            <p className="absolute inset-0 flex items-center justify-center text-xs text-navy-300 text-center px-4">
              {t('noActivity7d')}
            </p>
          )}
          {/* horizontal gridlines at each tick */}
          {ticks
            .filter((v) => v !== 0)
            .map((v) => (
              <div
                key={v}
                className="absolute left-0 right-0 border-t border-dashed border-navy-50 pointer-events-none"
                style={{ bottom: `${(v / max) * 100}%` }}
              />
            ))}
          {data.map((d, i) => {
            const pct = Math.round((d.value / max) * 100)
            return (
              <div key={i} className="relative flex-1 flex flex-col items-center justify-end h-full group">
                <span className="text-[10px] font-bold text-navy-700 mb-1">{d.value}</span>
                <div
                  className="w-full max-w-[34px] bg-brand rounded-t-md bar-rise"
                  style={{ height: `${pct}%`, animationDelay: `${i * 80}ms` }}
                />
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex justify-between mt-2 text-[11px] font-medium text-navy-400">
        {data.map((d, i) => (
          <span key={i} className="flex-1 text-center">{d.label}</span>
        ))}
      </div>
    </div>
  )
}

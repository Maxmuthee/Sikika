import { useLanguage } from '../../i18n/LanguageContext.jsx'

// Pick a clean integer step (1/2/5 × 10^n) so the axis shows equal, readable
// intervals and every gridline matches its label exactly.
function niceStep(rough) {
  const r = Math.max(rough, 0.1)
  const pow = Math.pow(10, Math.floor(Math.log10(r)))
  const n = r / pow
  const s = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10
  return s * pow
}

export default function EngagementChart({ engagement }) {
  const { t } = useLanguage()
  const data = engagement || []

  const maxVal = Math.max(0, ...data.map((d) => d.value))
  // 3 equal steps up from 0; axisMax is always >= maxVal.
  const step = Math.max(1, niceStep(maxVal / 3))
  const axisMax = step * 3
  const ticks = [0, step, step * 2, step * 3]

  const empty = data.length > 0 && data.every((d) => d.value === 0)

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('chartTitle')}</h3>
        <span className="flex items-center gap-1.5 text-xs font-semibold text-navy-400 border border-navy-100 px-3 py-1.5 rounded-lg">
          {t('chartRange')}
        </span>
      </div>
      <p className="text-sm text-navy-400 mb-6">{t('chartSubtitle')}</p>

      <div className="flex">
        {/* Y-axis scale — same height & padding as the plot so labels line up */}
        <div className="relative h-56 w-10 shrink-0 mr-2 pb-1 text-xs font-semibold text-navy-500">
          {ticks.map((v) => (
            <span
              key={v}
              className="absolute right-2 leading-none -translate-y-1/2"
              style={{ bottom: `${(v / axisMax) * 100}%` }}
            >
              {v}
            </span>
          ))}
        </div>

        <div className="relative flex-1 flex items-end justify-between gap-3 h-56 border-b border-navy-100 pb-1">
          {empty && (
            <p className="absolute inset-0 flex items-center justify-center text-sm text-navy-300 text-center px-4">
              {t('noActivity7d')}
            </p>
          )}
          {/* horizontal gridlines at every tick — exact same positions as the labels */}
          {ticks
            .filter((v) => v !== 0)
            .map((v) => (
              <div
                key={v}
                className="absolute left-0 right-0 border-t border-dashed border-navy-50 pointer-events-none"
                style={{ bottom: `${(v / axisMax) * 100}%` }}
              />
            ))}
          {data.map((d, i) => {
            const pct = axisMax === 0 ? 0 : Math.round((d.value / axisMax) * 100)
            return (
              <div key={i} className="relative flex-1 flex flex-col items-center justify-end h-full group">
                <span className="text-xs font-bold text-navy-700 mb-1">{d.value}</span>
                <div
                  className="w-full max-w-[34px] bg-brand rounded-t-md bar-rise"
                  style={{ height: `${pct}%`, animationDelay: `${i * 80}ms` }}
                />
              </div>
            )
          })}
        </div>
      </div>

      <div className="flex justify-between mt-2 text-xs font-medium text-navy-400">
        {data.map((d, i) => (
          <span key={i} className="flex-1 text-center">{d.label}</span>
        ))}
      </div>
    </div>
  )
}

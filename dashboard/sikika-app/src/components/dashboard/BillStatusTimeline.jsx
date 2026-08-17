import { useLanguage } from '../../i18n/LanguageContext.jsx'

const STAGE_KEYS = [
  'stageFirstReading',
  'stagePublicParticipation',
  'stageCommitteeReview',
  'stageSecondReading',
  'stageGovernorsAssent',
]

export default function BillStatusTimeline({ bill }) {
  const { t } = useLanguage()

  const current = bill ? bill.stage : -1

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <h3 className="font-bold text-navy-700 mb-4">{t('billStatusTitle')}</h3>

      <ol className="relative border-l-2 border-navy-100 ml-2 space-y-5">
        {STAGE_KEYS.map((key, i) => {
          const done = i < current
          const active = i === current
          const dot = active
            ? 'bg-brand ring-4 ring-brand-100'
            : done
              ? 'bg-brand ring-2 ring-brand'
              : 'bg-white border-2 border-navy-200'
          const text = active ? 'text-brand' : done ? 'text-navy-700' : 'text-navy-300'
          return (
            <li key={key} className="ml-4">
              <span className={`absolute -left-[9px] w-4 h-4 rounded-full border-2 border-white ${dot}`} />
              <p className={`text-base font-semibold ${text}`}>{t(key)}</p>
              {active && (
                <p className="text-sm text-navy-400">
                  {t('stageCurrentPhase')}
                  {bill && bill.participants > 0 && (
                    <> · {bill.participants} {t('citizensEngaged')}</>
                  )}
                </p>
              )}
            </li>
          )
        })}
      </ol>
    </div>
  )
}

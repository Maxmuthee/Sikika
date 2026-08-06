import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function BillStatusTimeline() {
  const { t } = useLanguage()

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <h3 className="flex items-center gap-2 font-bold text-navy-700 mb-4">{t('billStatusTitle')}</h3>

      <ol className="relative border-l-2 border-navy-100 ml-2 space-y-5">
        <li className="ml-4">
          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-brand border-2 border-white ring-2 ring-brand" />
          <p className="text-sm font-semibold text-navy-700">{t('stageFirstReading')}</p>
          <p className="text-xs text-navy-400">Oct 12, 2025</p>
        </li>
        <li className="ml-4">
          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-brand border-2 border-white ring-2 ring-brand" />
          <p className="text-sm font-semibold text-navy-700">{t('stagePublicParticipation')}</p>
          <p className="text-xs text-navy-400">Nov 05, 2025</p>
        </li>
        <li className="ml-4">
          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-brand border-2 border-white ring-4 ring-brand-100" />
          <p className="text-sm font-semibold text-brand">{t('stageCommitteeReview')}</p>
          <p className="text-xs text-navy-400">{t('stageCurrentPhase')}</p>
        </li>
        <li className="ml-4">
          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-white border-2 border-navy-200" />
          <p className="text-sm font-semibold text-navy-300">{t('stageSecondReading')}</p>
        </li>
        <li className="ml-4">
          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-white border-2 border-navy-200" />
          <p className="text-sm font-semibold text-navy-300">{t('stageGovernorsAssent')}</p>
        </li>
      </ol>
    </div>
  )
}

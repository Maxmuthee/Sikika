import { useLanguage } from '../../i18n/LanguageContext.jsx'

const STATUS_STYLES = {
  Proposed: 'bg-amber-50 text-amber-700 border-amber-200',
  Bill: 'bg-teal-50 text-teal-700 border-teal-200',
  Ongoing: 'bg-emerald-50 text-emerald-700 border-emerald-200',
}

export default function BillsList({ bills }) {
  const { t } = useLanguage()
  const list = bills || []

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('billsListTitle')}</h3>
        <span className="text-[10px] font-bold text-navy-400 bg-navy-50 px-2 py-0.5 rounded-full">
          {list.length}
        </span>
      </div>
      <p className="text-xs text-navy-400 mb-4">{t('billsListSubtitle')}</p>

      {list.length === 0 && (
        <p className="text-xs text-navy-300 text-center py-6">{t('billsListEmpty')}</p>
      )}

      <ul className="divide-y divide-navy-50">
        {list.map((b) => (
          <li key={b.id} className="py-3.5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-semibold text-navy-700 leading-snug">{b.name}</p>
                <p className="text-xs text-navy-400 mt-0.5">{b.ward}</p>
              </div>
              <span
                className={`shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                  STATUS_STYLES[b.status] || 'bg-slate-50 text-slate-600 border-slate-200'
                }`}
              >
                {b.status}
              </span>
            </div>
            <div className="flex items-center gap-4 mt-2 text-[11px] font-medium text-navy-400">
              <span>
                <span className="text-emerald-600 font-bold">✓</span> {b.support} {t('billsListSupport')}
              </span>
              <span>
                <span className="text-orange-600 font-bold">✗</span> {b.oppose} {t('billsListOppose')}
              </span>
              <span>
                <span className="text-navy-500 font-bold">💬</span> {b.feedback_count} {t('billsListFeedback')}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
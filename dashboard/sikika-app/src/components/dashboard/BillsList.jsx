import { useLanguage } from '../../i18n/LanguageContext.jsx'

const STATUS_STYLES = {
  Proposed: 'bg-amber-50 text-amber-700 border-amber-200',
  Bill: 'bg-teal-50 text-teal-700 border-teal-200',
  Ongoing: 'bg-emerald-50 text-emerald-700 border-emerald-200',
}

const ICON = {
  stroke: 'currentColor',
  strokeWidth: 2,
  fill: 'none',
  className: 'w-3.5 h-3.5',
}

export default function BillsList({ bills }) {
  const { t } = useLanguage()
  const list = bills || []

  return (
    <div className="bg-white border border-navy-100 rounded-2xl p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-bold text-navy-700">{t('billsListTitle')}</h3>
        <span className="text-xs font-bold text-navy-400 bg-navy-50 px-2 py-0.5 rounded-full">
          {list.length}
        </span>
      </div>
      <p className="text-sm text-navy-400 mb-4">{t('billsListSubtitle')}</p>

      {list.length === 0 && (
        <p className="text-sm text-navy-300 text-center py-6">{t('billsListEmpty')}</p>
      )}

      <ul className="divide-y divide-navy-50">
        {list.map((b) => (
          <li key={b.id} className="py-3.5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-base font-semibold text-navy-700 leading-snug">{b.name}</p>
                <p className="text-sm text-navy-400 mt-0.5">{b.ward}</p>
              </div>
              <span
                className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded-full border ${
                  STATUS_STYLES[b.status] || 'bg-slate-50 text-slate-600 border-slate-200'
                }`}
              >
                {b.status}
              </span>
            </div>
            <div className="flex items-center gap-5 mt-2 text-sm font-medium text-navy-500">
              <span className="flex items-center gap-1.5">
                <svg {...ICON} className="w-4 h-4 text-emerald-600" viewBox="0 0 24 24">
                  <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                </svg>
                {b.support} {t('billsListSupport')}
              </span>
              <span className="flex items-center gap-1.5">
                <svg {...ICON} className="w-4 h-4 text-orange-600" viewBox="0 0 24 24">
                  <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3z" />
                  <path d="M17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3" />
                </svg>
                {b.oppose} {t('billsListOppose')}
              </span>
              <span className="flex items-center gap-1.5">
                <svg {...ICON} className="w-4 h-4 text-navy-500" viewBox="0 0 24 24">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                {b.feedback_count} {t('billsListFeedback')}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function BillCard() {
  const { t } = useLanguage()

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
      <div className="flex flex-col md:flex-row items-stretch md:min-h-[320px]">
        {/* Left Column: Fixed aspect & height scaling */}
        <div className="md:w-1/2 bg-amber-50 h-48 md:h-auto md:min-h-[220px] relative">
          <img
            src="/images/bill-produce.jpg"
            alt="Agricultural produce crate"
            className="w-full h-full object-cover absolute inset-0"
          />
        </div>

        {/* Right Column: Content */}
        <div className="md:w-1/2 p-5 flex flex-col justify-between">
          <div>
            <span className="inline-block text-[10px] font-bold text-[#EA580C] tracking-wide uppercase mb-2">
              {t('activeLegislation')}
            </span>

            <div className="flex items-start justify-between gap-2 mb-3">
              <h3 className="font-bold text-[#0F172A] text-lg leading-snug">{t('billTitle')}</h3>
              <div className="flex gap-2 shrink-0 text-slate-400">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
                </svg>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="18" cy="5" r="3" />
                  <circle cx="6" cy="12" r="3" />
                  <circle cx="18" cy="19" r="3" />
                  <path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" />
                </svg>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-500 mb-1">
                  <span>{t('publicSupport')}</span>
                  <span className="text-[#0F172A] font-bold">78%</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#EA580C] rounded-full" style={{ width: '78%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs font-medium text-slate-500 mb-1">
                  <span>{t('budgetAlignment')}</span>
                  <span className="text-[#0F172A] font-bold">92%</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#EA580C] rounded-full" style={{ width: '92%' }} />
                </div>
              </div>
            </div>

            <div className="bg-slate-50 rounded-xl p-3.5 mb-4 border border-slate-100">
              <span className="inline-block text-[10px] font-bold text-[#EA580C] mb-1">{t('aiInsightTag')}</span>
              <p className="text-xs text-slate-600 leading-relaxed">{t('aiInsightBody')}</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex -space-x-2">
              <span className="w-6 h-6 rounded-full bg-slate-600 text-white text-[9px] flex items-center justify-center border-2 border-white font-bold">
                U1
              </span>
              <span className="w-6 h-6 rounded-full bg-[#EA580C] text-white text-[9px] flex items-center justify-center border-2 border-white font-bold">
                U2
              </span>
              <span className="w-6 h-6 rounded-full bg-teal-600 text-white text-[9px] flex items-center justify-center border-2 border-white font-bold">
                U3
              </span>
              <span className="w-6 h-6 rounded-full bg-slate-200 text-[#0F172A] text-[9px] flex items-center justify-center border-2 border-white font-bold">
                +12
              </span>
            </div>
            <button className="flex items-center gap-1.5 bg-[#EA580C] hover:bg-orange-700 text-white text-xs font-semibold px-3.5 py-2 rounded-lg transition">
              {t('readFullText')} →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
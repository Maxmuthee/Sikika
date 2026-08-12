import { useLanguage } from '../../i18n/LanguageContext.jsx'

export default function SubmitCTA() {
  const { t } = useLanguage()

  return (
    <div className="bg-brand rounded-2xl p-5 text-white">
      <h3 className="font-bold text-lg mb-1.5">{t('submitTitle')}</h3>
      <p className="text-sm text-white/90 mb-4">
        {t('submitBody')
          .split('20880')
          .reduce((acc, part, i, arr) => {
            acc.push(part)
            if (i < arr.length - 1) acc.push(<strong key={i}>20880</strong>)
            return acc
          }, [])}
      </p>
    </div>
  )
}

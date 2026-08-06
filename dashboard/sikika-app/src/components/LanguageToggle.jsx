import { useLanguage } from '../i18n/LanguageContext.jsx'

export default function LanguageToggle() {
  const { lang, toggleLang } = useLanguage()

  return (
    <button
      onClick={toggleLang}
      className="inline-flex items-center gap-1 text-xs font-semibold bg-navy-50 text-navy-400 px-1 py-1 rounded-full"
    >
      <span
        className={`px-2.5 py-1 rounded-full transition ${
          lang === 'sw' ? 'bg-brand text-white' : 'text-navy-400'
        }`}
      >
        Swahili
      </span>
      <span
        className={`px-2.5 py-1 rounded-full transition ${
          lang === 'en' ? 'bg-brand text-white' : 'text-navy-400'
        }`}
      >
        English
      </span>
    </button>
  )
}

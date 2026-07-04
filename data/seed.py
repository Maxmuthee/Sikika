"""Seed projects + fallback translations across Nakuru sub-counties.

Real, current items (FY2025/26 Nakuru budget priorities + bills before
Parliament in 2026), each placed in ONE sub-county so no bill repeats across
the menu. Sources: Nakuru County FY2025/26 estimates (roads 800km, water
ceiling KSh 413M, total KSh 20.7B); Parliament 2026 bill tracker (Finance Bill
2026, Constitution of Kenya (Amendment) Bill 2026); Ministry of Mining
Explosives Bill 2026.

Fallback translations are HAND-WRITTEN plain-language stand-ins so USSD works
with no API key. Amounts are written in Kiswahili words (e.g. "shilingi milioni
tano"), never "KSh 5M". scripts/ingest.py overwrites these with real,
length-capped AI output once ANTHROPIC_API_KEY is set.
"""

from __future__ import annotations

import os

from app import store

_HERE = os.path.dirname(__file__)
EXPLOSIVES_PDF = os.path.join(_HERE, "explosives_bill_2026.pdf")

# Each project: sub-county, English name, raw English source, optional PDF,
# status, and hand-written sw/en fallback screens.
PROJECTS = [
    {
        "sub": "Molo", "name_en": "Molo fertilizer subsidy", "status": "Proposed",
        "raw": ("Agriculture, Livestock & Fisheries. Proposed FY2025/26: fertilizer "
                "subsidy for smallholder farmers, Molo, Nakuru County: KSh 5,000,000 "
                "from the Nakuru County Agricultural Development Fund; 2,000 subsidised "
                "bags of NPK fertilizer. Status: proposed, public forum 10 July, Molo Hall."),
        "t": {
            "sw": {
                "project_name": "Ruzuku ya mbolea Molo",
                "sms_alert": "Sikika: Nakuru imependekeza shilingi milioni tano ruzuku ya mbolea Molo. Baraza 10 Julai, Molo Hall. Piga *384# kupiga kura.",
                "civic_education": "Kila mwaka kaunti hutenga pesa kupunguza bei ya mbolea kwa wakulima wadogo. Mwaka huu ni shilingi milioni tano, mifuko elfu mbili.",
                "data_summary": "Kiasi: shilingi milioni tano. Chanzo: Mfuko wa Kilimo Nakuru. Hali: Inasubiri idhini.",
            },
            "en": {
                "project_name": "Molo fertilizer subsidy",
                "sms_alert": "Sikika: Nakuru proposed KSh 5 million fertilizer subsidy for Molo. Baraza 10 July, Molo Hall. Dial *384# to vote.",
                "civic_education": "Each year the county sets aside money to cut fertilizer costs for small farmers. This year: 5 million shillings, 2,000 bags.",
                "data_summary": "Amount: 5 million shillings. Source: Nakuru Agricultural Fund. Status: Proposed for approval.",
            },
        },
    },
    {
        "sub": "Molo", "name_en": "The Explosives Bill 2026", "status": "Bill",
        "pdf": EXPLOSIVES_PDF,
        "raw": ("The Explosives Bill, 2026 (Ministry of Mining). Regulates manufacture, "
                "import, storage, transport, sale and use of explosives in Kenya via "
                "licences, permits, inspection and penalties. Affects quarry workers, "
                "miners and traders who handle blasting materials."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Vilipuzi 2026",
                "sms_alert": "Sikika: Mswada mpya wa Vilipuzi unaweka leseni na adhabu kwa wanaotumia baruti. Piga *384# kujifunza na kutoa maoni.",
                "civic_education": "Sheria mpya inadhibiti nani anaweza kutengeneza, kuhifadhi au kutumia vilipuzi; wachimbaji watahitaji leseni.",
                "data_summary": "Mswada wa Vilipuzi 2026. Na: Wizara ya Madini. Unaweka: leseni, vibali, ukaguzi, adhabu. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "The Explosives Bill 2026",
                "sms_alert": "Sikika: A new Explosives Bill sets licences, permits & penalties for handling blasting materials. Dial *384# to learn & comment.",
                "civic_education": "A new law controls who may make, store, move or use explosives; miners and quarry workers will need licences.",
                "data_summary": "Explosives Bill 2026. By: Ministry of Mining. Adds: licences, permits, inspections, penalties. Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Njoro", "name_en": "Njoro water rehabilitation", "status": "Proposed",
        "raw": ("Water, Environment & Natural Resources. FY2025/26 water sector needs "
                "KSh 979,883,620 for development against a ceiling of KSh 413,356,364; "
                "funds rehabilitation of water systems and boreholes serving rural wards."),
        "t": {
            "sw": {
                "project_name": "Ukarabati wa maji Njoro",
                "sms_alert": "Sikika: Nakuru imetenga shilingi milioni 413 kwa ukarabati wa maji na visima. Piga *384# kuona na kutoa maoni.",
                "civic_education": "Kaunti inataka kukarabati mifumo ya maji na visima ili vijiji vipate maji safi ya kutosha.",
                "data_summary": "Kikomo: shilingi milioni 413. Chanzo: Sekta ya Maji Nakuru. Hali: Bajeti inayopendekezwa.",
            },
            "en": {
                "project_name": "Njoro water rehabilitation",
                "sms_alert": "Sikika: Nakuru set aside KSh 413 million to rehabilitate water systems & boreholes. Dial *384# to view & comment.",
                "civic_education": "The county plans to repair water systems and boreholes so villages get enough clean water.",
                "data_summary": "Ceiling: 413 million shillings. Source: Nakuru Water sector. Status: Proposed budget.",
            },
        },
    },
    {
        "sub": "Naivasha", "name_en": "Naivasha roads upgrade", "status": "Ongoing",
        "raw": ("Roads & Transport. FY2025/26 the county plans to upgrade over 800 km "
                "of roads county-wide using graders, rollers, dozers, excavators and "
                "tippers for grading, gravelling and drainage; Naivasha ward roads included."),
        "t": {
            "sw": {
                "project_name": "Ukarabati wa barabara Naivasha",
                "sms_alert": "Sikika: Nakuru inapanga kukarabati zaidi ya kilomita 800 za barabara. Barabara za Naivasha zimo. Piga *384# kutoa maoni.",
                "civic_education": "Kaunti inatumia mitambo kusawazisha, kuweka changarawe na mifereji kwenye barabara za vijijini.",
                "data_summary": "Lengo: kilomita 800 za barabara. Chanzo: Ada ya Matengenezo ya Barabara. Hali: Inaendelea.",
            },
            "en": {
                "project_name": "Naivasha roads upgrade",
                "sms_alert": "Sikika: Nakuru plans to upgrade over 800 km of roads; Naivasha ward roads included. Dial *384# to comment.",
                "civic_education": "The county uses machinery to grade, gravel and drain rural roads so they are passable all year.",
                "data_summary": "Target: 800 km of roads. Source: Roads Maintenance Levy. Status: Ongoing.",
            },
        },
    },
    {
        "sub": "Nakuru Town East", "name_en": "Health facilities upgrade", "status": "Proposed",
        "raw": ("Health Services. FY2025/26 priority: upgrade health infrastructure and "
                "increase access to quality services, including equipping dispensaries "
                "and health centres across Nakuru sub-counties."),
        "t": {
            "sw": {
                "project_name": "Uboreshaji wa hospitali",
                "sms_alert": "Sikika: Nakuru inapanga kuboresha hospitali na zahanati na kuongeza huduma bora. Piga *384# kuona na kutoa maoni.",
                "civic_education": "Kaunti inataka kuimarisha zahanati na vituo vya afya ili wananchi wapate matibabu bora karibu nao.",
                "data_summary": "Sekta: Afya. Chanzo: Bajeti ya Kaunti Nakuru. Hali: Bajeti inayopendekezwa.",
            },
            "en": {
                "project_name": "Health facilities upgrade",
                "sms_alert": "Sikika: Nakuru plans to upgrade hospitals & dispensaries and widen access to care. Dial *384# to view & comment.",
                "civic_education": "The county wants to strengthen dispensaries and health centres so people get good care close to home.",
                "data_summary": "Sector: Health. Source: Nakuru County budget. Status: Proposed budget.",
            },
        },
    },
    {
        "sub": "Gilgil", "name_en": "The Finance Bill 2026", "status": "Bill",
        "raw": ("The Finance Bill, 2026 (National Assembly). Proposes changes to taxes, "
                "levies and duties that affect prices, businesses and household incomes. "
                "Open for public participation."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Fedha 2026",
                "sms_alert": "Sikika: Mswada wa Fedha 2026 unapendekeza mabadiliko ya kodi yanayogusa bei na biashara. Piga *384# kujifunza na kutoa maoni.",
                "civic_education": "Mswada wa Fedha huamua kodi na tozo za mwaka. Mabadiliko yanaweza kubadilisha bei za bidhaa na mapato ya kaya.",
                "data_summary": "Mswada wa Fedha 2026. Na: Bunge la Kitaifa. Unagusa: kodi, tozo, bei. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "The Finance Bill 2026",
                "sms_alert": "Sikika: The Finance Bill 2026 proposes tax changes affecting prices & businesses. Dial *384# to learn & comment.",
                "civic_education": "The Finance Bill sets the year's taxes and levies. Changes can shift the price of goods and household income.",
                "data_summary": "Finance Bill 2026. By: National Assembly. Affects: taxes, levies, prices. Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Rongai", "name_en": "Rongai ward infrastructure", "status": "Proposed",
        "raw": ("Ward development. FY2025/26 ward proposals prioritise infrastructure "
                "then water; Rongai ward allocation funds local roads, drainage and "
                "small water points under the Roads Maintenance Levy."),
        "t": {
            "sw": {
                "project_name": "Miundombinu ya kata Rongai",
                "sms_alert": "Sikika: Pesa za maendeleo ya kata Rongai zitajenga barabara ndogo, mifereji na maji. Piga *384# kutoa maoni.",
                "civic_education": "Kila kata hupewa pesa za maendeleo. Rongai inaelekeza kwenye barabara za mtaa, mifereji na maji.",
                "data_summary": "Sekta: Miundombinu ya kata. Chanzo: Ada ya Barabara. Hali: Bajeti inayopendekezwa.",
            },
            "en": {
                "project_name": "Rongai ward infrastructure",
                "sms_alert": "Sikika: Rongai ward development funds local roads, drainage & water points. Dial *384# to comment.",
                "civic_education": "Each ward gets development funds. Rongai's go to local roads, drainage and small water points.",
                "data_summary": "Sector: Ward infrastructure. Source: Roads Maintenance Levy. Status: Proposed budget.",
            },
        },
    },
    {
        "sub": "Bahati", "name_en": "Constitution (Amendment) Bill 2026", "status": "Bill",
        "raw": ("The Constitution of Kenya (Amendment) Bill, 2026 (Senate Bill No. 7 of "
                "2026). Proposes constitutional and electoral changes, including a rule "
                "barring former county governors from elective office within five years "
                "of leaving office. Open for public views."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Marekebisho ya Katiba 2026",
                "sms_alert": "Sikika: Mswada wa kubadilisha Katiba unazuia magavana wa zamani kugombea kwa miaka mitano. Piga *384# kutoa maoni.",
                "civic_education": "Mswada huu unabadilisha sheria za uchaguzi, ikiwemo kuzuia gavana wa zamani kugombea kwa miaka mitano baada ya kuondoka.",
                "data_summary": "Mswada wa Katiba 2026 (Seneti Na. 7). Unagusa: sheria za uchaguzi. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "Constitution (Amendment) Bill 2026",
                "sms_alert": "Sikika: A bill to amend the Constitution bars ex-governors from office for 5 years. Dial *384# to comment.",
                "civic_education": "This bill changes electoral rules, including barring a former governor from running for 5 years after leaving office.",
                "data_summary": "Constitution Bill 2026 (Senate No.7). Affects: electoral rules. Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Nakuru Town West", "name_en": "County Wards (Equitable Development) Bill 2024", "status": "Bill",
        "raw": ("The County Wards (Equitable Development) Bill, 2024 (Senate Bill No. 20 "
                "of 2024). Requires county development funds to be shared fairly across "
                "all wards so no area is left behind."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Maendeleo Sawa ya Kata 2024",
                "sms_alert": "Sikika: Mswada wa Maendeleo Sawa ya Kata unahakikisha kila kata inapata fedha za haki. Piga *384# kutoa maoni.",
                "civic_education": "Mswada huu unahakikisha kila kata inapata sehemu ya haki ya fedha za maendeleo ili maeneo yasisahaulike.",
                "data_summary": "Mswada wa Kata 2024 (Seneti Na.20). Unagusa: mgawanyo wa fedha za maendeleo. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "County Wards (Equitable Development) Bill 2024",
                "sms_alert": "Sikika: The County Wards Equitable Development Bill ensures every ward gets a fair share of funds. Dial *384# to comment.",
                "civic_education": "This bill makes sure every ward gets a fair share of development funds so no area is left behind.",
                "data_summary": "Wards Bill 2024 (Senate No.20). Affects: sharing of development funds. Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Kuresoi North", "name_en": "Digital Agricultural Information Bill 2026", "status": "Bill",
        "raw": ("The Digital Agricultural Information Bill, 2026. Establishes a farmer "
                "registry and the Kenya Agriculture Digital Information Centre (KADIC) "
                "to strengthen farming data systems."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Taarifa za Kilimo Kidijitali 2026",
                "sms_alert": "Sikika: Mswada mpya unataka kusajili wakulima na kuweka taarifa za kilimo kidijitali. Piga *384# kutoa maoni.",
                "civic_education": "Mswada huu unaanzisha mfumo wa kusajili wakulima na kuhifadhi taarifa za kilimo ili kupanga msaada vyema.",
                "data_summary": "Mswada wa Taarifa za Kilimo 2026. Unaanzisha: usajili wa wakulima (KADIC). Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "Digital Agricultural Information Bill 2026",
                "sms_alert": "Sikika: A new bill registers farmers and stores farm data digitally. Dial *384# to comment.",
                "civic_education": "This bill sets up a system to register farmers and store farming data so support can be planned better.",
                "data_summary": "Digital Agri Info Bill 2026. Creates: farmer registry (KADIC). Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Kuresoi South", "name_en": "Livestock Protection & Sustainability Bill 2024", "status": "Bill",
        "raw": ("The Livestock Protection and Sustainability Bill, 2024 (Senate Bill No. "
                "32 of 2024). Protects livestock and curbs theft and disease to help "
                "herders and dairy farmers."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Ulinzi wa Mifugo 2024",
                "sms_alert": "Sikika: Mswada wa Ulinzi wa Mifugo unalinda ng'ombe na kudhibiti wizi na magonjwa. Piga *384# kutoa maoni.",
                "civic_education": "Mswada huu unalinda mifugo na kudhibiti wizi na magonjwa ili wafugaji na wakulima wa maziwa wafaidike.",
                "data_summary": "Mswada wa Mifugo 2024 (Seneti Na.32). Unagusa: ulinzi wa mifugo, magonjwa. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "Livestock Protection & Sustainability Bill 2024",
                "sms_alert": "Sikika: The Livestock Protection Bill guards cattle and curbs theft & disease. Dial *384# to comment.",
                "civic_education": "This bill protects livestock and controls theft and disease so herders and dairy farmers benefit.",
                "data_summary": "Livestock Bill 2024 (Senate No.32). Affects: livestock protection, disease. Status: Bill (public input).",
            },
        },
    },
    {
        "sub": "Subukia", "name_en": "Agriculture Produce (Minimum Returns) Bill 2025", "status": "Bill",
        "raw": ("The Agriculture Produce (Minimum Guaranteed Returns) Bill, 2025 (Senate "
                "Bill No. 17 of 2025). Would set a guaranteed minimum price for produce "
                "so farmers are not forced to sell at a loss."),
        "t": {
            "sw": {
                "project_name": "Mswada wa Bei ya Chini ya Mazao 2025",
                "sms_alert": "Sikika: Mswada unataka kuweka bei ya chini ya uhakika kwa mazao ya wakulima. Piga *384# kutoa maoni.",
                "civic_education": "Mswada huu unaweka bei ya chini ya uhakika kwa mazao ili wakulima wasilazimike kuuza kwa hasara.",
                "data_summary": "Mswada wa Bei ya Mazao 2025 (Seneti Na.17). Unagusa: bei ya chini ya mazao. Hali: Mswada (maoni ya umma).",
            },
            "en": {
                "project_name": "Agriculture Produce (Minimum Returns) Bill 2025",
                "sms_alert": "Sikika: A bill would set a guaranteed minimum price for farmers' produce. Dial *384# to comment.",
                "civic_education": "This bill sets a guaranteed minimum price for produce so farmers don't have to sell at a loss.",
                "data_summary": "Produce Returns Bill 2025 (Senate No.17). Affects: minimum crop prices. Status: Bill (public input).",
            },
        },
    },
]


def seed_all() -> None:
    store.init_db()
    seeded = []
    for p in PROJECTS:
        pid = store.get_or_create_project(
            ward=p["sub"], name_en=p["name_en"], raw_text=p["raw"],
            pdf_path=p.get("pdf"), status=p["status"],
        )
        for lang, t in p["t"].items():
            store.upsert_translation(pid, lang, **t)
        seeded.append((pid, p["sub"], p["name_en"]))

    print("Seeded projects (idempotent):")
    for pid, sub, name in seeded:
        print(f"  #{pid:>2}  {sub:<18} {name}")

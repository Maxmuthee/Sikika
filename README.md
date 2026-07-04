# Sikika

> Built during the **Democracy & AI Hackathon** — July 4th, 2026
> Hosted by **Mozilla Foundation** & **KamiLimu**

---

## Team

| Name | Role | GitHub |
|------|------|--------|
| Esther Oyoo | Lead Developer | @aah3sta |
| Maxwell Gitahi | Lead Developer | @Maxmuthee |

**Team Name:** A-Hacks
**University:** Kenyatta University, USIU - Africa

---

## Problem & User

### Problem Statement

<!-- Describe the core problem in 2-3 sentences. Keep it sharp. -->

> Over 510,000 rural residents aged 35+ in Nakuru County are systematically cut off from county government accountability and public participation processes, as proven by the county's low score of 25 out of 100 on the 2024 County Budget Transparency Survey. This exclusion happens because official accountability documents are published as complex English PDFs online, while over half of rural Kenyans lack the smartphones, internet, or English literacy required to access them. Existing tools like the Jihusishe app fail this demographic by ignoring the deep urban-rural digital divide, leaving a critical need for an offline, local-language channel built for basic feature phones.

### Target User

<!-- Who specifically are you building for? Be as concrete as possible. -->

| Dimension | Detail |
|-----------|--------|
| **Primary user** | A 45-year-old smallholder farmer in rural Nakuru who relies entirely on a basic feature phone. |
| **Tech comfort** | Comfortable with USSD menus and basic SMS; completely offline with no smartphone, web browser, or email access. |
| **Language** | Swahili, Kikuyu - No English literacy |
| **Current workflow** | Hears about local county development plans late via word-of-mouth or local radio, travels miles to centralized barazas to air their views. |

### The Specific Gap

<!-- What exists today? What's the precise gap your solution fills? -->

1. **What's already there:** TISA's Jihusishe digital platform for tracking county data and reporting governance issues.
2. **Why it falls short:** Runs only in English on smartphone apps and web browsers, requiring active internet bundles and text-heavy interactions.
3. **The gap we fill:** Offline, micro-localized Swahili and Kikuyu bill summaries delivered via USSD menus and SMS — no smartphones, internet, or English literacy required.

### Why It Matters

<!-- Connect this to democratic participation. -->

> When rural citizens are locked out of public participation, county governments pass budgets and bills without real community oversight, rendering local voices invisible. Closing this accessibility gap restores a fundamental democratic mechanism: older, rural right-holders can securely review localized county decisions from their homes, log informed feedback and legally hold local duty-bearers accountable.

---

## Run Instructions

### Prerequisites

- **Python 3.10+** (developed on 3.12)
- A **DeepSeek API key** (the AI runs on DeepSeek's OpenAI-compatible API)
- That's all — SQLite ships with Python; no Node, Docker, or database server needed.

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Maxmuthee/Sikika.git
cd Sikika

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the AI key
cp .env.example .env             # then set SIKIKA_API_KEY to your DeepSeek key

# 5. Create + seed the database (Nakuru sub-counties, wards, budgets, 2026 bills)
python scripts/init_db.py

# 6. (Optional) Pre-generate real AI mother-tongue content for every item
python scripts/ingest.py         # needs the API key; otherwise hand-written fallbacks are used

# 7. Run the server
uvicorn app.main:app --reload
```

Then open:
- **http://localhost:8000/simulator** — feature-phone simulator (USSD dialer + SMS chat), drives the app offline
- **http://localhost:8000/** — county participation dashboard (votes + AI-aggregated brief)

---

## 📁 Project Structure

```
.
├── app/                          ← FastAPI backend
│   ├── main.py                   ← API: /ussd, /sms, /county, /admin/notify, dashboard
│   ├── ussd.py                   ← USSD state machine (signup → browse → vote), paginated & localized
│   ├── store.py                  ← SQLite persistence
│   ├── hashing.py                ← SHA-256 anonymisation of phone & national ID
│   ├── notify.py                 ← outbound SMS alerts to registered citizens
│   ├── wards.py                  ← Nakuru sub-counties & their wards
│   └── static/
│       ├── simulator.html        ← feature-phone simulator (USSD + SMS)
│       └── dashboard.html        ← county participation dashboard
├── ai/                           ← AI core (DeepSeek via the OpenAI SDK)
│   ├── core.py                   ← simplify · translate · aggregate · answer
│   └── prompts.py                ← prompts + language config (sw / ki / en)
├── data/
│   ├── seed.py                   ← real Nakuru budget items & 2026 bills
│   └── explosives_bill_2026.pdf  ← a real tabled bill, simplified on demand
├── scripts/
│   ├── init_db.py                ← create + seed the database
│   ├── ingest.py                 ← pre-generate AI mother-tongue content
│   └── notify.py                 ← send SMS alerts for a project
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

---

## Approach & Architecture

Sikika meets rural citizens on the channel they already have — a **basic feature phone** — over **USSD** (interactive menus) and **SMS** (alerts + a conversational AI assistant). No smartphone, internet, or English needed; the phone only needs a cellular signal. The AI runs entirely **server-side**, so the citizen stays offline.

**What the AI does (four jobs):**
- **Simplify** — turns long English county budgets and bills (including real PDFs) into ≤160-character **Swahili, Kikuyu, or English** screens and SMS alerts.
- **Answer** — citizens text follow-up questions and Sikika replies in their own language, **grounded only in the real bill facts**, with conversation memory.
- **Translate & scrub** — citizen feedback is translated to English and **PII-redacted** before storage.
- **Aggregate** — feedback is rolled into a **county brief** that makes participation visible, closing the loop (Nakuru scored 25/100 on acting on public input).

**Privacy:** phone numbers and national IDs are stored only as **SHA-256 hashes**. The ID enforces one-person-one-vote and is never shown or stored in the clear.

**Stack:** FastAPI · SQLite · **DeepSeek** (`deepseek-chat`, via the OpenAI-compatible API) · pypdf · USSD/SMS in the **Africa's Talking** format (a built-in simulator drives it offline for demos).

```
                       Cellular network (no internet needed)
  [Feature phone] ──USSD / SMS──►  [Africa's Talking]  ──HTTPS──►  [ Sikika · FastAPI ]
        ▲                                                              │        │
        └───────────── SMS / USSD reply ◄──────────────────────────────┘        │
                                                          ┌─────────────────────┴───────────┐
                                                          ▼                                  ▼
                                                 [ SQLite ]                          [ DeepSeek LLM ]
                                          votes · feedback · registrations      simplify · translate ·
                                                 (all hashed)                    aggregate · answer

  [County officials] ──►  [ Dashboard ]  ◄──  live vote tallies + AI-aggregated citizen brief
```

---

## License

MIT © Sikika, 2026

---

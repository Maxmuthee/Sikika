# Sikika — Technical Documentation

> Offline civic participation for rural Nakuru County, delivered to basic feature
> phones over USSD and SMS, in Swahili, Kikuyu, and English. The AI runs
> server-side; the citizen needs only a cellular signal — no smartphone, no
> internet, no English.

*Democracy & AI Hackathon — Mozilla Foundation & KamiLimu. Team A-Hacks.*

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Setup & Installation](#5-setup--installation)
6. [Configuration (Environment Variables)](#6-configuration-environment-variables)
7. [Running the Project](#7-running-the-project)
8. [The USSD Channel](#8-the-ussd-channel)
9. [The SMS Channel](#9-the-sms-channel)
10. [The AI Layer](#10-the-ai-layer)
11. [Data Model](#11-data-model)
12. [Privacy & Security](#12-privacy--security)
13. [API Reference](#13-api-reference)
14. [The Local Simulator](#14-the-local-simulator)
15. [The County Dashboard](#15-the-county-dashboard)
16. [Scripts](#16-scripts)
17. [Africa's Talking Integration](#17-africas-talking-integration)
18. [Deployment & Production](#18-deployment--production)
19. [Costs](#19-costs)
20. [Roadmap](#20-roadmap)
21. [Troubleshooting](#21-troubleshooting)

---

## 1. Overview

Over **510,000 rural residents aged 35+** in Nakuru County are cut off from county
government accountability: budget and bill documents are 200-page English PDFs
online, while this demographic lacks smartphones, internet, or English literacy.
Nakuru scored **25/100** on the 2024 County Budget Transparency Survey for acting
on public input.

**Sikika** closes that gap on the phone people already own. It:

- **Simplifies** county budgets and national bills (including real PDFs) into
  short **Swahili / Kikuyu / English** messages.
- Delivers them over **USSD** (interactive menus) and **SMS** (alerts + a
  conversational AI assistant citizens can text questions to, offline).
- Lets citizens **register once** (national ID, sub-county, ward), **vote**
  (one person, one vote), and **give feedback**.
- Aggregates that feedback into a **county-facing brief**, making participation
  visible — the loop Nakuru's 25/100 score is missing.

The name **"Sikika"** is Swahili for *"to be heard."*

---

## 2. Architecture & Data Flow

The AI runs entirely server-side, so the citizen stays offline. SMS and USSD ride
the **cellular network** (not the internet); only the phone's signal is needed.

```
                    Cellular network (no internet needed)
 [Feature phone] ──USSD / SMS──► [ Africa's Talking ] ──HTTPS──► [ Sikika · FastAPI ]
       ▲                                                            │          │
       └───────────── SMS / USSD reply ◄────────────────────────────┘          │
                                                       ┌───────────────────────┴─────────────┐
                                                       ▼                                      ▼
                                               [ SQLite ]                            [ DeepSeek LLM ]
                                       votes · feedback · registrations         simplify · translate ·
                                       · SMS thread  (phone & ID hashed)         aggregate · answer

 [County officials] ──► [ Dashboard ]  ◄── live vote tallies + AI-aggregated citizen brief
```

**Key design property:** the `/ussd` and `/sms` endpoints speak Africa's Talking's
exact wire format. The **local simulator** and the **real AT gateway** are
therefore interchangeable from the server's perspective — the only difference is
who delivers the message to the handset. Going live is a configuration change,
not a code change.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Backend / API | **FastAPI** (Python), Uvicorn |
| Storage | **SQLite** (Python standard library; swap to PostgreSQL for production) |
| AI / LLM | **DeepSeek** (`deepseek-chat`) via the **OpenAI SDK** (`base_url = https://api.deepseek.com`) |
| PDF extraction | **pypdf** (local text extraction; DeepSeek has no PDF input) |
| Telco channel | **USSD + SMS** in the **Africa's Talking** format (sandbox for the demo) |
| Anonymisation | **SHA-256** (phone & national ID) |
| Frontend | Self-contained HTML (feature-phone simulator + county dashboard) |

---

## 4. Project Structure

```
.
├── app/                          FastAPI backend
│   ├── main.py                   API endpoints (/ussd, /sms, /county, /admin, dashboard)
│   ├── ussd.py                   USSD state machine (signup → browse → vote)
│   ├── store.py                  SQLite persistence (all tables + queries)
│   ├── hashing.py                SHA-256 anonymisation (phone, ID, vote nullifier)
│   ├── notify.py                 outbound SMS (Africa's Talking / stub) + notifications
│   ├── wards.py                  Nakuru sub-counties → wards
│   └── static/
│       ├── simulator.html        feature-phone simulator (USSD + SMS)
│       └── dashboard.html        county participation dashboard
├── ai/                           AI core (DeepSeek via the OpenAI SDK)
│   ├── core.py                   simplify · simplify_pdf · translate · aggregate · answer
│   └── prompts.py                prompts + language config (sw / ki / en)
├── data/
│   ├── seed.py                   real Nakuru budget items & 2026 bills
│   └── explosives_bill_2026.pdf  a real tabled bill, simplified on demand
├── scripts/
│   ├── init_db.py                create + seed the database
│   ├── ingest.py                 pre-generate AI mother-tongue content
│   ├── notify.py                 send SMS alerts for a project
│   └── test_ai_core.py           smoke-test the AI functions
├── requirements.txt
├── .env.example
├── README.md
└── DOCUMENTATION.md              ← this file
```

---

## 5. Setup & Installation

**Prerequisites:** Python 3.10+ (developed on 3.12) and a **DeepSeek API key**.
SQLite ships with Python — no database server needed.

```bash
git clone https://github.com/Maxmuthee/Sikika.git
cd Sikika

python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env              # then set SIKIKA_API_KEY (see §6)

python scripts/init_db.py         # create + seed the database
python scripts/ingest.py          # (optional) generate real AI content — needs the key
```

---

## 6. Configuration (Environment Variables)

Set these in `.env` (gitignored; never commit it).

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SIKIKA_API_KEY` | Yes (for AI) | — | DeepSeek API key |
| `SIKIKA_BASE_URL` | No | `https://api.deepseek.com` | LLM base URL (OpenAI-compatible) |
| `SIKIKA_MODEL` | No | `deepseek-chat` | LLM model |
| `SIKIKA_HASH_SALT` | Prod | `sikika-local-dev-salt` | Salt for phone/ID hashing — **set a strong secret in production** |
| `SIKIKA_DB` | No | `sikika.db` | SQLite file path |
| `AT_USERNAME` | For real SMS | — | Africa's Talking username (`sandbox` in sandbox) |
| `AT_API_KEY` | For real SMS | — | Africa's Talking API key |
| `AT_SENDER` | No | — | SMS sender ID / short code (not used in sandbox) |

Without `AT_*`, outbound SMS is **logged** rather than sent — the local simulator
still works fully. Without `SIKIKA_API_KEY`, the USSD/SMS flows still run on
hand-written fallback content, and the SMS assistant returns a graceful "try again"
message.

---

## 7. Running the Project

```bash
uvicorn app.main:app --reload
```

Then open:

- **http://localhost:8000/simulator** — feature-phone simulator (USSD dialer + SMS chat)
- **http://localhost:8000/** — county participation dashboard
- **http://localhost:8000/health** — liveness check

---

## 8. The USSD Channel

USSD is a **stateless** protocol: Africa's Talking posts an accumulating `text`
field (choices joined by `*`, e.g. `1*7*1*3`). Sikika derives all state from that
string — no server-side session store. Every reply begins with:

- `CON …` — keep the session open, expect more input
- `END …` — final screen, close the session

Implemented in [app/ussd.py](app/ussd.py). Entry point `handle(phone_number, text)`
routes on whether the caller's phone is **already registered**.

### 8.1 Navigation (all menus)

| Input | Action |
|---|---|
| `0` | Back one step |
| `00` | Main menu (the sub-county list) |
| `99` | Next page (on paginated lists) |

Menus are **paginated** (4 items/screen) to stay under the ~182-character USSD
limit, with **continuous numbering** across pages (page 2 shows 5–8, not 1–4), so a
number is a global choice regardless of page.

### 8.2 First-time users — one-time signup

An unregistered phone is walked through registration automatically (no special
code needed — just dial):

```
Dial *384*7030#
 → Choose language:  1 Kiswahili · 2 Gikuyu · 3 English
 → Enter national ID number
 → Choose sub-county   (paginated, all 11 Nakuru sub-counties)
 → Choose ward          (paginated, wards of that sub-county)
 → "Umesajiliwa!"  (registered; ends the session)
```

The ID is stored **only as a SHA-256 hash** (`id_hash`, UNIQUE) — one registration
per person, even from a different phone. The phone number is retained **only** for
SMS delivery. See §12.

### 8.3 Registered users — browse & participate

```
Dial *384*7030#
 → Choose language
 → Choose sub-county
 → Choose a project / bill
 → Action menu:
      1. What is this project/bill?   (civic education, mother tongue)
      2. View budget / details        (amount, source, status)
      3. Vote                         (see 8.4)
      4. Listen by voice              (IVR callback note)
```

Screens 1, 2, and 4 are informational and navigable (back/main). Their content
comes from the **AI-simplified `translations`** table (see §10).

### 8.4 Voting — one person, one vote

Voting **re-requests the national ID** and verifies it against the caller's
registration before recording:

```
3. Vote
 → "Enter your ID number to vote:"
 → (verify hash matches this phone's registration; reject otherwise)
 → (if already voted on this item → "You have already voted")
 → 1 Support · 2 Oppose
 → recorded · "Thank you, your vote has been counted"
```

The vote is stored under a **vote nullifier** (a separate hash of the ID, distinct
from the registration hash — see §12), so:

- A person can vote **only once per project** (even across phones).
- Votes are **not linkable** to a registration/phone by a plain database query.

### 8.5 Sub-counties & wards

All 11 Nakuru sub-counties (Nakuru Town East/West, Naivasha, Gilgil, Kuresoi
North/South, Molo, Njoro, Rongai, Subukia, Bahati) and their wards are defined in
[app/wards.py](app/wards.py). Every sub-county is seeded with at least one project
or bill.

---

## 9. The SMS Channel

Implemented at `POST /sms` in [app/main.py](app/main.py). SMS gives offline
citizens **two-way, conversational** access to Sikika — the AI runs server-side,
so the citizen only needs a normal SMS.

### 9.1 Default — AI Q&A with memory

Any inbound text is treated as a **question**. Sikika answers with
`answer_sms()` ([ai/core.py](ai/core.py)):

- In the **same language** the citizen wrote in.
- **Grounded only in the real project/bill facts** (a context sheet built from the
  `translations` table) — it will not invent figures.
- **Concise** (≈2 SMS).
- With **conversation memory** — recent thread turns are fed back to the model, so
  follow-ups ("When is the meeting?") resolve correctly.

### 9.2 Commands

| Command | Effect |
|---|---|
| `SIKIZA <id>` / `LISTEN <id>` | Voice/IVR callback — "we will call you to read it aloud" (simulated; real IVR is future work) |
| `MAONI <text>` / `FEEDBACK <text>` | Submit feedback → translated to English, PII-scrubbed, tagged, stored |
| `MSAADA` / `HELP` | Help text |

### 9.3 Notifications (outbound)

When a new item is published for a sub-county, every citizen registered there
receives the **AI-simplified SMS alert in their language**
([app/notify.py](app/notify.py) → `notify_new_project`). Notifications are also
recorded in the citizen's SMS thread so they appear in the simulator.

Triggers: `POST /admin/notify/{project_id}`, or `python scripts/notify.py <id>`.

---

## 10. The AI Layer

All LLM calls live in [ai/core.py](ai/core.py), using the **OpenAI SDK pointed at
DeepSeek**. Prompts and the language table are in [ai/prompts.py](ai/prompts.py).
Language is a single code threaded everywhere: `sw`, `ki`, `en`.

### 10.1 The functions

| Function | Purpose | Output |
|---|---|---|
| `simplify_budget(raw_text, lang)` | Budget/bill text → feature-phone content | `BudgetSummary` |
| `simplify_pdf(pdf_path, lang)` | Extract PDF text (pypdf) → simplify | `BudgetSummary` |
| `translate_feedback(text, source_lang)` | Feedback → English + PII-scrub + tag | `FeedbackAnalysis` |
| `aggregate_feedback(items)` | Many feedback items → county brief | `CountyBrief` |
| `answer_sms(question, history, context, lang_hint)` | Conversational SMS Q&A | `str` |

### 10.2 Structured output

DeepSeek is OpenAI-compatible but does **not** support Anthropic-style schema
outputs. Sikika uses DeepSeek's **JSON mode** (`response_format={"type":
"json_object"}`) with an explicit field instruction, then validates into a Pydantic
model (`BudgetSummary`, `FeedbackAnalysis`, `CountyBrief`). Callers always receive
a validated object.

### 10.3 The Pydantic schemas

- **`BudgetSummary`**: `project_name`, `sms_alert` (≤160), `civic_education` (≤130),
  `data_summary` (≤130). The three short fields drive USSD/SMS screens; the ingest
  script also caps them as a safety net.
- **`FeedbackAnalysis`**: `english`, `sentiment` (support/oppose/mixed/unclear),
  `theme`.
- **`CountyBrief`**: `total`, `support`, `oppose`, `headline`, `top_concerns[]`.

### 10.4 Language & money rules

Prompts instruct the model to write **money in words** in Swahili/Kikuyu
("shilingi milioni tano", never "KSh 5M"), use a 6th-grade reading level, never
invent figures, and stay neutral. Kikuyu is low-resource — outputs should be
reviewed by a native speaker before production broadcast (see §20).

### 10.5 Ahead-of-time ingestion

USSD sessions are too short (~90s) to call an LLM live. `scripts/ingest.py`
pre-generates all translations when a project is added; USSD then only **reads**
the `translations` table.

---

## 11. Data Model

SQLite, defined in [app/store.py](app/store.py). `ward` on `projects` holds the
sub-county name.

| Table | Key columns | Notes |
|---|---|---|
| `projects` | `id`, `ward`, `name_en`, `raw_text`, `pdf_path`, `status` | A budget item or bill |
| `translations` | (`project_id`, `lang`), `project_name`, `sms_alert`, `civic_education`, `data_summary` | AI-simplified content per language |
| `profiles` | `phone_hash` (PK), `lang`, `sub_county`, `ward` | Lightweight browse profile |
| `registrations` | `phone_hash` (PK), `phone_number`, `id_hash` (UNIQUE), `lang`, `sub_county`, `ward` | One-time signup; `id_hash` enforces one-per-person |
| `votes` | (`project_id`, `voter_hash`), `choice` | One vote per person per project; `voter_hash` = vote nullifier |
| `feedback` | `id`, `project_id`, `phone_hash`, `lang`, `english`, `sentiment`, `theme` | Translated, PII-scrubbed feedback |
| `sms` | `id`, `phone_hash`, `phone_number`, `direction` (`in`/`out`), `body` | Two-way SMS thread |

---

## 12. Privacy & Security

Sikika's promise: **verification data is hashed, anonymised, and never shared.**
Implemented in [app/hashing.py](app/hashing.py) (SHA-256, salted with
`SIKIKA_HASH_SALT`).

| Data | Treatment |
|---|---|
| **Phone number** | Hashed (`hash_phone`) for all anonymous attribution (profiles, feedback, SMS thread key). The **raw number is retained only in `registrations`**, solely to deliver SMS alerts. |
| **National ID** | **Never stored raw.** `hash_id` (registration) enforces one-person-one-registration; the ID is only ever compared as a hash, never displayed. |
| **Vote identity** | `vote_nullifier` — a *separate* hash of the ID (different domain prefix), so a vote's `voter_hash` ≠ the registration's `id_hash`. Votes cannot be joined back to a registration/phone by a plain query. |
| **Feedback PII** | Names/phones/IDs in free-text feedback are redacted to `[NAME]`/`[PHONE]` by the AI **before storage**. |
| **On the site** | No endpoint or page exposes any raw ID or hash — the dashboard shows only aggregate tallies and the AI brief. |

**Honest limits (state these in any pitch):**
- Uniqueness ≠ authenticity. Sikika enforces one-ID-one-vote but cannot confirm an
  ID truly belongs to the caller without an **IPRS/Huduma** integration.
- Vote↔registration unlinkability holds against casual DB access; it is not
  cryptographically unbreakable (an operator with the salt could brute-force the
  ID space). True ballot secrecy needs blind signatures — future work.

---

## 13. API Reference

Base URL in development: `http://localhost:8000`.

| Method & Path | Purpose | Input | Output |
|---|---|---|---|
| `GET /health` | Liveness | — | `{status, service}` |
| `GET /` | County dashboard | — | HTML |
| `GET /simulator` | Feature-phone simulator | — | HTML |
| `POST /ussd` | USSD state machine | form: `phoneNumber`, `text`, `sessionId`, `serviceCode` | `CON …` / `END …` (text) |
| `POST /sms` | Inbound SMS (AI Q&A / commands) | form: `from`, `text`, `to` | `{reply}` |
| `GET /api/sms?phone=` | SMS thread for a phone | query: `phone` | `{messages[]}` |
| `POST /api/demo/notify?phone=&project_id=` | Push an alert to one phone (demo) | query | `{sent}` |
| `POST /admin/notify/{project_id}` | Alert all registrants in a sub-county | path | `{project, sub_county, recipients, sent[]}` |
| `GET /api/projects` | Projects + live tallies + feedback counts | — | `{projects[]}` |
| `GET /county/{project_id}/brief` | Votes + AI-aggregated brief | path | `{project, ward, votes, feedback_count, brief?}` |
| `GET /api/stats` | Registration count | — | `{registrations}` |

The `/ussd` and `/sms` request shapes match Africa's Talking exactly.

---

## 14. The Local Simulator

[app/static/simulator.html](app/static/simulator.html), served at `/simulator`. A
browser page styled as a feature phone, with **USSD** and **Messages** tabs. It
**only fakes the telco** — every request hits the real `/ussd` and `/sms`
endpoints with the real AI and database.

- **USSD tab:** keeps the session client-side, accumulates choices into the
  `*`-joined `text`, and POSTs to `/ussd` with AT's exact fields; renders the
  `CON`/`END` reply as the phone screen. Full support for navigation (`0`/`00`/`99`).
- **Messages tab:** an SMS chat thread; typing POSTs to `/sms`, the AI reply is
  shown; a **"new bill alert"** button injects a notification via `/api/demo/notify`.
- **SIM selector:** switch between preset phone numbers to demo multiple citizens
  (e.g. to grow a vote tally, or register several users).

Because it sends the same request shape AT would, the simulator is a faithful
stand-in — the demo shown is the real production code path, minus the paid
delivery. Works fully **offline** (no internet, no ngrok, no AT account).

---

## 15. The County Dashboard

[app/static/dashboard.html](app/static/dashboard.html), served at `/`. The
official-facing view that makes participation visible:

- A project list with live vote counts and feedback counts.
- Per project: status, **stat tiles** (total/support/oppose/feedback), an
  accessible support-vs-oppose bar, and the **AI-aggregated brief** with ranked
  top concerns.
- Auto-refreshes; reads `GET /api/projects` and `GET /county/{id}/brief`.

This is the artifact that closes Nakuru's 25/100 loop: citizen input arrives as a
report officials can act on.

---

## 16. Scripts

| Script | Purpose |
|---|---|
| `python scripts/init_db.py` | Create the SQLite schema and seed projects, bills, wards. Idempotent. No API key needed. |
| `python scripts/ingest.py` | Pre-generate AI mother-tongue content (all projects × sw/ki/en; PDFs via pypdf). **Needs the API key.** Caps USSD fields for safety. |
| `python scripts/notify.py <project_id>` | Send the SMS alert for a project to all registrants in its sub-county. |
| `python scripts/test_ai_core.py` | Smoke-test the AI functions end to end (needs the key). |

---

## 17. Africa's Talking Integration

Sikika's `/ussd` and `/sms` already speak AT's format, so integration is
configuration, not code. Outbound SMS is env-gated in
[app/notify.py](app/notify.py): with `AT_USERNAME` + `AT_API_KEY` set, it sends via
the `africastalking` SDK; otherwise it logs (local simulator still works).

### 17.1 Sandbox (free, no KYC — for testing / demo)

1. Create a free Africa's Talking account → use the **sandbox** app; copy its API key.
2. Expose the server publicly: `ngrok http 8000`.
3. In the sandbox dashboard:
   - **USSD → Create Channel**, set callback → `https://<ngrok>/ussd`.
   - **Inbound SMS** callback → `https://<ngrok>/sms`.
4. Set `AT_USERNAME=sandbox` and `AT_API_KEY=<sandbox key>` in `.env`.
5. Use AT's **Launch Simulator** to dial the code / send SMS.

### 17.2 Production (real phones)

USSD shortcodes in Kenya are gated by the mobile operators and the Communications
Authority — this requires business KYC (a registered **Business Name** via
eCitizen, ~KSh 950, satisfies it) and takes weeks. Steps: take the AT account
**live** (KYC) → apply for a **shared USSD shortcode** + **alphanumeric sender ID**
→ set the callback to a **deployed** HTTPS URL (not ngrok) → swap the live
username + key into the server env. **No application code changes.**

---

## 18. Deployment & Production

To move off a laptop:

1. **Database:** swap SQLite → **PostgreSQL** (only [app/store.py](app/store.py)
   changes). Set `SIKIKA_DB`/connection via env.
2. **Host:** deploy the FastAPI app (Render, Railway, Fly.io, or a VPS) with HTTPS
   and a stable public URL for the AT callback.
3. **Secrets:** set `SIKIKA_HASH_SALT` to a strong secret; store keys in the host's
   secret manager, not the repo.
4. **Content pipeline:** add an editor step to **review AI simplifications before
   broadcast** — civic accuracy matters. Keep `ingest.py` for generation.
5. **Compliance:** register as a **data controller with the ODPC** (Kenya Data
   Protection Act 2019); publish a privacy policy; capture consent at signup.

---

## 19. Costs

| Item | Notes |
|---|---|
| **USSD shortcode** (shared) | Setup + monthly rental per network — the dominant recurring cost |
| **Per USSD session** | Small per-session charge (absorbed to keep it free to the citizen) |
| **SMS** | Per outbound message + sender-ID monthly |
| **DeepSeek tokens** | Very cheap — fractions of a cent per interaction; negligible vs telco |
| **Hosting + Postgres** | ~$25–100/month |
| **Business Name registration** | ~KSh 950 (eCitizen) — clears KYC for AT + shortcode + sender ID |
| **ODPC data-controller registration** | Annual fee |
| **Editor/curator** | Human review of budgets & AI output — second-biggest real cost |

Telco + people dominate; servers and AI are the cheap part.

---

## 20. Roadmap

- **IVR "listen" callback:** real outbound voice — TTS for Swahili/English, and for
  low-resource **Kikuyu**, pre-recorded human clips (best) or Meta **MMS** TTS.
- **Kikuyu text quality:** layer **NLLB-200** (open MT; includes Kikuyu) or a
  fine-tuned model, with **native-speaker review** before broadcast; evaluate with
  the **Kencorpus** dataset.
- **Real ID verification:** IPRS/Huduma integration for authenticity (currently
  uniqueness only).
- **Toll-free delivery:** reverse-billed shortcode so SMS/USSD is free to citizens.
- **Content ingestion:** automated scraping of county/Parliament budget & bill
  documents, with editorial review.

---

## 21. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| SMS assistant replies "I can't answer right now" | No/invalid `SIKIKA_API_KEY`, or no network to DeepSeek. Set the key in `.env`. |
| USSD shows hand-written text, not AI content | `scripts/ingest.py` hasn't been run (or no key). Run it to populate `translations`. |
| `Form data requires "python-multipart"` | `pip install -r requirements.txt` (it's included). |
| Re-running `init_db.py` seems to change nothing | It's idempotent by design — it won't duplicate projects or wipe votes. |
| Outbound SMS only appears in logs | `AT_*` not set — expected in local mode. Set sandbox creds to actually send. |
| Windows console errors printing Kikuyu (`ũ`/`ĩ`) | Cosmetic console-encoding issue; data is stored correctly. `ingest.py` handles it. |
| Want a fresh demo (no registrations/votes) | Delete `sikika.db` and re-run `python scripts/init_db.py`. |
| `401 invalid x-api-key` from DeepSeek | Wrong key or base URL. Confirm `SIKIKA_API_KEY` and `SIKIKA_BASE_URL=https://api.deepseek.com`. |

---

*Built for the Democracy & AI Hackathon — Mozilla Foundation & KamiLimu.
Sikika — "to be heard."*

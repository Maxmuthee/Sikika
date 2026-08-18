"""USSD state machine (Africa's Talking format).

Two flows, chosen by whether the caller's phone is already registered:

  * NOT registered -> one-time SIGNUP wizard:
        language -> enter national ID -> sub-county -> ward -> save.
    The ID is stored only as a SHA-256 hash (enforces one registration per
    person). The phone number is retained only to deliver SMS alerts.

  * registered -> BROWSE: language -> sub-county -> project -> civic/data/vote.

AT posts a `text` field accumulating inputs joined by '*'. State is derived
from that string (stateless). Navigation on any menu:
  0 = back one step, 00 = main menu, 99 = next page (paged menus).
Replies start with CON (keep session open) or END (close session).
"""

from __future__ import annotations

import math

from . import store
from . import wards as W
from .hashing import hash_id, hash_phone, vote_nullifier
from .notify import deliver

LANG_BY_CHOICE = {"1": "sw", "2": "ki", "3": "en"}

SUBCOUNTIES = [
    "Nakuru Town East", "Nakuru Town West", "Naivasha", "Gilgil",
    "Kuresoi North", "Kuresoi South", "Molo", "Njoro",
    "Rongai", "Subukia", "Bahati",
]
WARDS = SUBCOUNTIES  # backward-compatible export (main.py iterates these)

# A bill is open for votes/SMS feedback ONLY while it is in the public-
# participation phase: "Proposed" (county items with forums scheduled/underway)
# and "Bill" (public input open). Once a bill moves past that stage — e.g.
# "Ongoing", "Enacted", "Assented" — the window closes and votes/feedback are
# rejected with an explicit message.
def participation_open(status: str) -> bool:
    return (status or "").strip().lower() in {"proposed", "bill"}

PAGE_SIZE = 4  # options per USSD screen (keeps each screen < 182 chars)

LANGUAGE_MENU = (
    "CON Karibu Sikika / Welcome\n"
    "1. Kiswahili\n"
    "2. Gikuyu\n"
    "3. English"
)

SIGNUP_LANGUAGE_MENU = (
    "CON Karibu Sikika. Jisajili mara moja / Register once.\n"
    "Chagua lugha / Choose language:\n"
    "1. Kiswahili\n"
    "2. Gikuyu\n"
    "3. English"
)

INVALID_BILINGUAL = "END Chaguo si sahihi. / Invalid choice."

LABELS = {
    "sw": {
        "ask_id": "Karibu! Weka nambari yako ya kitambulisho (ID):",
        "bad_id": "Nambari ya ID si sahihi. Bonyeza 0 uweke tena.",
        "pick_area": "Chagua eneo lako (kata ndogo):",
        "pick_ward": "Chagua kata (ward) yako:",
        "id_taken": "Kitambulisho hiki kimeshasajiliwa. Asante.",
        "registered": "Umesajiliwa! Utapokea arifa za miradi ya {ward}, {sub}. Piga *384*7030# kuona miradi.",
        "sms_registered": "Sikika: Umesajiliwa kwa {ward}, {sub}. Utapokea arifa za miradi mipya. Asante!",
        "sms_voted": "Sikika: Kura yako kuhusu '{project}' imepokelewa. Asante kwa kushiriki!",
        "page": "Ukurasa",
        "no_projects": "Hakuna miswada inayofanya kazi katika eneo hili kwa sasa. Asante.",
        "projects": "Miradi na miswada:",
        "welcome": "Karibu Sikika.",
        "menu_my_area": "1. Miradi ya {area}",
        "menu_other": "2. Maeneo mengine",
        "menu_profile": "3. Badilisha wasifu",
        "profile_menu": "Badilisha wasifu:",
        "change_lang": "1. Lugha",
        "change_area": "2. Eneo",
        "choose_lang": "Chagua lugha mpya:",
        "lang_changed": "Lugha imebadilishwa. Asante.",
        "area_changed": "Eneo limebadilishwa: {ward}, {sub}. Asante.",
        "menu": "Chagua kitendo:",
        "opt_about": "1. Kuhusu (maelezo na bajeti)",
        "opt_vote": "2. Piga kura",
        "opt_voice": "4. Sikiliza kwa sauti (utapigiwa)",
        "ask_vote_id": "Ili kupiga kura, weka nambari yako ya ID:",
        "vote_id_bad": "ID hailingani na usajili wako. Bonyeza 0 ujaribu tena.",
        "already_voted": "Umeshapiga kura kwa mradi huu. Asante.",
        "vote_prompt": "Kura yako:",
        "opt_support": "1. Naunga mkono",
        "opt_oppose": "2. Napinga",
        "vote_done": "Asante! Kura yako imehesabiwa.",
        "vote_closed": "Ushiriki kwa mswada huu umefungwa. Asante.",
        "voice_note": "Utapigiwa simu usikie kwa lugha yako. Asante.",
        "nav_next": "99. Zaidi",
        "nav_back": "0. Rudi nyuma",
        "nav_main": "00. Menyu kuu",
        "invalid": "Chaguo si sahihi. Jaribu tena.",
    },
    "ki": {
        "ask_id": "Wamukirwo! Ikira namba yaku ya kitambulisho (ID):",
        "bad_id": "Namba ya ID ti njega. Hinya 0 ucokererie.",
        "pick_area": "Thura gicigo giaku:",
        "pick_ward": "Thura ward yaku:",
        "id_taken": "Kitambulisho giki nikiandikithie. Ni wega.",
        "registered": "Niwandikithia! Niukwamukira uhoro wa miradi ya {ward}, {sub}. Hura *384*7030# kuona miradi.",
        "sms_registered": "Sikika: Niwandikithia {ward}, {sub}. Niukwamukira uhoro wa miradi mieru. Ni wega!",
        "sms_voted": "Sikika: Kura yaku igulyu ya '{project}' niyamukirwo. Ni wega ni gukorwo!",
        "page": "Ithangu",
        "no_projects": "Gutiri miradi gicigo giki riu. Ni wega.",
        "projects": "Miradi na miswada:",
        "welcome": "Wamukirwo Sikika.",
        "menu_my_area": "1. Miradi ya {area}",
        "menu_other": "2. Icigo iria ingi",
        "menu_profile": "3. Garura maundu maku",
        "profile_menu": "Garura:",
        "change_lang": "1. Ruthiomi",
        "change_area": "2. Gicigo",
        "choose_lang": "Thura ruthiomi rweru:",
        "lang_changed": "Ruthiomi niwagaruruo. Ni wega.",
        "area_changed": "Gicigo nikiagaruruo: {ward}, {sub}. Ni wega.",
        "menu": "Thura undu:",
        "opt_about": "1. Uhoro (maelezo na mbeca)",
        "opt_vote": "2. Hura kura",
        "opt_voice": "4. Thikiriria na mugambo (niukuhurwo)",
        "ask_vote_id": "Kuhura kura, ikira namba yaku ya ID:",
        "vote_id_bad": "ID ndiiganaine na kwiyandikithia gwaku. Hinya 0 ugerie.",
        "already_voted": "Niwahurite kura mradi-ini uyu. Ni wega.",
        "vote_prompt": "Kura yaku:",
        "opt_support": "1. Ninyitikaniirie",
        "opt_oppose": "2. Ndiitikaniirie",
        "vote_done": "Ni wega! Kura yaku niyatarwo.",
        "vote_closed": "Ukoru wa mswada uyu niugirirwo. Ni wega.",
        "voice_note": "Niukuhurwo thimu uigue na ruthiomi rwaku. Ni wega.",
        "nav_next": "99. Ingi",
        "nav_back": "0. Coka thutha",
        "nav_main": "00. Menyu nene",
        "invalid": "Uthuri ti wagiriire. Geria ringi.",
    },
    "en": {
        "ask_id": "Welcome! Enter your national ID number:",
        "bad_id": "Invalid ID number. Press 0 to re-enter.",
        "pick_area": "Choose your sub-county:",
        "pick_ward": "Choose your ward:",
        "id_taken": "This ID is already registered. Thank you.",
        "registered": "Registered! You'll get alerts for {ward}, {sub}. Dial *384*7030# to view projects.",
        "sms_registered": "Sikika: You are registered for {ward}, {sub}. You'll get alerts on new projects. Thank you!",
        "sms_voted": "Sikika: Your vote on '{project}' has been received. Thank you for taking part!",
        "page": "Page",
        "no_projects": "No active bills in this area right now. Thank you.",
        "projects": "Projects & bills:",
        "welcome": "Welcome to Sikika.",
        "menu_my_area": "1. Projects in {area}",
        "menu_other": "2. Other areas",
        "menu_profile": "3. Change my profile",
        "profile_menu": "Change profile:",
        "change_lang": "1. Language",
        "change_area": "2. Area",
        "choose_lang": "Choose new language:",
        "lang_changed": "Language updated. Thank you.",
        "area_changed": "Area updated: {ward}, {sub}. Thank you.",
        "menu": "Choose an action:",
        "opt_about": "1. About (details & budget)",
        "opt_vote": "2. Vote",
        "opt_voice": "4. Listen by voice (we'll call you)",
        "ask_vote_id": "To vote, enter your ID number:",
        "vote_id_bad": "ID does not match your registration. Press 0 to retry.",
        "already_voted": "You have already voted on this. Thank you.",
        "vote_prompt": "Your vote:",
        "opt_support": "1. I support",
        "opt_oppose": "2. I oppose",
        "vote_done": "Thank you! Your vote has been counted.",
        "vote_closed": "Participation for this bill is closed. Thank you.",
        "voice_note": "We'll call you to listen in your language. Thank you.",
        "nav_next": "99. More",
        "nav_back": "0. Back",
        "nav_main": "00. Main menu",
        "invalid": "Invalid choice. Try again.",
    },
}


# --- token helpers -----------------------------------------------------------
def _resolve(text: str) -> list[str]:
    """Split accumulated text and apply back/main tokens (0 / 00)."""
    out: list[str] = []
    for p in (text.split("*") if text else []):
        if p == "00":
            out = []               # jump back to the root menu
        elif p == "0":
            if out:
                out.pop()          # back one step
        else:
            out.append(p)
    return out


def _consume_paged(tokens: list[str], n_items: int):
    """Walk a paged-menu token run.

    Returns (choice, remaining, page):
      - choice None + page int  -> still on the menu; render `page`.
      - choice int (1-based global) + remaining tokens -> a selection was made.
    """
    max_page = (n_items - 1) // PAGE_SIZE if n_items else 0
    page = 0
    for i, tok in enumerate(tokens):
        if tok == "99":
            page = min(page + 1, max_page)
        elif tok == "88":
            page = max(page - 1, 0)
        else:
            return (int(tok) if tok.isdigit() else -1), tokens[i + 1:], None
    return None, [], page


def _render_paged(lbl: dict, title: str, options: list[str], page: int) -> str:
    total = max(1, math.ceil(len(options) / PAGE_SIZE))
    start = page * PAGE_SIZE
    chunk = options[start:start + PAGE_SIZE]
    lines = "\n".join(f"{start+i+1}. {name}" for i, name in enumerate(chunk))
    controls = []
    if page < total - 1:
        controls.append(lbl["nav_next"])
    controls.extend([lbl["nav_back"], lbl["nav_main"]])
    return f"CON {title} ({lbl['page']} {page+1}/{total})\n{lines}\n" + "   ".join(controls)


def _footer_deep(lbl: dict) -> str:
    return f"\n{lbl['nav_back']}   {lbl['nav_main']}"


def _index(seq, one_based) -> str | None:
    try:
        i = int(one_based) - 1
    except (TypeError, ValueError):
        return None
    return seq[i] if 0 <= i < len(seq) else None


def _valid_id(raw: str) -> bool:
    return raw.isdigit() and 6 <= len(raw) <= 9


# --- entry -------------------------------------------------------------------
def handle(phone_number: str, text: str) -> str:
    phone_hash = hash_phone(phone_number)
    reg = store.get_registration(phone_hash)
    if reg is None:
        return _signup(phone_number, phone_hash, text)
    return _browse(phone_hash, reg, text)


# --- one-time signup ---------------------------------------------------------
def _signup(phone_number: str, phone_hash: str, text: str) -> str:
    resolved = _resolve(text)

    if not resolved:
        return SIGNUP_LANGUAGE_MENU

    lang = LANG_BY_CHOICE.get(resolved[0])
    if lang is None:
        return INVALID_BILINGUAL
    lbl = LABELS[lang]
    rest = resolved[1:]

    # Step 1: national ID number.
    if not rest:
        return f"CON {lbl['ask_id']}"
    id_raw = rest[0]
    if not _valid_id(id_raw):
        return f"CON {lbl['bad_id']}\n{lbl['nav_back']}"

    # Step 2: sub-county (paged).
    choice, after_sub, page = _consume_paged(rest[1:], len(SUBCOUNTIES))
    if choice is None:
        return _render_paged(lbl, lbl["pick_area"], SUBCOUNTIES, page)
    sub = _index(SUBCOUNTIES, choice)
    if sub is None:
        return f"CON {lbl['invalid']}\n{lbl['nav_back']}"

    # Step 3: ward (paged, within the chosen sub-county).
    wards = W.wards_for(sub)
    wchoice, _after_ward, wpage = _consume_paged(after_sub, len(wards))
    if wchoice is None:
        return _render_paged(lbl, lbl["pick_ward"], wards, wpage)
    ward = _index(wards, wchoice)
    if ward is None:
        return f"CON {lbl['invalid']}\n{lbl['nav_back']}"

    # Step 4: save the one-time registration.
    status = store.register(phone_hash, phone_number, hash_id(id_raw), lang, sub, ward)
    if status == "id_taken":
        return f"END {lbl['id_taken']}"
    # Confirmation SMS so the citizen has a record in their inbox.
    deliver(phone_number, lbl["sms_registered"].format(ward=ward, sub=sub))
    return f"END {lbl['registered'].format(ward=ward, sub=sub)}"


# --- browse (registered users) ----------------------------------------------
def _browse(phone_hash: str, reg, text: str) -> str:
    resolved = _resolve(text)
    lang = reg["lang"] if reg["lang"] in LABELS else "sw"
    lbl = LABELS[lang]

    # Main menu — in the citizen's SAVED language (no re-selection).
    if not resolved:
        return (
            f"CON {lbl['welcome']}\n"
            f"{lbl['menu_my_area'].format(area=reg['sub_county'])}\n"
            f"{lbl['menu_other']}\n{lbl['menu_profile']}"
        )

    top, rest = resolved[0], resolved[1:]

    if top == "1":  # projects in my saved area (no sub-county re-selection)
        return _browse_projects(reg, lang, lbl, reg["sub_county"], rest)

    if top == "2":  # browse another area
        choice, after_sub, page = _consume_paged(rest, len(SUBCOUNTIES))
        if choice is None:
            return _render_paged(lbl, lbl["pick_area"], SUBCOUNTIES, page)
        sub = _index(SUBCOUNTIES, choice)
        if sub is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        return _browse_projects(reg, lang, lbl, sub, after_sub)

    if top == "3":  # change profile (language / area)
        return _change_profile(phone_hash, reg, lbl, rest)

    return f"CON {lbl['invalid']}{_footer_deep(lbl)}"


def _browse_projects(reg, lang, lbl, sub, tokens):
    projects = store.list_projects(sub)
    if not projects:
        return f"CON {lbl['no_projects']}{_footer_deep(lbl)}"

    # Choose a project.
    if not tokens:
        lines = []
        for i, p in enumerate(projects):
            tr = store.get_translation(p["id"], lang)
            name = tr["project_name"] if tr else p["name_en"]
            lines.append(f"{i+1}. {name}")
        return f"CON {lbl['projects']}\n" + "\n".join(lines) + _footer_deep(lbl)

    project = _pick(projects, tokens[0])
    if project is None:
        return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
    tr = store.get_translation(project["id"], lang)

    # Action menu: 1. About (details + budget, paired), 2. Vote.
    if len(tokens) == 1:
        return f"CON {lbl['menu']}\n{lbl['opt_about']}\n{lbl['opt_vote']}{_footer_deep(lbl)}"

    action = tokens[1]

    if action == "1":  # About — explanation + facts (works for bills with no budget)
        civic = tr["civic_education"] if tr else project["raw_text"][:120]
        data = tr["data_summary"] if tr else ""
        body = civic + (f"\n{data}" if data else "")
        return f"CON {body}{_footer_deep(lbl)}"

    if action == "2":  # Vote — re-enter ID so one person votes only once
        if not participation_open(project["status"]):
            return f"END {lbl['vote_closed']}"
        if len(tokens) == 2:
            return f"CON {lbl['ask_vote_id']}"
        entered_id = tokens[2]
        if not _valid_id(entered_id) or hash_id(entered_id) != reg["id_hash"]:
            return f"CON {lbl['vote_id_bad']}\n{lbl['nav_back']}"
        nullifier = vote_nullifier(entered_id)
        if store.has_voted(project["id"], nullifier):
            return f"CON {lbl['already_voted']}{_footer_deep(lbl)}"
        if len(tokens) == 3:
            return (f"CON {lbl['vote_prompt']}\n{lbl['opt_support']}\n"
                    f"{lbl['opt_oppose']}{_footer_deep(lbl)}")
        vchoice = {"1": "support", "2": "oppose"}.get(tokens[3])
        if vchoice is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        store.record_vote(project["id"], nullifier, vchoice)
        name = tr["project_name"] if tr else project["name_en"]
        deliver(reg["phone_number"], lbl["sms_voted"].format(project=name))
        return f"CON {lbl['vote_done']}{_footer_deep(lbl)}"

    return f"CON {lbl['invalid']}{_footer_deep(lbl)}"


def _change_profile(phone_hash, reg, lbl, tokens):
    if not tokens:
        return (f"CON {lbl['profile_menu']}\n{lbl['change_lang']}\n"
                f"{lbl['change_area']}{_footer_deep(lbl)}")

    which = tokens[0]

    if which == "1":  # change language
        if len(tokens) == 1:
            return (f"CON {lbl['choose_lang']}\n1. Kiswahili\n2. Gikuyu\n3. English"
                    f"{_footer_deep(lbl)}")
        new_lang = LANG_BY_CHOICE.get(tokens[1])
        if new_lang is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        store.update_registration(phone_hash, lang=new_lang)
        return f"END {LABELS[new_lang]['lang_changed']}"

    if which == "2":  # change area (sub-county + ward)
        choice, after_sub, page = _consume_paged(tokens[1:], len(SUBCOUNTIES))
        if choice is None:
            return _render_paged(lbl, lbl["pick_area"], SUBCOUNTIES, page)
        sub = _index(SUBCOUNTIES, choice)
        if sub is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        wards = W.wards_for(sub)
        wchoice, _after, wpage = _consume_paged(after_sub, len(wards))
        if wchoice is None:
            return _render_paged(lbl, lbl["pick_ward"], wards, wpage)
        ward = _index(wards, wchoice)
        if ward is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        store.update_registration(phone_hash, sub_county=sub, ward=ward)
        return f"END {lbl['area_changed'].format(ward=ward, sub=sub)}"

    return f"CON {lbl['invalid']}{_footer_deep(lbl)}"


def _pick(seq, choice: str):
    """Return seq[choice-1] for a 1-based USSD choice string, or None."""
    try:
        idx = int(choice) - 1
    except (TypeError, ValueError):
        return None
    return seq[idx] if 0 <= idx < len(seq) else None

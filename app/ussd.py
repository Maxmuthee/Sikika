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

LANG_BY_CHOICE = {"1": "sw", "2": "ki", "3": "en"}

SUBCOUNTIES = [
    "Nakuru Town East", "Nakuru Town West", "Naivasha", "Gilgil",
    "Kuresoi North", "Kuresoi South", "Molo", "Njoro",
    "Rongai", "Subukia", "Bahati",
]
WARDS = SUBCOUNTIES  # backward-compatible export (main.py iterates these)

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
        "registered": "Umesajiliwa! Utapokea arifa za miradi ya {ward}, {sub}. Piga *384# kuona miradi.",
        "page": "Ukurasa",
        "no_projects": "Hakuna miradi katika eneo hili kwa sasa. Asante.",
        "projects": "Miradi na miswada:",
        "menu": "Chagua kitendo:",
        "opt_civic": "1. Mradi/mswada huu ni nini?",
        "opt_data": "2. Angalia bajeti/maelezo",
        "opt_vote": "3. Piga kura",
        "opt_voice": "4. Sikiliza kwa sauti (utapigiwa)",
        "ask_vote_id": "Ili kupiga kura, weka nambari yako ya ID:",
        "vote_id_bad": "ID hailingani na usajili wako. Bonyeza 0 ujaribu tena.",
        "already_voted": "Umeshapiga kura kwa mradi huu. Asante.",
        "vote_prompt": "Kura yako:",
        "opt_support": "1. Naunga mkono",
        "opt_oppose": "2. Napinga",
        "vote_done": "Asante! Kura yako imehesabiwa.",
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
        "registered": "Niwandikithia! Niukwamukira uhoro wa miradi ya {ward}, {sub}. Hura *384# kuona miradi.",
        "page": "Ithangu",
        "no_projects": "Gutiri miradi gicigo giki riu. Ni wega.",
        "projects": "Miradi na miswada:",
        "menu": "Thura undu:",
        "opt_civic": "1. Mradi/mswada uyu ni kii?",
        "opt_data": "2. Rora mbeca/maundu",
        "opt_vote": "3. Hura kura",
        "opt_voice": "4. Thikiriria na mugambo (niukuhurwo)",
        "ask_vote_id": "Kuhura kura, ikira namba yaku ya ID:",
        "vote_id_bad": "ID ndiiganaine na kwiyandikithia gwaku. Hinya 0 ugerie.",
        "already_voted": "Niwahurite kura mradi-ini uyu. Ni wega.",
        "vote_prompt": "Kura yaku:",
        "opt_support": "1. Ninyitikaniirie",
        "opt_oppose": "2. Ndiitikaniirie",
        "vote_done": "Ni wega! Kura yaku niyatarwo.",
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
        "registered": "Registered! You'll get alerts for {ward}, {sub}. Dial *384# to view projects.",
        "page": "Page",
        "no_projects": "No projects in this area yet. Thank you.",
        "projects": "Projects & bills:",
        "menu": "Choose an action:",
        "opt_civic": "1. What is this project/bill?",
        "opt_data": "2. View budget/details",
        "opt_vote": "3. Vote",
        "opt_voice": "4. Listen by voice (we'll call you)",
        "ask_vote_id": "To vote, enter your ID number:",
        "vote_id_bad": "ID does not match your registration. Press 0 to retry.",
        "already_voted": "You have already voted on this. Thank you.",
        "vote_prompt": "Your vote:",
        "opt_support": "1. I support",
        "opt_oppose": "2. I oppose",
        "vote_done": "Thank you! Your vote has been counted.",
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
            out = out[:1]
        elif p == "0":
            if out:
                out.pop()
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
    return f"END {lbl['registered'].format(ward=ward, sub=sub)}"


# --- browse (registered users) ----------------------------------------------
def _browse(phone_hash: str, reg, text: str) -> str:
    resolved = _resolve(text)

    if not resolved:
        return LANGUAGE_MENU
    lang = LANG_BY_CHOICE.get(resolved[0])
    if lang is None:
        return INVALID_BILINGUAL
    lbl = LABELS[lang]

    # Sub-county selection (paged, continuous numbering).
    choice, after_sub, page = _consume_paged(resolved[1:], len(SUBCOUNTIES))
    if choice is None:
        return _render_paged(lbl, lbl["pick_area"], SUBCOUNTIES, page)
    sub = _index(SUBCOUNTIES, choice)
    if sub is None:
        return f"CON {lbl['invalid']}{_footer_deep(lbl)}"

    store.upsert_profile(phone_hash, lang, sub_county=sub, ward=sub)

    projects = store.list_projects(sub)
    if not projects:
        return f"CON {lbl['no_projects']}{_footer_deep(lbl)}"

    # Choose a project.
    if not after_sub:
        lines = []
        for i, p in enumerate(projects):
            tr = store.get_translation(p["id"], lang)
            name = tr["project_name"] if tr else p["name_en"]
            lines.append(f"{i+1}. {name}")
        return f"CON {lbl['projects']}\n" + "\n".join(lines) + _footer_deep(lbl)

    project = _pick(projects, after_sub[0])
    if project is None:
        return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
    tr = store.get_translation(project["id"], lang)

    # Project action menu.
    if len(after_sub) == 1:
        return (
            f"CON {lbl['menu']}\n{lbl['opt_civic']}\n{lbl['opt_data']}\n"
            f"{lbl['opt_vote']}\n{lbl['opt_voice']}{_footer_deep(lbl)}"
        )

    action = after_sub[1]

    if action == "1":  # civic education
        body = tr["civic_education"] if tr else project["raw_text"][:130]
        return f"CON {body}{_footer_deep(lbl)}"

    if action == "2":  # data summary
        body = tr["data_summary"] if tr else project["raw_text"][:130]
        return f"CON {body}{_footer_deep(lbl)}"

    if action == "3":  # vote — re-enter ID so one person votes only once
        # Step a: ask for the ID.
        if len(after_sub) == 2:
            return f"CON {lbl['ask_vote_id']}"
        entered_id = after_sub[2]
        # Must be the caller's own registered ID (verified as a hash).
        if not _valid_id(entered_id) or hash_id(entered_id) != reg["id_hash"]:
            return f"CON {lbl['vote_id_bad']}\n{lbl['nav_back']}"
        nullifier = vote_nullifier(entered_id)
        if store.has_voted(project["id"], nullifier):
            return f"CON {lbl['already_voted']}{_footer_deep(lbl)}"
        # Step b: choose support/oppose.
        if len(after_sub) == 3:
            return (
                f"CON {lbl['vote_prompt']}\n{lbl['opt_support']}\n"
                f"{lbl['opt_oppose']}{_footer_deep(lbl)}"
            )
        vchoice = {"1": "support", "2": "oppose"}.get(after_sub[3])
        if vchoice is None:
            return f"CON {lbl['invalid']}{_footer_deep(lbl)}"
        store.record_vote(project["id"], nullifier, vchoice)
        return f"CON {lbl['vote_done']}{_footer_deep(lbl)}"

    if action == "4":  # voice / IVR callback note
        return f"CON {lbl['voice_note']}{_footer_deep(lbl)}"

    return f"CON {lbl['invalid']}{_footer_deep(lbl)}"


def _pick(seq, choice: str):
    """Return seq[choice-1] for a 1-based USSD choice string, or None."""
    try:
        idx = int(choice) - 1
    except (TypeError, ValueError):
        return None
    return seq[idx] if 0 <= idx < len(seq) else None

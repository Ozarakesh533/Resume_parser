import os
import re
import fitz  # PyMuPDF
import pdfplumber
import json
import nltk
from nltk.corpus import stopwords
from datetime import datetime
from dateutil.relativedelta import relativedelta
import phonenumbers
from phonenumbers import NumberParseException
from geopy.geocoders import Nominatim
from typing import Optional
from collections import defaultdict
import shutil

# Download stopwords if not already downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# ------------------ Text normalization helpers ------------------ #
def _normalize_text_block(txt: str) -> str:
    # unify whitespace, normalize dashes, remove excessive empty lines
    if not txt:
        return ""
    txt = txt.replace("\u00A0", " ")  # non-breaking space
    txt = re.sub(r"\s+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    txt = re.sub(r"[\t\r]", " ", txt)
    txt = re.sub(r"\s{2,}", " ", txt)
    # common page artifact: "Page 1 of 3"
    txt = re.sub(r"^\s*Page\s+\d+\s+(of|/)\s*\d+\s*$", "", txt, flags=re.IGNORECASE | re.MULTILINE)
    return txt.strip()

def _dehyphenate_lines(lines):
    out = []
    for ln in lines:
        if out and out[-1].rstrip().endswith('-') and ln[:1].islower():
            # join hyphenated split: prev-\nnext
            out[-1] = out[-1].rstrip()[:-1] + ln.lstrip()
        else:
            out.append(ln)
    return out

# ------------------ Step 1: Extract Text Using pdfplumber (UPDATED) ------------------ #
def extract_text_with_pdfplumber(file_path):
    """Improved pdfplumber extraction with word-rebuild and table-aware merge."""
    try:
        pages_text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # 1) Native page text
                page_text = page.extract_text() or ""

                # 2) If native is too sparse, rebuild from words sorted by y,x
                if len(page_text.strip()) < 20:
                    try:
                        words = page.extract_words(x_tolerance=2, y_tolerance=3)
                        # group by line using y0 rounded
                        lines_map = {}
                        for w in words:
                            key = round(w.get('top', 0), 1)
                            lines_map.setdefault(key, []).append((w.get('x0', 0), w.get('text', '')))
                        rebuilt_lines = []
                        for _, items in sorted(lines_map.items(), key=lambda kv: kv[0]):
                            items.sort(key=lambda it: it[0])
                            rebuilt_lines.append(" ".join(t for _, t in items))
                        if rebuilt_lines:
                            page_text = "\n".join(rebuilt_lines)
                    except Exception:
                        pass

                # 3) Append table text (if any) as pipe-separated rows
                try:
                    tables = page.extract_tables()
                    for tbl in tables or []:
                        for row in tbl:
                            row = [ (cell.strip() if cell else '') for cell in row ]
                            if any(cell for cell in row):
                                page_text += "\n" + " | ".join(row)
                except Exception:
                    pass

                pages_text.append(_normalize_text_block(page_text))

        # dehyphenate across per-page lines
        joined = []
        for ptxt in pages_text:
            joined.extend(ptxt.splitlines())
        joined = _dehyphenate_lines(joined)
        return "\n".join(l for l in joined if l.strip())
    except Exception:
        return ""

# ------------------ Step 2: Extract Text Using pymupdf ------------------ #
def extract_text_with_pymupdf(file_path):
    """Best-effort text via PyMuPDF using multiple modes and line reconstruction."""
    try:
        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            # mode A: simple text
            txt_a = page.get_text("text") or ""

            # mode B: reconstruct from dict blocks/lines/spans when needed
            txt_b_lines = []
            try:
                d = page.get_text("dict")
                for block in d.get("blocks", []):
                    for line in block.get("lines", []):
                        spans_text = []
                        for span in line.get("spans", []):
                            s = span.get("text", "")
                            if s:
                                spans_text.append(s)
                        if spans_text:
                            txt_b_lines.append(" ".join(spans_text))
            except Exception:
                pass

            page_text = txt_a if len(txt_a.strip()) >= 20 else "\n".join(txt_b_lines)
            page_text = _normalize_text_block(page_text)
            pages_text.append(page_text)

        # dehyphenate across per-page lines
        joined = []
        for ptxt in pages_text:
            joined.extend(ptxt.splitlines())
        joined = _dehyphenate_lines(joined)
        return "\n".join(l for l in joined if l.strip())
    except Exception:
        return ""

def get_combined_texts(file_path):
    """Return combined text from both engines and each separately."""
    txt1 = extract_text_with_pdfplumber(file_path)
    txt2 = extract_text_with_pymupdf(file_path)
    combined = (txt1 or "") + "\n" + (txt2 or "")
    return combined.strip(), txt1, txt2

# ============================== Alternate PyMuPDF Sectionizer (Refined) ============================== #
# This is an alternative extractor added without changing existing logic.
# It is not wired into process_resume(); use manually for experiments or future fallbacks.

HEADER_PATTERNS_ALT = {
    "summary": re.compile(
        r"^\s*(summary|profile|professional\s+summary|about\s+me|objective|career\s+objective)\s*:?\s*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*(experience|work(\s+experience)?|employment|professional(\s+experience)?|career\s+history|sap\s+experience)\s*:?\s*$",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^\s*(skills?|skils|technical\s+skills?|key\s+skills?|core\s+competenc(y|ies)|expertise)\s*:?\s*$",
        re.IGNORECASE,
    ),
    "projects": re.compile(r"^\s*(projects?|project\s+portfolio|works?)\s*:?\s*$", re.IGNORECASE),
    "education": re.compile(r"^\s*(education|academic|qualifications?|degree)\s*:?\s*$", re.IGNORECASE),
    "certifications": re.compile(r"^\s*(certifications?|certificates?|accreditations?|awards?)\s*:?\s*$", re.IGNORECASE),
    "personal": re.compile(r"^\s*(personal\s+details|contact|contact\s+info)\s*:?\s*$", re.IGNORECASE),
}

SUB_HEADER_PATTERNS_ALT = {
    "experience": [
        re.compile(r"^\s*role\s*:?$", re.IGNORECASE),
        re.compile(r"^\s*project\s*:?:?\s*[\w\s\-]+", re.IGNORECASE),
    ],
    "skills": [
        re.compile(r"^\s*language\s+and\s+framework\s*:?$", re.IGNORECASE),
        re.compile(r"^\s*database\s*:?$", re.IGNORECASE),
        re.compile(r"^\s*development\s+tools\s*:?$", re.IGNORECASE),
        re.compile(r"^\s*technologies\s*:?$", re.IGNORECASE),
    ],
}

IMPLICIT_SECTION_CUES_ALT = [
    (re.compile(r"^\s*project\s*[:#]\s*\d+", re.IGNORECASE), "projects"),
    (re.compile(r"^\s*responsibilities\s*:?\s*$", re.IGNORECASE), "experience"),
]

LEADING_BULLETS_ALT = re.compile(r"^\s*[-•●▪□■–—❖●]+\s*")
TRAILING_BULLETS_ALT = re.compile(r"\s*[•●▪□■–—❖●]+\s*$")

def _alt_is_all_caps(s: str) -> bool:
    letters = re.sub(r"[^A-Za-z]+", "", s)
    return bool(letters) and letters.isupper()

def _alt_span_is_bold(span: dict) -> bool:
    flags = span.get("flags", 0)
    if flags & 16:  # be conservative for the alt extractor
        return True
    font_name = span.get("font", "") or ""
    return "bold" in font_name.lower()

def _alt_collect_page_font_median(page) -> float:
    sizes = [
        float(s.get("size", 0))
        for b in page.get_text("dict").get("blocks", [])
        for l in b.get("lines", [])
        for s in l.get("spans", [])
        if s.get("text", "").strip()
    ]
    if not sizes:
        return 11.0
    sizes.sort()
    mid = len(sizes) // 2
    return (sizes[mid] if len(sizes) % 2 else (sizes[mid - 1] + sizes[mid]) / 2.0) or 11.0

def _alt_line_is_header(text: str, is_bold: bool, max_size: float, median_size: float) -> bool:
    if len(text.split()) > 5:
        return False
    if not any(p.search(text) for p in HEADER_PATTERNS_ALT.values()):
        return False
    size_signal = max_size >= (median_size + 1.5)
    if "engineer" in text.lower():
        return False
    return is_bold or size_signal

def _alt_which_header(text: str) -> Optional[str]:
    for sec, pat in HEADER_PATTERNS_ALT.items():
        if pat.search(text):
            return sec
    return None

def _alt_is_sub_header(text: str, parent_section: str) -> bool:
    patterns = SUB_HEADER_PATTERNS_ALT.get(parent_section, [])
    return any(p.search(text) for p in patterns)

def _alt_clean_line(text: str) -> str:
    text = LEADING_BULLETS_ALT.sub("", text)
    text = TRAILING_BULLETS_ALT.sub("", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_sections_with_pymupdf_refined(file_path: str) -> dict:
    """
    Alternative refined segmentation not wired into process_resume by default.
    """
    doc = fitz.open(file_path)
    parsed_sections = defaultdict(list)

    all_page_blocks = []
    for page in doc:
        all_page_blocks.extend(page.get_text("dict", sort=False).get("blocks", []))

    base_median = _alt_collect_page_font_median(doc[0]) if len(doc) else 11.0
    header_info = []
    for block in all_page_blocks:
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = "".join(s.get("text", "") for s in spans).strip()
            if not line_text:
                continue
            is_bold = any(_alt_span_is_bold(s) for s in spans)
            max_size = max((float(s.get("size", 0)) for s in spans), default=11.0)
            potential = _alt_which_header(line_text)
            if potential and _alt_line_is_header(line_text, is_bold, max_size, base_median):
                y0 = line.get('bbox', [0,0,0,0])[1]
                header_info.append({"name": potential, "y0": y0})

    header_info.sort(key=lambda h: h['y0'])

    current_section = "__preamble__"
    for block in all_page_blocks:
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            line_text = "".join(s.get("text", "") for s in spans).strip()
            if not line_text:
                continue
            is_bold = any(_alt_span_is_bold(s) for s in spans)
            max_size = max((float(s.get("size", 0)) for s in spans), default=11.0)
            if _alt_which_header(line_text) and _alt_line_is_header(line_text, is_bold, max_size, base_median):
                current_section = _alt_which_header(line_text) or current_section
                continue

            y0 = line.get('bbox', [0,0,0,0])[1]
            best_match_header: Optional[str] = None
            for hdr in header_info:
                if y0 > hdr['y0']:
                    best_match_header = hdr['name']
                else:
                    break

            cleaned = _alt_clean_line(line_text)
            if not cleaned:
                continue
            if best_match_header:
                parsed_sections[best_match_header].append(cleaned)
            else:
                parsed_sections["__preamble__"].append(cleaned)

    final_sections = {}
    preamble_text = "\n".join(parsed_sections.get("__preamble__", []))

    email_pattern = re.compile(r"[\w\.\-]+@[\w\.\-]+\.\w+")
    phone_pattern = re.compile(r"(?:\+91[-\s]?)?[6-9]\d{9}\b")

    email = email_pattern.search(preamble_text)
    phone = phone_pattern.search(preamble_text)

    personal_info = []
    if email:
        personal_info.append(email.group(0))
    if phone:
        personal_info.append(phone.group(0))

    preamble_lines = [line for line in preamble_text.split('\n') if line.strip()]
    if preamble_lines:
        personal_info.insert(0, preamble_lines[0])

    summary_lines = []
    for line in preamble_lines:
        if not (email and email.group(0) in line) and not (phone and phone.group(0) in line) and not any(p in line.lower() for p in ["address", "india"]):
            if line not in personal_info and len(line.split()) > 5:
                summary_lines.append(line)

    final_sections["personal"] = "\n".join(dict.fromkeys(personal_info))
    if summary_lines:
        final_sections["summary"] = "\n".join(summary_lines)
    elif parsed_sections.get("summary"):
        final_sections["summary"] = "\n".join(parsed_sections["summary"])

    for sec in ["experience", "projects", "skills", "education", "certifications"]:
        lines = parsed_sections.get(sec, [])
        if lines:
            final_sections[sec] = "\n".join(lines).strip()

    return final_sections

# ------------------ Enhanced Name Extraction Logic ------------------ #

SECTION_HEADERS = {
    "profile","summary","objective","about me","professional summary","profile summary",
    "skills","technical skills","key skills","competencies","expertise",
    "experience","professional experience","work experience","employment history",
    "projects","achievements","certifications","education","references",
    "personal data","personal details",
    # Also treat these as headers to stop preface earlier
    "resume","curriculum vitae","biodata","bio-data"
}

# Never treat these as names (also check no-space variants for OCR joins).
SKIP_PHRASES = {
    "resume","curriculum vitae","curriculumvitae","cv","bio-data","biodata"
}

def _is_skip_phrase(line: str) -> bool:
    ll = line.strip().lower().strip('-:•|')
    if not ll:
        return False
    if ll in SKIP_PHRASES:
        return True
    if ll.replace(' ', '') in SKIP_PHRASES:
        return True
    return False

JOB_TITLE_WORDS = {
    'senior','junior','lead','software','engineer','developer','manager',
    'director','analyst','specialist','consultant','administrator','coordinator',
    'assistant','associate','executive','officer','president','head','chief',
    'test','quality','assurance','designer','architect','technician','support',
    'professional','experience','intern','trainee','dev','qa','sdet'
}

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+')
PHONE_RE = re.compile(r'\+?\d[\d\-\s()]{7,}\d')
URL_RE   = re.compile(r'(https?://)?(www\.)?(linkedin|github)\.com/[a-z0-9/_-]+', re.I)

LABEL_SPLIT_RE = re.compile(
    r"""^\s*(?:[•*●■▪️❖\-–—]?\s*)?      # optional bullet
        (?:name|full\s*name)\s*         # label
        [:\-–—]\s*                      # separator
        (.*)$                           # remainder on same line
    """,
    re.I | re.X
)

TITLE_NAME_RE = re.compile(
    r"""^(
        (?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5}) |
        (?:[A-Z]{2,}(?:\s+[A-Z]{2,}){1,5}) |
        (?:(?:[A-Z]\.\s*){1,3}[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)
    )$""",
    re.X
)

def _is_section_header(line: str) -> bool:
    ll = line.strip().lower().rstrip(':')
    return ll in SECTION_HEADERS

def _clean_candidate(line: str) -> str:
    cand = line.strip()
    cand = re.sub(r'\s+', ' ', cand)
    cand = cand.strip("•|-_—:;")
    return cand

def _bad_line(line: str) -> bool:
    if _is_skip_phrase(line):
        return True
    if EMAIL_RE.search(line) or PHONE_RE.search(line) or URL_RE.search(line):
        return True
    if any(tok.isdigit() for tok in line):
        return True
    if any(sym in line for sym in "/\\@#%^*_+=[]{}<>"):
        return True
    return False

def _tokenize(line: str):
    return [t for t in re.split(r'\s+', line.strip()) if t]

def _has_job_title_tokens(line: str) -> bool:
    return any(t.lower() in JOB_TITLE_WORDS for t in _tokenize(line))

def _is_name_shape(s: str) -> bool:
    s = _clean_candidate(s)
    if len(s) < 2 or len(s) > 120:
        return False
    if re.search(r"[^A-Za-z .'\-]", s):
        return False
    return TITLE_NAME_RE.match(s) is not None

def _normalize_name_tokens(tokens):
    cleaned = []
    for t in tokens:
        tt = t.strip(".-'")
        if not tt:
            continue
        if not re.match(r"^[A-Za-z][A-Za-z.\-']*$", t):
            continue
        cleaned.append(t)
    return cleaned

def _extract_from_labeled_block(lines, idx):
    line = lines[idx]
    m = LABEL_SPLIT_RE.match(line)
    if not m:
        return None
    remainder = _clean_candidate(m.group(1))

    if not remainder or len(_tokenize(remainder)) < 2:
        for j in range(idx + 1, min(idx + 3, len(lines))):
            nxt = _clean_candidate(lines[j])
            if not nxt or _bad_line(nxt) or _is_section_header(nxt):
                continue
            candidate = (remainder + " " + nxt).strip() if remainder else nxt
            tokens = _normalize_name_tokens(_tokenize(candidate))
            if 2 <= len(tokens) <= 6 and not _has_job_title_tokens(candidate):
                cand_str = " ".join(tokens)
                if _is_name_shape(cand_str):
                    return cand_str

    tokens = _normalize_name_tokens(_tokenize(remainder))
    if 2 <= len(tokens) <= 6:
        candidate = " ".join(tokens)
        if not _has_job_title_tokens(candidate) and _is_name_shape(candidate):
            return candidate

    if len(tokens) == 1:
        for j in range(idx + 1, min(idx + 3, len(lines))):
            nxt = _clean_candidate(lines[j])
            if not nxt or _bad_line(nxt) or _is_section_header(nxt):
                continue
            more = _normalize_name_tokens(_tokenize(nxt))
            merged = tokens + more
            merged = merged[:6]
            if len(merged) >= 2:
                candidate = " ".join(merged)
                if not _has_job_title_tokens(candidate) and _is_name_shape(candidate):
                    return candidate
    return None

def _extract_from_first_line_with_role(lines):
    if not lines:
        return None
    first = _clean_candidate(lines[0])
    if not first or _bad_line(first):
        return None

    tokens = _tokenize(first)
    if not tokens:
        return None

    name_tokens = []
    for t in tokens:
        upper = t.upper()
        if (upper in {
            "SAP","S/4HANA","HANA","ABAP","SD","MM","PP","FICO","CONSULTANT","ENGINEER","DEVELOPER",
            "MANAGER","ARCHITECT","LEAD","SR","JR","SENIOR","JUNIOR","ADMIN","ADMINISTRATOR"
        }
            or any(ch.isdigit() for ch in t)
            or '/' in t
            or (t.isupper() and len(t) > 2)
            or t.lower() in JOB_TITLE_WORDS):
            break
        if re.match(r"^[A-Za-z][A-Za-z.\-']*$", t):
            name_tokens.append(t)
        else:
            break

    if 1 <= len(name_tokens) <= 2:
        candidate = " ".join(name_tokens)
        if len(name_tokens) == 1:
            if name_tokens[0][0].isupper() and name_tokens[0].lower() not in JOB_TITLE_WORDS:
                return candidate
        else:
            if _is_name_shape(candidate):
                return candidate
    return None

def _name_score(line: str, index_weight: float) -> float:
    cand = _clean_candidate(line)
    tokens = _tokenize(cand)
    score = 0.0
    if TITLE_NAME_RE.match(cand): score += 4.0
    if 2 <= len(tokens) <= 3: score += 2.0
    elif len(tokens) == 4: score += 1.0
    else: score -= 1.0
    title_tokens = sum(1 for t in tokens if (t[:1].isupper() and t[1:].islower()))
    all_caps_tokens = sum(1 for t in tokens if t.isupper() and len(t) > 1)
    score += 0.3 * title_tokens
    score += 0.4 * all_caps_tokens
    if _has_job_title_tokens(cand): score -= 2.5
    if _bad_line(cand): score -= 5.0
    score += index_weight
    return score

def extract_name(text: str) -> str:
    """Extract name via layered heuristics (first-line role, labeled, preface, score, fallback)."""
    raw_lines = [ln.rstrip() for ln in text.split("\n")]
    lines = [ln for ln in (l.strip() for l in raw_lines) if ln]
    if not lines:
        return "Unknown"

    firstline_name = _extract_from_first_line_with_role(lines)
    if firstline_name:
        return firstline_name

    for i, line in enumerate(lines[:40]):
        if LABEL_SPLIT_RE.match(line):
            labeled = _extract_from_labeled_block(lines, i)
            if labeled:
                return labeled

    preface = []
    for ln in lines[:60]:
        if _is_section_header(ln):
            break
        preface.append(ln)
    preface = preface[:12] if preface else lines[:12]

    best = None
    best_score = float("-inf")
    for idx, ln in enumerate(preface):
        cand = _clean_candidate(ln)
        if (not cand or _bad_line(cand) or _has_job_title_tokens(cand)
            or _is_section_header(cand) or _is_skip_phrase(cand)):
            continue
        if not _is_name_shape(cand):
            continue
        index_weight = 2.0 - (idx * 0.15)
        sc = _name_score(cand, index_weight)
        if sc > best_score:
            best_score = sc
            best = cand
    if best:
        return best

    for ln in preface[:5]:
        if _bad_line(ln) or _is_section_header(ln) or _is_skip_phrase(ln):
            continue
        tokens = _normalize_name_tokens(_tokenize(ln))
        tokens = [t for t in tokens if t.lower() not in JOB_TITLE_WORDS]
        if 2 <= len(tokens) <= 6:
            cand = " ".join(tokens[:4])
            if not _is_skip_phrase(cand) and _is_name_shape(cand):
                return cand

    first = _clean_candidate(lines[0])
    if _is_name_shape(first) and not _is_section_header(first) and not _is_skip_phrase(first):
        return first
    return "Unknown"

def verify_and_select_name(name1, name2):
    if name1 == name2 or name2 == "Unknown":
        return name1
    if name1 == "Unknown":
        return name2
    return name1 if len(name1) >= len(name2) else name2

# ------------------ Contact Info (UNCHANGED) ------------------ #
def extract_email(text):
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    candidates = re.findall(r'(\+?\d[\d\-\s\(\)]{9,}\d)', text)
    for raw in candidates:
        cleaned = raw.strip()
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) < 10 or len(digits) > 15:
            continue

        if len(digits) == 10 and digits[0] in {'6', '7', '8', '9'}:
            try:
                pn = phonenumbers.parse(digits, 'IN')
                if phonenumbers.is_valid_number(pn):
                    return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except NumberParseException:
                pass

        try:
            pn_in = phonenumbers.parse(cleaned, 'IN')
            if phonenumbers.is_valid_number(pn_in):
                return phonenumbers.format_number(pn_in, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except NumberParseException:
            pass

        try:
            pn_any = phonenumbers.parse(cleaned, None)
            if phonenumbers.is_valid_number(pn_any):
                return phonenumbers.format_number(pn_any, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except NumberParseException:
            pass
    return None

def extract_linkedin(text):
    match = re.search(r'(https?://)?(www\.)?(linkedin\.com/in/[a-zA-Z0-9_-]+)', text)
    if match:
        url = match.group(0)
        return url if url.startswith("http") else "https://" + url
    match_username = re.search(r'linkedin[:\s]*([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if match_username:
        username = match_username.group(1)
        return f"https://www.linkedin.com/in/{username}"
    return None

def extract_github(text):
    match = re.search(r'(https?://)?(www\.)?(github\.com/[a-zA-Z0-9_-]+)', text)
    if match:
        url = match.group(0)
        return "https://" + url if not url.startswith("http") else url
    match_username = re.search(r'github[:\s]*([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if match_username:
        username = match_username.group(1)
        return f"https://github.com/{username}"
    return None

def extract_location(text, use_geopy=False):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Common Indian cities and states for better matching
    indian_locations = {
        'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 
        'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore',
        'maharashtra', 'karnataka', 'tamil nadu', 'gujarat', 'rajasthan', 'uttar pradesh',
        'west bengal', 'telangana', 'andhra pradesh', 'kerala', 'madhya pradesh'
    }
    
    location_patterns = [
        r'\b([A-Za-z\s]+),\s*([A-Za-z\s]+)\b',  # City, State format
        r'\b([A-Za-z]+)\s*,\s*(India|INDIA)\b',  # City, India
        r'\b(Address|Location|City|Residence)\s*:?\s*([A-Za-z\s,]+)\b'  # Labeled location
    ]
    
    # Skip lines that are clearly not locations
    skip_patterns = [
        r'•.*?(posting|implementation|configuration|support|issues)',
        r'\b(experience|skills|education|projects|responsibilities)\b',
        r'\b(years?|months?)\b.*\b(experience|exp)\b',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+',  # email
        r'\+?\d[\d\s\-()]{8,}\d'  # phone
    ]
    
    def is_valid_location(loc_text):
        loc_lower = loc_text.lower().strip()
        # Check if it's a known location
        if any(city in loc_lower for city in indian_locations):
            return True
        # Check if it matches city, state pattern
        if re.match(r'^[A-Za-z\s]+,\s*[A-Za-z\s]+$', loc_text.strip()):
            return True
        # Reject if too long (likely description)
        if len(loc_text) > 50:
            return False
        return False
    
    # Look for explicit location labels first
    for line in lines[:15]:  # Check first 15 lines
        # Skip lines that are clearly not locations
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        # Check for labeled locations
        label_match = re.search(r'\b(Address|Location|City|Residence|Place)\s*:?\s*([A-Za-z\s,]+)', line, re.IGNORECASE)
        if label_match:
            location_text = label_match.group(2).strip()
            if is_valid_location(location_text):
                return location_text
        
        # Check for city, state patterns
        for pattern in location_patterns:
            match = re.search(pattern, line)
            if match:
                if len(match.groups()) >= 2:
                    location_text = f"{match.group(1).strip()}, {match.group(2).strip()}"
                else:
                    location_text = match.group(1).strip() if match.group(1) else match.group(0).strip()
                
                if is_valid_location(location_text):
                    return location_text
    
    # Look for standalone city names
    for line in lines[:10]:
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue
            
        words = line.split()
        for word in words:
            clean_word = re.sub(r'[^A-Za-z\s]', '', word).strip().lower()
            if clean_word in indian_locations and len(clean_word) > 3:
                return word.strip()
    
    return None

# ------------------ Enhanced Skill Extraction ------------------ #
def extract_skills(text):
    """Extract skills robustly, filtering sentences and person names."""
    stop_words_set = set(stopwords.words('english'))

    junk_keywords = {
        "skills", "tools", "technologies", "services", "languages", "systems", "expertise",
        "responsibilities", "projects", "summary", "roles", "role", "team", "teams", "functional",
        "applications", "application", "platforms", "frameworks", "experience", "methodologies",
        "used", "use", "using", "proficient", "knowledge", "worked", "responsible", "designing",
        "developing", "testing", "managing", "created", "performed", "maintaining", "executing",
        "engineer", "engineered", "helped", "understanding", "done", "skills.",
        "communication", "problem", "teamwork", "collaboration", "leadership", "interpersonal",
        "thinking", "adaptability", "attention", "critical", "self", "fast", "quick", "learning",
        "and", "between", "to", "from", "till", "since", "before", "after", "year", "years",
        "etc", "etc.", "version", "control", "expert", "company", "client", "project",
        "organization", "details", "working", "environment", "task", "responsibility", "objective", "goal",
        # Additional location-related terms to exclude
        "pune", "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata", "india",
        "maharashtra", "karnataka", "gujarat", "rajasthan", "tamil nadu", "west bengal",
        # Job titles and roles to exclude
        "lecturer", "professor", "manager", "developer", "analyst", "consultant", "engineer",
        "coordinator", "specialist", "executive", "officer", "director", "lead", "senior", "junior",
        # Common non-skill terms
        "bank", "coordination", "organizational", "confidently", "typing", "wpm",
        "english", "hindi", "marathi", "tamil", "telugu", "gujarati", "bengali"
    }

    TECH_TERMS = {
        "aws","azure","gcp","docker","kubernetes","helm","terraform","ansible","jenkins","git","gitlab",
        "python","java","javascript","typescript","node.js","go","golang","ruby","php","c","c++","c#",
        "react","angular","vue","next.js","nuxt","redux","html","css","sass","less","bootstrap",
        "sql","mysql","postgresql","postgres","oracle","mongodb","hive","spark","hadoop","pyspark",
        "selenium","pytest","junit","testng","cypress","playwright","jmeter",
        "rest","rest api","graphql","soap","microservices","ci/cd","api",
        "pandas","numpy","scikit-learn","sklearn","tensorflow","pytorch","nlp","eda",
        "linux","windows","macos","bash","shell","powershell","jira","confluence",
        "sap","abap","hana","s/4hana","fico","mm","sd","pp","tableau","power bi",
        "spring","hibernate","maven","gradle","junit","mockito","kafka","redis",
        "elasticsearch","kibana","logstash","grafana","prometheus","splunk"
    }

    FORCE_UPPER = {"SQL","HTML","CSS","AWS","GCP","EDA","CNN","RNN","QA","REST","CI/CD","API","SAP","ABAP"}

    def is_person_name(s: str) -> bool:
        words = [w for w in re.split(r"\s+", s.strip()) if w]
        if 2 <= len(words) <= 4 and all(w[:1].isupper() and w[1:].islower() for w in words if w.isalpha()):
            if any(w.lower() in TECH_TERMS for w in words):
                return False
            return True
        return False

    MONTHS_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\b", re.IGNORECASE)
    COMPANY_SUFFIXES = {"technologies","solutions","labs","pvt","ltd","inc","llc","limited","corporation","corp"}
    VERB_CLUES = {"implemented","designed","developed","built","created","managed","led","leading","owning","driving","improved","optimized","maintained","executed"}

    def is_short_tech_token(tok: str) -> bool:
        t = tok.strip()
        if not t:
            return False
        if len(t.split()) > 4:
            return False
        if not re.fullmatch(r"[A-Za-z0-9+#./_\- ]+", t):
            return False
        if t.endswith('.') and len(t.split()) > 3:
            return False
        if MONTHS_RE.search(t) or re.search(r"\b\d{4}\b", t):
            return False
        if t.lower() in stop_words_set or t.lower() in junk_keywords:
            return False
        if re.fullmatch(r"\d+", t):
            return False
        if len(t.split()) == 1 and re.search(r"(ing|ed)$", t.lower()):
            return False
        parts = [p.lower() for p in t.split()]
        if any(p in COMPANY_SUFFIXES for p in parts):
            return False
        if parts and parts[0] in VERB_CLUES:
            return False
        if is_person_name(t):
            return False
        return True

    candidates = []
    for line in (l for l in text.split("\n") if l.strip()):
        cleaned_line = re.sub(r"\(.*?\)", "", line)
        for token in re.split(r"[,;/|\n]", cleaned_line):
            for sub in re.split(r":", token):
                val = sub.strip().strip("-•|")
                if not val:
                    continue
                if is_short_tech_token(val):
                    up = val.upper()
                    if up in FORCE_UPPER or val.lower() in TECH_TERMS:
                        candidates.append(up)
                    else:
                        if len(val.split()) > 1:
                            candidates.append(" ".join(w.upper() if w.lower() in {"ci/cd","api","sql"} else w.title() for w in val.split()))
                        else:
                            candidates.append(val.title())

    seen = set()
    result = []
    for c in candidates:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            result.append(c)
    return result

# Keep the original skill utilities for backward compatibility
def clean_skill_lines(lines):
    cleaned = []
    for line in lines:
        line = re.sub(r'[|•]', ',', line)
        line = re.sub(r'[^\w\s,#+.&/-]', '', line)
        line = re.sub(r'\s+', ' ', line).strip()
        if line:
            skills = re.split(r'[\s/&]+', line)
            cleaned.extend([s.strip() for s in skills if s.strip()])
    return cleaned

def extract_flat_skills(lines):
    flat = []
    for line in lines:
        flat.extend([s.strip() for s in re.split(r'[|,;•]', line) if s.strip()])
    return list(set(flat))

# ------------------ SECTION HEADERS ------------------ #
SECTION_PATTERNS = {
    "education": r"\b(education|academic|qualification|degree)\b",
    "experience": r"\b(experience|work|employment|job history|professional background)\b",
    "skills": r"\b(Skills|skills|technical skills|key skills|competencies|expertise|technologies|key skills |skills and expertise|core skills|Skills|SKILLS)\b",
    "projects": r"\b(projects|portfolio|works)\b",
    "certifications": r"\b(certifications|certificates|accreditations)\b",
    "summary": r"\b(summary|profile|objective|about me|professional summary)\b",
    "languages": r"\b(language|languages|known languages|spoken languages)\b"
}

# ------------------ ✅ UPDATED Experience/Section Parsing (COLUMN-AWARE) ------------------ #
def extract_sections_with_pymupdf(file_path):
    """
    Column-aware sectionizer:
    - Splits blocks into left/right columns by x0 vs midline
    - Processes each column top-to-bottom
    - Detects section headers by bold/size + regex match
    """
    parsed_sections = {k: [] for k in SECTION_PATTERNS.keys()}
    parsed_sections["others"] = []

    doc = fitz.open(file_path)
    current_section = "others"

    for page in doc:
        d = page.get_text("dict")
        blocks = d.get("blocks", []) or []

        # Determine midline for this page
        mid_x = page.rect.width / 2.0

        left_col_blocks, right_col_blocks = [], []
        for block in blocks:
            if "lines" not in block:
                continue
            x0 = block.get("bbox", [0, 0, 0, 0])[0]
            (left_col_blocks if x0 < mid_x else right_col_blocks).append(block)

        # process left then right column
        for col_blocks in (left_col_blocks, right_col_blocks):
            for block in sorted(col_blocks, key=lambda b: b["bbox"][1]):  # sort by y0
                lines = block.get("lines", [])
                for line in lines:
                    line_text = ""
                    is_bold = False
                    font_size = 0.0
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        if "bold" in (span.get("font", "").lower()):
                            is_bold = True
                        try:
                            font_size = max(font_size, float(span.get("size", 0)))
                        except Exception:
                            pass

                    line_text = line_text.strip()
                    if not line_text:
                        continue

                    # Identify section headers
                    if len(line_text.split()) <= 7:
                        for section, pattern in SECTION_PATTERNS.items():
                            if re.search(pattern, line_text.lower(), re.IGNORECASE):
                                if is_bold or font_size > 11:
                                    current_section = section
                                    break

                    parsed_sections[current_section].append(line_text)

    # Final cleanup
    final_sections = {}
    for section, lines in parsed_sections.items():
        cleaned = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line).strip()
            if line:
                cleaned.append(line)
        final_sections[section] = "\n".join(cleaned)

    return final_sections

# Keep the original parse_resume_pdf function for backward compatibility
def parse_resume_pdf(file_path):
    parsed_resume = {k: [] for k in SECTION_PATTERNS.keys()}
    parsed_resume["others"] = []

    doc = fitz.open(file_path)
    current_section = "others"

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                is_bold = False
                font_size = 0
                for span in line["spans"]:
                    line_text += span["text"]
                    if "bold" in span["font"].lower():
                        is_bold = True
                    font_size = max(font_size, span["size"])

                line_text = line_text.strip()
                if not line_text:
                    continue

                # Switch section if bold or heading matches
                if is_bold or font_size > 11:
                    for section, pattern in SECTION_PATTERNS.items():
                        if re.search(pattern, line_text.lower(), re.IGNORECASE):
                            current_section = section
                            break

                parsed_resume[current_section].append(line_text)

    final_resume = {}
    for section, lines in parsed_resume.items():
        cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in lines if line.strip()]
        if section == "skills":
            skill_text = "\n".join(cleaned_lines)
            final_resume[section] = extract_skills(skill_text)
        else:
            final_resume[section] = "\n".join(cleaned_lines)

    return final_resume

def naive_split_sections_from_text(text: str):
    """Very lightweight fallback when structured parse fails."""
    try:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        buckets = {k: [] for k in SECTION_PATTERNS.keys()}
        buckets["others"] = []
        current = "others"
        for ln in lines:
            matched = None
            for sec, pat in SECTION_PATTERNS.items():
                if re.search(pat, ln, re.IGNORECASE):
                    matched = sec
                    break
            if matched:
                current = matched
                continue
            buckets[current].append(ln)
        out = {}
        for k, vals in buckets.items():
            out[k] = "\n".join(vals)
        return out
    except Exception:
        return {k: "" for k in list(SECTION_PATTERNS.keys()) + ["others"]}

# ------------------ ✅ Experience Duration Calculator ------------------ #
def calculate_total_experience(experience_text):
    date_range_pattern = re.compile(
        r'(?P<start>(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
        r'Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2}[-/])\s*\d{4}|\d{4})\s*'
        r'(?:to|–|-|—|until|upto|through)\s*'
        r'(?P<end>(?:Present|Now|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
        r'Aug(?:ust)?|Sep(?:t)?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2}[-/])\s*\d{4}|\d{4}|Present|Now)',
        re.IGNORECASE
    )

    def parse_date(date_str):
        s = re.sub(r'\bSept\b', 'Sep', date_str, flags=re.IGNORECASE).strip()
        for fmt in ("%b %Y", "%B %Y", "%m/%Y", "%m-%Y", "%Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        return None

    now = datetime.now()
    intervals = []

    for m in date_range_pattern.finditer(experience_text):
        start_str = m.group('start').strip()
        end_str = m.group('end').strip()
        start_dt = parse_date(start_str)
        end_dt = now if re.search(r'present|now', end_str, re.IGNORECASE) else parse_date(end_str)
        if start_dt and end_dt and end_dt >= start_dt:
            if start_dt.year < 1980:
                continue
            if (end_dt.year - start_dt.year) > 20:
                continue
            intervals.append((start_dt, end_dt))

    if not intervals:
        return "0 years and 0 months"

    intervals.sort(key=lambda x: x[0])
    merged = []
    cur_s, cur_e = intervals[0]
    for s, e in intervals[1:]:
        if s <= cur_e:
            if e > cur_e:
                cur_e = e
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))

    total_months = 0
    for s, e in merged:
        delta = relativedelta(e, s)
        total_months += delta.years * 12 + delta.months

    earliest = merged[0][0]
    max_delta = relativedelta(now, earliest)
    max_months = max_delta.years * 12 + max_delta.months
    total_months = min(total_months, max_months)
    total_months = min(total_months, 50 * 12)

    years = total_months // 12
    months = total_months % 12
    return f"{years} years and {months} months"

# ------------------ Final Resume Processor ------------------ #
def process_resume(file_path):
    """Robust end-to-end parse that never raises and always returns JSON string."""
    try:
        combined, text_pdfplumber, text_pymupdf = get_combined_texts(file_path)

        # Contacts from combined text, but prefer pdfplumber for better linear text
        email = extract_email(text_pdfplumber or combined)
        phone = extract_phone(text_pdfplumber or combined)
        linkedin = extract_linkedin(text_pdfplumber or combined)
        github = extract_github(text_pdfplumber or combined)

        # Name from both sources
        name = verify_and_select_name(
            extract_name(text_pdfplumber or combined),
            extract_name(text_pymupdf or combined)
        )

        # Location (no network validation by default)
        location = extract_location(text_pdfplumber or combined, use_geopy=False)

        # Extract sections using PyMuPDF sectionizer (updated column-aware)
        sections_original = extract_sections_with_pymupdf(file_path)

        # Use refined PyMuPDF sectionizer ONLY for skills (fallback to original if empty)
        try:
            sections_refined = extract_sections_with_pymupdf_refined(file_path)
            refined_skills_text = (sections_refined or {}).get("skills", "")
        except Exception:
            refined_skills_text = ""

        skills_text = refined_skills_text or sections_original.get("skills", "")
        skills = extract_skills(skills_text)

        # Experience duration remains based on original sectionizer
        total_exp = calculate_total_experience(sections_original.get("experience", ""))

        result = {
            "personalInfo": {
                "name": name,
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "github": github,
                "location": location,
            },
            "skills": skills or [],
            "total_experience": total_exp or "0 years and 0 months",
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        fallback = {
            "personalInfo": {"name": "Unknown", "email": None, "phone": None, "linkedin": None, "github": None, "location": None},
            "skills": [],
            "total_experience": "0 years and 0 months",
            "error": str(e),
        }
        return json.dumps(fallback, ensure_ascii=False, indent=2)

# ------------------ Run ------------------ #
if __name__ == "__main__":
    # Batch CLI: process all PDFs in Resumes/ and write JSON into Output/
    base = os.path.dirname(__file__)
    resumes_dir = os.path.join(base, "Resumes")
    out_dir = os.path.join(base, "Output")
    wrong_dir = os.path.join(base, "wrong_output")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(wrong_dir, exist_ok=True)
    pdfs = [p for p in os.listdir(resumes_dir) if p.lower().endswith('.pdf')] if os.path.isdir(resumes_dir) else []
    if not pdfs:
        print("No PDFs found in Resumes/.")
    else:
        print(f"Parsing {len(pdfs)} resumes...")
        for i, fname in enumerate(sorted(pdfs), 1):
            pdf_path = os.path.join(resumes_dir, fname)
            try:
                result = process_resume(pdf_path)

                try:
                    obj = json.loads(result) if isinstance(result, str) else result
                except Exception:
                    obj = {}

                extracted_name = (((obj or {}).get("personalInfo", {}) or {}).get("name") or "").strip()
                skills_list = (obj or {}).get("skills") or []

                base_no_ext = os.path.splitext(fname)[0]
                if not extracted_name or extracted_name.lower() == "unknown":
                    extracted_name = base_no_ext

                safe_name = re.sub(r"[^A-Za-z0-9]+", "_", extracted_name).strip("_") or base_no_ext
                json_filename = f"{safe_name}_resume.json"

                name_tokens = [t for t in re.split(r"\s+", extracted_name.strip()) if t]
                starts_bad = (not extracted_name) or (not extracted_name[0].isalpha())
                too_many_words = len(name_tokens) > 3
                empty_skills = len(skills_list) == 0
                is_wrong = starts_bad or too_many_words or empty_skills

                with open(os.path.join(out_dir, json_filename), "w", encoding="utf-8") as f:
                    f.write(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))

                if is_wrong:
                    try:
                        dest_pdf = os.path.join(wrong_dir, fname)
                        if os.path.abspath(pdf_path) != os.path.abspath(dest_pdf):
                            if os.path.exists(dest_pdf):
                                name_root, name_ext = os.path.splitext(fname)
                                suffix = 1
                                while True:
                                    candidate = os.path.join(wrong_dir, f"{name_root}_{suffix}{name_ext}")
                                    if not os.path.exists(candidate):
                                        dest_pdf = candidate
                                        break
                                    suffix += 1
                            shutil.move(pdf_path, dest_pdf)
                        print(f"[{i}/{len(pdfs)}] WRONG -> moved to wrong_output: {fname}")
                    except Exception as move_err:
                        print(f"[{i}/{len(pdfs)}] WARN: failed to move wrong resume {fname}: {move_err}")
                else:
                    print(f"[{i}/{len(pdfs)}] OK: {fname}")
            except Exception as e:
                print(f"[{i}/{len(pdfs)}] FAIL: {fname} :: {e}")

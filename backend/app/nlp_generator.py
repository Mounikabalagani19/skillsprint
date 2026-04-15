
"""
NLP-based Q&A generator using NLTK.

Generates MCQ, True/False, and Fill-in-blank questions
from plain educational text (e.g. extracted from a PDF chapter).
No AI required — purely pattern matching + statistical NLP.
"""

import re
import random
import string
from collections import Counter

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag


# ──────────────────────────────────────────
# 1. Ensure NLTK data is available
# ──────────────────────────────────────────

def _ensure_nltk_data():
    needed = [
        ("tokenizers/punkt_tab",                   "punkt_tab"),
        ("taggers/averaged_perceptron_tagger_eng",  "averaged_perceptron_tagger_eng"),
        ("corpora/stopwords",                       "stopwords"),
    ]
    for path, pkg in needed:
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"[NLP] Downloading NLTK package: {pkg}")
            nltk.download(pkg, quiet=True)

_ensure_nltk_data()


# ──────────────────────────────────────────
# 2. Text Cleaning
# ──────────────────────────────────────────

def clean_text(text: str) -> str:
    """Fix common PDF extraction artefacts."""
    # Rejoin words split across lines by a hyphen
    text = re.sub(r'([a-z])-\s*\n\s*([a-z])', r'\1\2', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove non-ASCII
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Collapse multiple newlines into one
    text = re.sub(r'\n{2,}', '\n', text)
    # Remove lettered list markers like "(a)", "(b)", "(c)" — common in exam PDFs
    text = re.sub(r'\([a-z]\)\s*', ' ', text)
    # Remove numbered list markers like "1.", "2.", "(1)", "(2)" at line start
    text = re.sub(r'(?m)^\s*\(?[0-9]+[.)]\s*', '', text)
    return text.strip()


# ──────────────────────────────────────────
# 3. Extractors
# ──────────────────────────────────────────

def _extract_definitions(text: str) -> list[tuple[str, str]]:
    """
    Find (term, definition) pairs using linguistic patterns:
      • "X is a Y"
      • "X is defined as Y"
      • "X refers to Y"
      • "X means Y"
    Returns list of (term, definition) tuples (up to 15).
    """
    patterns = [
        # "X is/are [a/an/the] ..."
        r'\b([A-Z][a-zA-Z]{2,}(?:\s[A-Z][a-zA-Z]{2,}){0,3})\b'
        r'\s+(?:is|are)\s+(?:a|an|the)\s+([^.]{15,120})\.',
        # "X is defined as ..."  /  "X refers to ..."  /  "X means ..."
        r'\b([A-Z][a-zA-Z]{2,}(?:\s[a-zA-Z]{2,}){0,3})\b'
        r'\s+(?:is defined as|refers to|means)\s+([^.]{15,120})\.',
        # Lower-case term (min 3 chars): "set is ...", "variable is ..."
        r'\b([a-z][a-zA-Z]{2,}(?:\s[a-z][a-zA-Z]{2,}){0,2})\b'
        r'\s+(?:is|are)\s+(?:a|an)\s+([^.]{15,100})\.',
        # "X stores Y" pattern (e.g. "dictionary stores data in the form of key-value pairs")
        r'\b([a-z][a-zA-Z]{2,})\b'
        r'\s+stores\s+([^.]{15,120})\.',
    ]
    # Words that must never appear as a question term.
    # Covers pronouns, demonstratives, relative pronouns, generic nouns and
    # common sentence-starting words that regex picks up as false positives.
    _BAD_TERMS = {
        # Pronouns / demonstratives / relative (all lowercase — compared via key.lower())
        'this', 'that', 'these', 'those', 'there', 'here', 'which', 'what',
        'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'it', 'its',
        'they', 'their', 'them', 'he', 'she', 'we', 'you', 'the', 'such',
        'each', 'both', 'all', 'any', 'some', 'one', 'other', 'another',
        'then', 'thus', 'hence', 'also', 'now', 'yet', 'still', 'well',
        # Generic nouns that appear at sentence start and yield bad definitions
        'output', 'input', 'cost', 'price', 'level', 'process', 'method',
        'approach', 'factor', 'area', 'part', 'role', 'scope', 'nature',
        'purpose', 'result', 'concept', 'theory', 'aspect', 'type', 'types',
        'function', 'use', 'need', 'goal', 'aim', 'task', 'step', 'point',
        'example', 'case', 'way', 'form', 'basis', 'source', 'effect',
        'impact', 'value', 'amount', 'number', 'rate', 'size', 'term',
        'feature', 'benefit', 'issue', 'problem', 'solution', 'analysis',
        'information', 'data', 'knowledge', 'revenue', 'profit', 'loss',
    }

    # Definitions that start with these words are too vague to be useful
    _VAGUE_DEFN_STARTERS = re.compile(
        r'^(?:important|basic|major|main|key|certain|various|general|common|'
        r'specific|particular|special|significant|essential|critical|primary|'
        r'fundamental|typical|useful|effective|the manager|the process|'
        r'part of|used to|used for|also|often|always|usually)\b',
        re.IGNORECASE
    )

    results: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text):
            term = m.group(1).strip()
            defn = m.group(2).strip()
            key  = term.lower()

            # ── Reject bad terms ──────────────────────────────────────────
            if key in _BAD_TERMS:
                continue
            # Must be purely alphabetic (spaces allowed for multi-word terms)
            if not re.match(r'^[A-Za-z][A-Za-z ]*$', term):
                continue
            # Single-word terms must be at least 4 characters
            words_in_term = term.split()
            if len(words_in_term) == 1 and len(term) < 4:
                continue
            # No more than 3 words
            if len(words_in_term) > 3:
                continue

            # ── Reject bad definitions ────────────────────────────────────
            # Skip if definition contains a question mark (mid-sentence fragment)
            if '?' in defn:
                continue
            # Skip if definition contains lettered list markers like "(a)", "(b)"
            if re.search(r'\([a-z]\)', defn):
                continue
            # Skip definitions that are too short
            if len(defn.strip()) < 20:
                continue
            # Skip vague / non-specific definitions
            if _VAGUE_DEFN_STARTERS.match(defn):
                continue

            if key not in seen:
                seen.add(key)
                results.append((term, defn))
    return results[:15]
    return results[:15]


def _extract_enumerations(text: str) -> list[tuple[str, list[str]]]:
    """
    Find (category, [item, ...]) patterns:
      • "X includes A, B, and C"
      • "types of X are A, B, C"
      • "X can be A, B or C"
    """
    patterns = [
        r'(?:types|kinds|forms|examples|categories) of ([a-zA-Z ]{3,40}?)'
        r'\s+(?:are|include|is)\s*:?\s*([A-Za-z][A-Za-z, ]+?)(?=[.;\n])',
        r'([A-Za-z ]{3,40}?)\s+(?:includes|contains|consists of|can be|may be)\s*:?\s*'
        r'([A-Za-z][A-Za-z, ]+?)(?=[.;\n])',
    ]
    _ARTICLES = re.compile(r'^(a|an|the)\s+', re.IGNORECASE)
    results: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            category  = _ARTICLES.sub('', m.group(1).strip())  # strip 'A set' -> 'set'
            items_raw = m.group(2).strip()
            items = [i.strip() for i in re.split(r',\s*(?:and|or)?\s*', items_raw) if i.strip()]
            # Filter out single-character items (e.g. bracket symbols like '[', '(')
            items = [i for i in items if len(i) > 1]
            if len(items) >= 3 and category.lower() not in seen:
                seen.add(category.lower())
                results.append((category, items[:6]))
    return results[:8]


def _extract_true_false_sentences(text: str) -> list[str]:
    """
    Pick factual declarative sentences good for True/False questions:
      • Length between 40–150 chars
      • Contains a factual verb (is/are/was/were/has/have/can)
      • Not a question, not a negation
    """
    sentences = sent_tokenize(text)
    result: list[str] = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 40 or len(sent) > 150:
            continue
        if sent.endswith('?'):
            continue
        if ' not ' in sent.lower() or "n't" in sent.lower():
            continue
        # Skip sentences that look like a section header glued to content:
        # e.g. "Tuple Definition A tuple is an immutable..."
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]', sent):
            continue
        # Skip sentences beginning with section-label words
        if re.match(r'^(Definition|Example|Note|Summary|Key|Types|Important|Overview|Introduction)\b',
                    sent, re.IGNORECASE):
            continue
        if re.search(r'\b(?:is|are|was|were|has|have|can|will|should|must)\b',
                     sent, re.IGNORECASE):
            result.append(sent)
    return result[:20]


def _extract_key_terms(text: str) -> list[str]:
    """
    Extract the top-30 meaningful nouns using NLTK POS tagging.
    Used as a distractor pool for MCQs.
    """
    stop = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    nouns = [
        word for word, pos in tagged
        if pos in ('NN', 'NNS', 'NNP', 'NNPS')
        and word.lower() not in stop
        and len(word) > 3
        and word.isalpha()
    ]
    freq = Counter(nouns)
    return [term for term, _ in freq.most_common(30)]


# ──────────────────────────────────────────
# 4. Distractor Helper
# ──────────────────────────────────────────

_FALLBACK_DISTRACTORS = [
    "None of the above",
    "All of the above",
    "Cannot be determined",
    "Not applicable",
]

def _make_distractors(correct: str, pool: list[str], n: int = 3) -> list[str]:
    """Pick n items from pool that are not the correct answer."""
    candidates = [p for p in pool if p.lower() != correct.lower() and len(p) > 2]
    random.shuffle(candidates)
    chosen = candidates[:n]
    # Pad with fallbacks if pool is too small
    fb_idx = 0
    while len(chosen) < n:
        chosen.append(_FALLBACK_DISTRACTORS[fb_idx % len(_FALLBACK_DISTRACTORS)])
        fb_idx += 1
    return chosen


def _question_type_targets(num_questions: int) -> tuple[int, int, int]:
    """Return target counts for (mcq, fill_blank, true_false)."""
    pattern = ["mcq"] * 5 + ["fill_blank"] * 4 + ["true_false"]
    mcq_target = 0
    fill_target = 0
    true_false_target = 0

    for index in range(max(0, num_questions)):
        question_type = pattern[index % len(pattern)]
        if question_type == "mcq":
            mcq_target += 1
        elif question_type == "fill_blank":
            fill_target += 1
        else:
            true_false_target += 1

    return mcq_target, fill_target, true_false_target


# ──────────────────────────────────────────
# 5. Main Generator
# ──────────────────────────────────────────

def generate_questions(text: str, num_questions: int = 15) -> list[dict]:
    """
    Generate a list of questions from educational text.

    Each question dict has:
        type        : "mcq" | "true_false" | "fill_blank"
        question    : str
        options     : list[str]  (empty for fill_blank)
        answer      : str        (correct answer or "True"/"False")
        explanation : str

    Parameters
    ----------
    text          : plain text extracted from a PDF
    num_questions : max number of questions to return
    """
    text = clean_text(text)

    definitions = _extract_definitions(text)
    enumerations = _extract_enumerations(text)
    tf_sentences = _extract_true_false_sentences(text)
    key_terms = _extract_key_terms(text)

    term_names = [definition[0] for definition in definitions]
    defn_values = [definition[1] for definition in definitions]

    mcq_questions: list[dict] = []
    fill_blank_questions: list[dict] = []
    true_false_questions: list[dict] = []

    # Build definition-based MCQ and fill-in-the-blank candidates.
    shuffled_defs = list(definitions)
    random.shuffle(shuffled_defs)

    for idx, (term, defn) in enumerate(shuffled_defs):
        concept = term.lower()
        other_defns = [value for value in defn_values if value.lower() != defn.lower()]
        other_terms = [value for value in term_names if value.lower() != concept]

        if idx % 2 == 0 and len(other_defns) >= 3:
            distractors = _make_distractors(defn, other_defns, 3)
            options = [defn] + distractors
            random.shuffle(options)
            mcq_questions.append({
                "type": "mcq",
                "question": f"What is {term}?",
                "options": options,
                "answer": defn,
                "explanation": f"{term} is defined as: {defn}",
                "_concept": concept,
            })
        else:
            short_def = (defn[:60] + "…") if len(defn) > 60 else defn
            fill_blank_questions.append({
                "type": "fill_blank",
                "question": f"__________ is {short_def}",
                "options": [],
                "answer": term,
                "explanation": f"{term} is {defn}",
                "_concept": concept,
            })

        short_defn = (defn[:80] + "…") if len(defn) > 80 else defn
        noun_pool = [
            key_term for key_term in key_terms
            if key_term.isalpha() and len(key_term) >= 4 and key_term.lower() != concept
        ]
        distractors = _make_distractors(term, other_terms + noun_pool, 3)
        options = [term] + distractors
        random.shuffle(options)
        mcq_questions.append({
            "type": "mcq",
            "question": f"Which data type is described as: '{short_defn}'?",
            "options": options,
            "answer": term,
            "explanation": f"{term} is defined as: {defn}",
            "_concept": concept,
        })

    for category, items in enumerations:
        cat_key = category.lower()
        correct = random.choice(items)
        distractors = _make_distractors(correct, term_names + key_terms, 3)
        options = [correct] + distractors
        random.shuffle(options)
        mcq_questions.append({
            "type": "mcq",
            "question": f"Which of the following is a type / component of {category}?",
            "options": options,
            "answer": correct,
            "explanation": f"{category} includes: {', '.join(items)}",
            "_concept": cat_key,
        })

    _TF_STOP = {
        'which', 'these', 'those', 'their', 'there', 'where', 'while',
        'about', 'often', 'every', 'first', 'other', 'being', 'would',
        'could', 'using', 'since', 'after', 'before', 'stored', 'stores',
        'value', 'values', 'allows', 'python', 'types', 'data'
    }

    tf_seen: set[str] = set()
    for sent in tf_sentences:
        sent_lower = sent.lower()
        words = [
            word for word in re.findall(r'\b[a-z]{5,}\b', sent_lower)
            if word not in _TF_STOP
        ]
        concept = '|'.join(words[:3]) or sent_lower[:40]
        if concept in tf_seen:
            continue
        tf_seen.add(concept)
        true_false_questions.append({
            "type": "true_false",
            "question": sent,
            "options": ["True", "False"],
            "answer": "True",
            "explanation": "This statement appears directly in the source material.",
            "_concept": concept,
        })

    mcq_target, fill_target, true_false_target = _question_type_targets(num_questions)

    def _select_questions(
        candidates: list[dict],
        target: int,
        used_concepts: set[str],
        allow_global_reuse: bool = False,
    ) -> list[dict]:
        selected: list[dict] = []
        local_concepts: set[str] = set()

        # First pass: prefer concepts not used by earlier buckets.
        for candidate in candidates:
            if len(selected) >= target:
                break
            concept = candidate["_concept"]
            if concept in used_concepts or concept in local_concepts:
                continue
            local_concepts.add(concept)
            selected.append(candidate)

        # Second pass: if needed, reuse concepts from other buckets but never
        # duplicate the same concept twice inside the current bucket.
        if allow_global_reuse and len(selected) < target:
            for candidate in candidates:
                if len(selected) >= target:
                    break
                concept = candidate["_concept"]
                if concept in local_concepts:
                    continue
                local_concepts.add(concept)
                selected.append(candidate)

        used_concepts.update(local_concepts)
        return selected

    random.shuffle(mcq_questions)
    random.shuffle(fill_blank_questions)
    random.shuffle(true_false_questions)

    used_concepts: set[str] = set()
    questions: list[dict] = []
    questions.extend(_select_questions(fill_blank_questions, fill_target, used_concepts))
    questions.extend(_select_questions(mcq_questions, mcq_target, used_concepts, allow_global_reuse=True))
    questions.extend(_select_questions(true_false_questions, true_false_target, used_concepts, allow_global_reuse=True))

    if len(questions) < num_questions:
        for candidate in mcq_questions + fill_blank_questions + true_false_questions:
            if len(questions) >= num_questions:
                break
            concept = candidate["_concept"]
            if concept in used_concepts:
                continue
            used_concepts.add(concept)
            questions.append(candidate)

    for question in questions:
        question.pop("_concept", None)

    random.shuffle(questions)
    return questions[:num_questions]

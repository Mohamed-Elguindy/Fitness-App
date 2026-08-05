from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import pdfplumber


APP_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIRS = {
    "nutrition": APP_ROOT / "data" / "nutrition_papers",
    "training": APP_ROOT / "data" / "training_papers",
}
REPORT_PATH = APP_ROOT / "experiments" / "reports" / "phase1_chunking_report.md"
CHUNKS_JSONL_PATH = APP_ROOT / "experiments" / "reports" / "phase1_hybrid_chunks.jsonl"

LOCAL_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
TARGET_FIXED_TOKENS = 800
FIXED_OVERLAP_TOKENS = 150
TARGET_HYBRID_TOKENS = 750
HYBRID_OVERLAP_TOKENS = 100
MAX_STRUCTURE_TOKENS = 1000
MIN_CHUNK_TOKENS = 50
SEMANTIC_BREAK_PERCENTILE = 85

SECTION_HEADINGS = {
    "abstract",
    "acknowledgements",
    "acknowledgments",
    "applications",
    "background",
    "competing interests",
    "conclusion",
    "conclusions",
    "conflict of interest",
    "conflicts of interest",
    "discussion",
    "funding",
    "introduction",
    "limitations",
    "method",
    "methods",
    "practical applications",
    "position statement",
    "position statements",
    "recommendations",
    "references",
    "results",
    "summary",
}
REFERENCE_SECTION_NAMES = {
    "references",
    "acknowledgements",
    "acknowledgments",
    "funding",
    "conflict of interest",
    "conflicts of interest",
    "competing interests",
}
TITLE_BY_FILE = {
    "ACSM-Progression-models-in-resistance-training-for-healthy-adults-2009.pdf": (
        "Progression Models in Resistance Training for Healthy Adults"
    ),
    "Effects of Resistance Training Frequency on Measures of Muscle Hypertrophy - A Systematic Review and Meta-Analysis.pdf": (
        "Effects of Resistance Training Frequency on Measures of Muscle Hypertrophy: A Systematic Review and Meta-Analysis"
    ),
    "hukin-81-199.pdf": (
        "A Systematic Review of the Effects of Different Resistance Training Volumes on Muscle Hypertrophy"
    ),
    "ijerph-17-01285.pdf": (
        "A Systematic Review with Meta-Analysis of the Effect of Resistance Training on Whole-Body Muscle Growth in Healthy Adult Males"
    ),
    "oajsm-7-115.pdf": "Diagnosis and Prevention of Overtraining Syndrome: An Opinion on Education Strategies",
    "s12970-017-0173-z.pdf": (
        "International Society of Sports Nutrition Position Stand: Safety and Efficacy of Creatine Supplementation in Exercise, Sport, and Medicine"
    ),
    "s12970-017-0174-y.pdf": "International Society of Sports Nutrition Position Stand: Diets and Body Composition",
    "s12970-017-0177-8.pdf": "International Society of Sports Nutrition Position Stand: Protein and Exercise",
    "s12970-017-0189-4.pdf": "International Society of Sports Nutrition Position Stand: Nutrient Timing",
}


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class DocumentText:
    corpus: str
    source_file: str
    title: str
    parser: str
    pages: list[PageText]


@dataclass
class Chunk:
    strategy: str
    corpus: str
    source_file: str
    title: str
    section: str
    chunk_index: int
    text: str
    token_count: int


def build_token_counter() -> tuple[Callable[[str], int], str]:
    try:
        import tiktoken

        tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")

        def count_tiktoken(text: str) -> int:
            return len(tokenizer.encode(text))

        return count_tiktoken, "tiktoken:text-embedding-3-small"
    except Exception:
        return count_regex_tokens, "regex-word-fallback"


def count_regex_tokens(text: str) -> int:
    return len(re.findall(r"\b\w+(?:[-']\w+)?\b", text))


estimate_tokens, TOKEN_COUNTER_NAME = build_token_counter()
SEMANTIC_SPLITTER_STATUS = "not initialized"


def normalize_line(line: str) -> str:
    line = line.replace("\u00ad", "")
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"\s+([,.;:?!)])", r"\1", line)
    line = re.sub(r"([(])\s+", r"\1", line)
    line = re.sub(r"\b([A-Z])\s+([a-z]{2,})\b", r"\1\2", line)
    return line


def normalize_heading(line: str) -> str:
    clean = normalize_line(line)
    clean = re.sub(r"^\d+(\.\d+)*\s+", "", clean)
    clean = clean.strip(" :").lower()
    return clean


def is_heading(line: str) -> bool:
    clean = normalize_heading(line)
    if clean in SECTION_HEADINGS:
        return True
    if clean.startswith("abstract"):
        return True
    if len(clean.split()) <= 5 and clean in SECTION_HEADINGS:
        return True
    return False


def is_reference_section(section: str) -> bool:
    clean = normalize_heading(section)
    return clean in REFERENCE_SECTION_NAMES


def remove_repeated_page_noise(pages: list[list[str]]) -> list[list[str]]:
    normalized_pages = [[normalize_line(line) for line in page if normalize_line(line)] for page in pages]
    line_counts = Counter(line for page in normalized_pages for line in set(page))
    min_repeated = max(3, len(pages) // 2)

    cleaned_pages: list[list[str]] = []
    for page in normalized_pages:
        cleaned = []
        for line in page:
            is_page_number = bool(re.fullmatch(r"\d{1,4}", line))
            is_repeated_short_line = line_counts[line] >= min_repeated and len(line) < 120
            if is_page_number or is_repeated_short_line:
                continue
            cleaned.append(line)
        cleaned_pages.append(cleaned)
    return cleaned_pages


def should_continue_line(previous: str, current: str) -> bool:
    if previous.endswith((".", "?", "!", ":", ";")):
        return False
    if is_heading(current):
        return False
    if len(previous) < 45:
        return False
    return True


def join_wrapped_lines(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current = ""

    for line in lines:
        if not line:
            continue
        if is_heading(line):
            if current:
                paragraphs.append(current.strip())
                current = ""
            paragraphs.append(normalize_line(line))
            continue
        if current.endswith("-") and line[:1].islower():
            current = current[:-1] + line
        elif current and should_continue_line(current, line):
            current += " " + line
        else:
            if current:
                paragraphs.append(current.strip())
            current = line

    if current:
        paragraphs.append(current.strip())

    return "\n\n".join(paragraphs)


def parse_with_pdfplumber(path: Path) -> tuple[list[PageText], str]:
    raw_pages: list[list[str]] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(
                x_tolerance=2,
                y_tolerance=3,
                layout=True,
                x_density=7.25,
                y_density=13,
            ) or ""
            raw_pages.append(text.splitlines())

    cleaned_pages = remove_repeated_page_noise(raw_pages)
    pages = [
        PageText(page_number=index + 1, text=join_wrapped_lines(lines))
        for index, lines in enumerate(cleaned_pages)
    ]
    return pages, "pdfplumber-layout"


def parse_with_unstructured_if_available(path: Path) -> tuple[list[PageText], str] | None:
    try:
        from unstructured.partition.pdf import partition_pdf
    except Exception:
        return None

    elements = partition_pdf(
        filename=str(path),
        strategy="hi_res",
        infer_table_structure=True,
    )
    page_blocks: dict[int, list[str]] = {}
    for element in elements:
        text = normalize_line(str(element))
        if not text:
            continue
        page_number = int(getattr(getattr(element, "metadata", None), "page_number", 1) or 1)
        page_blocks.setdefault(page_number, []).append(text)

    pages = [
        PageText(page_number=page_number, text="\n\n".join(blocks))
        for page_number, blocks in sorted(page_blocks.items())
    ]
    return pages, "unstructured-hi-res"


def extract_pdf(path: Path, corpus: str) -> DocumentText:
    parsed = parse_with_unstructured_if_available(path) or parse_with_pdfplumber(path)
    pages, parser = parsed
    title = TITLE_BY_FILE.get(path.name) or infer_title_from_first_page(pages[0].text if pages else path.stem)
    return DocumentText(corpus=corpus, source_file=path.name, title=title, parser=parser, pages=pages)


def infer_title_from_first_page(text: str) -> str:
    lines = [normalize_line(line) for line in text.splitlines() if normalize_line(line)]
    candidates: list[str] = []
    for index, line in enumerate(lines[:40]):
        lower = line.lower()
        if any(skip in lower for skip in ["copyright", "journal", "doi", "license", "open access", "abstract"]):
            continue
        if len(line) < 8 or re.fullmatch(r"\d+[-–]\d+", line):
            continue
        candidates.append(line)
        if len(candidates) >= 2 or (index > 8 and candidates):
            break
    return " ".join(candidates)[:180] if candidates else "Untitled"


def split_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = [("front matter", [])]
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        first_line = block.splitlines()[0].strip()
        if is_heading(first_line):
            section_name = normalize_heading(first_line)
            sections.append((section_name, []))
            remaining = "\n".join(block.splitlines()[1:]).strip()
            if remaining:
                sections[-1][1].append(remaining)
        else:
            sections[-1][1].append(block)

    return [
        (name, "\n\n".join(blocks).strip())
        for name, blocks in sections
        if "\n\n".join(blocks).strip() and not is_reference_section(name)
    ]


def token_windows(words: list[str], target: int, overlap: int) -> list[str]:
    if not words:
        return []
    chunks = []
    start = 0
    step = max(1, target - overlap)
    while start < len(words):
        end = min(len(words), start + target)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step
    return chunks


def make_chunk(
    strategy: str,
    doc: DocumentText,
    section: str,
    chunk_index: int,
    text: str,
) -> Chunk:
    text = re.sub(r"\s+", " ", text).strip()
    return Chunk(
        strategy=strategy,
        corpus=doc.corpus,
        source_file=doc.source_file,
        title=doc.title,
        section=section,
        chunk_index=chunk_index,
        text=text,
        token_count=estimate_tokens(text),
    )


def merge_micro_chunks(chunks: list[Chunk], min_tokens: int = MIN_CHUNK_TOKENS) -> list[Chunk]:
    if len(chunks) > 1 and chunks[0].token_count < min_tokens:
        second = chunks[1]
        combined_text = f"{chunks[0].text} {second.text}".strip()
        chunks[1] = Chunk(
            strategy=second.strategy,
            corpus=second.corpus,
            source_file=second.source_file,
            title=second.title,
            section=second.section,
            chunk_index=second.chunk_index,
            text=combined_text,
            token_count=estimate_tokens(combined_text),
        )
        chunks = chunks[1:]

    merged: list[Chunk] = []
    for chunk in chunks:
        if chunk.token_count >= min_tokens or not merged:
            merged.append(chunk)
            continue

        previous = merged[-1]
        combined_text = f"{previous.text} {chunk.text}".strip()
        merged[-1] = Chunk(
            strategy=previous.strategy,
            corpus=previous.corpus,
            source_file=previous.source_file,
            title=previous.title,
            section=previous.section,
            chunk_index=previous.chunk_index,
            text=combined_text,
            token_count=estimate_tokens(combined_text),
        )

    for index, chunk in enumerate(merged):
        chunk.chunk_index = index
    return merged


def fixed_chunks(doc: DocumentText) -> list[Chunk]:
    text = "\n\n".join(page.text for page in doc.pages)
    words = re.findall(r"\S+", text)
    chunks = [
        make_chunk("fixed", doc, "full text", index, chunk)
        for index, chunk in enumerate(token_windows(words, TARGET_FIXED_TOKENS, FIXED_OVERLAP_TOKENS))
    ]
    return merge_micro_chunks(chunks)


def structure_chunks(doc: DocumentText) -> list[Chunk]:
    text = "\n\n".join(page.text for page in doc.pages)
    chunks: list[Chunk] = []
    for section, body in split_sections(text):
        words = re.findall(r"\S+", body)
        pieces = token_windows(words, MAX_STRUCTURE_TOKENS, FIXED_OVERLAP_TOKENS)
        for piece in pieces:
            chunks.append(make_chunk("structure", doc, section, len(chunks), piece))
    return merge_micro_chunks(chunks)


def sentence_groups(text: str, target_tokens: int, overlap_tokens: int) -> list[str]:
    sentences = split_sentences(text)
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_tokens = estimate_tokens(sentence)
        if current and current_tokens + sentence_tokens > target_tokens:
            chunks.append(" ".join(current).strip())
            overlap: list[str] = []
            overlap_count = 0
            for prior in reversed(current):
                prior_tokens = estimate_tokens(prior)
                if overlap_count + prior_tokens > overlap_tokens:
                    break
                overlap.insert(0, prior)
                overlap_count += prior_tokens
            current = overlap
            current_tokens = overlap_count
        current.append(sentence)
        current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def cap_oversized_pieces(pieces: list[str], target_tokens: int, overlap_tokens: int) -> list[str]:
    capped: list[str] = []
    for piece in pieces:
        if estimate_tokens(piece) <= target_tokens:
            capped.append(piece)
        else:
            for sentence_piece in sentence_groups(piece, target_tokens, overlap_tokens):
                if estimate_tokens(sentence_piece) <= target_tokens:
                    capped.append(sentence_piece)
                else:
                    capped.extend(greedy_token_budget_groups(sentence_piece, target_tokens, overlap_tokens))
    return capped


def greedy_token_budget_groups(text: str, target_tokens: int, overlap_tokens: int) -> list[str]:
    words = re.findall(r"\S+", text)
    chunks: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join([*current, word])
        if current and estimate_tokens(candidate) > target_tokens:
            chunks.append(" ".join(current).strip())
            overlap_words: list[str] = []
            for prior in reversed(current):
                overlap_candidate = " ".join([prior, *overlap_words])
                if estimate_tokens(overlap_candidate) > overlap_tokens:
                    break
                overlap_words.insert(0, prior)
            current = [*overlap_words, word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current).strip())
    return chunks


class LocalSemanticSplitter:
    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name, local_files_only=True)

    def split_text(self, text: str) -> list[str]:
        sentences = split_sentences(text)
        if len(sentences) <= 2:
            return [text]

        embeddings = self.model.encode(sentences, normalize_embeddings=True)
        distances = []
        for index in range(len(embeddings) - 1):
            similarity = float(embeddings[index] @ embeddings[index + 1])
            distances.append(1.0 - similarity)

        if not distances:
            return [text]

        threshold = float(statistics.quantiles(distances, n=100)[SEMANTIC_BREAK_PERCENTILE - 1])
        chunks: list[str] = []
        current: list[str] = []
        current_tokens = 0

        for index, sentence in enumerate(sentences):
            sentence_tokens = estimate_tokens(sentence)
            should_break = False
            if current and index > 0:
                semantic_break = distances[index - 1] >= threshold
                size_break = current_tokens + sentence_tokens > TARGET_HYBRID_TOKENS
                should_break = semantic_break or size_break

            if should_break:
                chunks.append(" ".join(current).strip())
                current = []
                current_tokens = 0

            current.append(sentence)
            current_tokens += sentence_tokens

        if current:
            chunks.append(" ".join(current).strip())

        return chunks


_LOCAL_SEMANTIC_SPLITTER: LocalSemanticSplitter | None = None
_LOCAL_SEMANTIC_LOAD_FAILED = False


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text) if sentence.strip()]


def local_semantic_groups_if_available(text: str) -> list[str] | None:
    global SEMANTIC_SPLITTER_STATUS, _LOCAL_SEMANTIC_LOAD_FAILED, _LOCAL_SEMANTIC_SPLITTER
    if _LOCAL_SEMANTIC_LOAD_FAILED:
        return None
    try:
        if _LOCAL_SEMANTIC_SPLITTER is None:
            _LOCAL_SEMANTIC_SPLITTER = LocalSemanticSplitter()
            SEMANTIC_SPLITTER_STATUS = f"active:{LOCAL_EMBEDDING_MODEL}"
        return _LOCAL_SEMANTIC_SPLITTER.split_text(text)
    except Exception:
        _LOCAL_SEMANTIC_LOAD_FAILED = True
        SEMANTIC_SPLITTER_STATUS = f"fallback:could not load {LOCAL_EMBEDDING_MODEL}"
        return None


def hybrid_chunks(doc: DocumentText) -> list[Chunk]:
    text = "\n\n".join(page.text for page in doc.pages)
    chunks: list[Chunk] = []
    for section, body in split_sections(text):
        paragraphs = [para.strip() for para in body.split("\n\n") if para.strip()]
        normalized_body = "\n\n".join(paragraphs)
        if estimate_tokens(normalized_body) > TARGET_HYBRID_TOKENS:
            pieces = local_semantic_groups_if_available(normalized_body)
            if pieces is None:
                pieces = sentence_groups(normalized_body, TARGET_HYBRID_TOKENS, HYBRID_OVERLAP_TOKENS)
            else:
                pieces = cap_oversized_pieces(pieces, TARGET_HYBRID_TOKENS, HYBRID_OVERLAP_TOKENS)
        else:
            pieces = [normalized_body]

        for piece in pieces:
            chunks.append(make_chunk("hybrid", doc, section, len(chunks), piece))
    return merge_micro_chunks(chunks)


def load_documents() -> list[DocumentText]:
    docs: list[DocumentText] = []
    for corpus, folder in PAPER_DIRS.items():
        for path in sorted(folder.glob("*.pdf"), key=lambda item: item.name.lower()):
            docs.append(extract_pdf(path, corpus))
    return docs


def summarize_chunks(chunks: list[Chunk]) -> dict[str, str]:
    token_counts = [chunk.token_count for chunk in chunks]
    if not token_counts:
        return {"count": "0", "avg": "0", "min": "0", "max": "0", "p90": "0", "under_min": "0"}
    return {
        "count": str(len(chunks)),
        "avg": f"{statistics.mean(token_counts):.0f}",
        "min": str(min(token_counts)),
        "max": str(max(token_counts)),
        "p90": f"{statistics.quantiles(token_counts, n=10)[8]:.0f}" if len(token_counts) >= 10 else str(max(token_counts)),
        "under_min": str(sum(1 for count in token_counts if count < MIN_CHUNK_TOKENS)),
    }


def compact_sample(text: str, max_chars: int = 750) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars].rstrip() + ("..." if len(text) > max_chars else "")


def export_hybrid_jsonl(chunks: list[Chunk]) -> None:
    with CHUNKS_JSONL_PATH.open("w", encoding="utf-8") as output:
        for chunk in chunks:
            output.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def write_report(docs: list[DocumentText], all_chunks: dict[str, list[Chunk]]) -> None:
    lines: list[str] = []
    lines.append("# Phase 1 Chunking Experiment Report")
    lines.append("")
    lines.append("This report compares local chunking strategies after lightweight PDF preprocessing.")
    lines.append("")
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- Token counter: `{TOKEN_COUNTER_NAME}`")
    lines.append(f"- Local embedding model: `{LOCAL_EMBEDDING_MODEL}`")
    lines.append(f"- Hybrid target tokens: `{TARGET_HYBRID_TOKENS}`")
    lines.append(f"- Semantic break percentile: `{SEMANTIC_BREAK_PERCENTILE}`")
    lines.append(f"- Minimum chunk tokens after merge: `{MIN_CHUNK_TOKENS}`")
    lines.append(f"- Local semantic splitter: `{SEMANTIC_SPLITTER_STATUS}`")
    lines.append(f"- Hybrid JSONL export: `{CHUNKS_JSONL_PATH}`")
    lines.append("")
    lines.append("## Source PDFs")
    lines.append("")
    lines.append("| Corpus | File | Pages | Parser | Title |")
    lines.append("|---|---|---:|---|---|")
    for doc in docs:
        lines.append(f"| {doc.corpus} | `{doc.source_file}` | {len(doc.pages)} | `{doc.parser}` | {doc.title} |")

    lines.append("")
    lines.append("## Strategy Summary")
    lines.append("")
    lines.append("| Strategy | Chunks | Avg Tokens | Min | Under 50 | P90 | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for strategy, chunks in all_chunks.items():
        summary = summarize_chunks(chunks)
        lines.append(
            f"| {strategy} | {summary['count']} | {summary['avg']} | {summary['min']} | "
            f"{summary['under_min']} | {summary['p90']} | {summary['max']} |"
        )

    lines.append("")
    lines.append("## Per-Corpus Summary")
    lines.append("")
    lines.append("| Strategy | Corpus | Chunks | Avg Tokens | Min | Under 50 | P90 | Max |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for strategy, chunks in all_chunks.items():
        for corpus in PAPER_DIRS:
            corpus_chunks = [chunk for chunk in chunks if chunk.corpus == corpus]
            summary = summarize_chunks(corpus_chunks)
            lines.append(
                f"| {strategy} | {corpus} | {summary['count']} | {summary['avg']} | {summary['min']} | "
                f"{summary['under_min']} | {summary['p90']} | {summary['max']} |"
            )

    lines.append("")
    lines.append("## Sample Chunks")
    for strategy, chunks in all_chunks.items():
        lines.append("")
        lines.append(f"### {strategy}")
        for corpus in PAPER_DIRS:
            sample = next((chunk for chunk in chunks if chunk.corpus == corpus and chunk.token_count > 80), None)
            if not sample:
                continue
            lines.append("")
            lines.append(f"**{corpus} sample**")
            lines.append("")
            lines.append(f"- Source: `{sample.source_file}`")
            lines.append(f"- Section: `{sample.section}`")
            lines.append(f"- Tokens: `{sample.token_count}`")
            lines.append("")
            lines.append("> " + compact_sample(sample.text))

    lines.append("")
    lines.append("## Initial Read")
    lines.append("")
    lines.append("- References and back-matter sections are filtered before chunk creation.")
    lines.append("- Micro-chunks under 50 tokens are merged into the previous chunk when possible.")
    lines.append("- Hybrid chunks keep section metadata and split oversized sections with local embedding similarity when the BGE model is available.")
    lines.append("- If the local embedding model cannot load, the script falls back to sentence-boundary splitting.")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    docs = load_documents()
    all_chunks = {
        "fixed": [chunk for doc in docs for chunk in fixed_chunks(doc)],
        "structure": [chunk for doc in docs for chunk in structure_chunks(doc)],
        "hybrid": [chunk for doc in docs for chunk in hybrid_chunks(doc)],
    }
    export_hybrid_jsonl(all_chunks["hybrid"])
    write_report(docs, all_chunks)
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {CHUNKS_JSONL_PATH}")
    print(f"token_counter: {TOKEN_COUNTER_NAME}")
    for strategy, chunks in all_chunks.items():
        summary = summarize_chunks(chunks)
        print(
            f"{strategy}: {summary['count']} chunks, avg={summary['avg']}, "
            f"min={summary['min']}, under50={summary['under_min']}, "
            f"p90={summary['p90']}, max={summary['max']}"
        )


if __name__ == "__main__":
    main()

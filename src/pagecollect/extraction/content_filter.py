from pagecollect.extraction.transform import HEADING_TAGS, PARAGRAPH_TAGS
from pagecollect.extraction.lang_util import get_text_lang

MIN_WORDS = 30       # The minimum words to be a meaningful text block 

def is_long_paragraph(text: str) -> bool:
    """
    Determine whether a text block is long enough to be treated as
    a meaningful paragraph
    """
    text = text.strip()
    if not text:
        return False
    
    lang = get_text_lang(text)
    if not lang:
        return False
    
    if lang in {"zh-cn","zh-tw", "ja", "ko"}:
        return len(text) >= MIN_WORDS
    else:
        return len(text.split()) >= MIN_WORDS

def filter_blocks(blocks: list[dict]) -> tuple[bool, list[dict]]:
    """
    Filter raw DOM blocks into document text blocks.
    Keep heading and long paragraph blocks
    """
    out_blocks = []
    has_long_paragraph = False
    for b in blocks:
        tag = (b.get("tag") or "").lower()
        text = (b.get("text") or "").strip()
        if not text:
            continue
        if tag in HEADING_TAGS:
            out_blocks.append(b)
        elif tag in PARAGRAPH_TAGS:
            if is_long_paragraph(text):
                out_blocks.append(b)
                has_long_paragraph = True
    return has_long_paragraph, out_blocks
import hashlib
from urllib.parse import urljoin, urlparse, urlunparse
from pagecollect.extraction.url_util import normalize_url, is_internal_link

# File extensions that are unlikely to be HTML pages
NON_HTML_EXT = (
    ".pdf", ".txt",
    ".zip", ".rar", ".7z",
    ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".mp3", ".mp4", ".avi", ".mov",
)

# Tag groups used throughout the extraction pipeline
HEADING_TAGS = {"h1", "h2", "h3"}
PARAGRAPH_TAGS = {"p", "blockquote", "pre", "code"}
CONTENT_TAGS = set().union(HEADING_TAGS, PARAGRAPH_TAGS)

def is_probably_html(url: str) -> bool:
    """
    Heuristic check for whether a URL likely points to an HTML page
    """
    path = urlparse(url).path.lower()
    return not path.endswith(NON_HTML_EXT)

def normalize_block(text):
    """
    Normalize a single block of extracted text
    """
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l]
    out_text = " ".join(lines)
    return out_text

def build_page_info(parsed_page: dict, page_url: str) -> dict | None:
    """
    Build a page representation from a parsed page
    """
    out_blocks = []
    blocks = parsed_page["blocks"]
    for blk in blocks:
        if blk["tag"] not in CONTENT_TAGS:
            continue
        blk["text"] = normalize_block(blk["text"])
        out_blocks.append(blk)

    inner_links = page_to_inner_links(parsed_page, page_url)
    doc = {
        "title":parsed_page["title"],
        "blocks":out_blocks,
        "inner_links":inner_links
    }
    return doc

def page_to_inner_links(parsed_page: dict, page_url: str) -> list[str]:
    """
     Convert raw link records into a list of normalized, internal URLs
    """
    inner_link_set = set()
    links = parsed_page["links"]
    for lnk in links:
        href = lnk["href"]
        href_url = normalize_url(href, page_url)
        if is_internal_link(href_url, page_url):
            inner_link_set.add(href_url)

    inner_links = list(inner_link_set)
    return inner_links


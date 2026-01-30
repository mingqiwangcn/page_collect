import langdetect
from datetime import datetime, timezone
from pagecollect.extraction.parse import parse_page
from pagecollect.extraction.transform import build_page_info
from pagecollect.extraction import url_filter, content_filter
from pagecollect.extraction.lang_util import get_text_lang
from urllib.parse import urlparse

def calc_word_count(text: str):
    """
    Count words in text, treating each \n as a separate unit to represent
    structural boundaries
    """
    size = len(text.replace("\n", " <NL> ").split())
    return size

def now_utc_iso() -> str:
    """
    Return the current UTC time in ISO.
    """
    return datetime.now(timezone.utc).isoformat()

def filter_inner_links(inner_links, url_rules):
    """
    Filter extracted internal links using URL rules
    """
    links_to_keep = []
    for inner_url in inner_links:
        if not url_filter.should_keep(inner_url, url_rules):
            continue
        links_to_keep.append(inner_url)
    return links_to_keep

def make_content_text(blocks: list):
    """
    Concatenate text from filtered blocks into a single document string.
    Blocks are joined with \n to keep structure (e.g. headings)
    """
    text_lst = []
    for blk in blocks:
        text = blk.get("text")
        text_lst.append(text)
    out_text = "\n".join(text_lst)
    return out_text

def infer_page_type(page_url, page_type_rules):
    """
    Infer page type from URL path rules.
    """
    page_type = None
    if page_type_rules:
        path = urlparse(page_url).path or "/"
        for rule in page_type_rules:
            m = rule["match"].rstrip("/") or "/"
            if path == m or path.startswith(m):
                return rule["type"]
    return None

def extract_page(html: str, url: str, rules: dict) -> dict:
    """
    End-to-end page extraction
    """
    parsed_page = parse_page(html)
    page_info = build_page_info(parsed_page, url)
    blocks = page_info["blocks"]
    doc = None
    has_content, kept_blocks = content_filter.filter_blocks(blocks)
    if has_content:
        content_text = make_content_text(kept_blocks)
        page_type = infer_page_type(url, rules.get("page_types"))
        doc = {
            "url":url,
            "title":page_info["title"],
            "content_text":content_text,
            "page_type":page_type,
            "parent_url":None,
            "meta":{
                "language":get_text_lang(content_text),
                "word_count":calc_word_count(content_text),
                "char_count":len(content_text),
                "fetched_at":now_utc_iso()
            }
        }
    inner_links = page_info["inner_links"]
    inner_links_to_keep = filter_inner_links(inner_links, rules.get("urls"))
    out_page = {
        "doc":doc,
        "inner_links":inner_links_to_keep
    }
    return out_page
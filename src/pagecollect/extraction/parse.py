from bs4 import BeautifulSoup

# Containers that typically contain navigation or boilerplate content
NOISE_PARENTS = {"nav", "header", "footer", "aside"}

# Tags considered as potential “content blocks”
TAGS = ["h1", "h2", "h3", "p", "li", "blockquote", "pre", "code"]

def make_soup(html: str) -> BeautifulSoup:
    """
    Create a BeautifulSoup object from raw HTML.
    Prefer the fast and robust `lxml` parser.
    Fall back to `html5lib` if parsing fails.
    """
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html5lib")

def get_stripped_text(el):
    """
    Extract text from an element, joining all stripped strings
    with newlines to preserve some structure.
    """
    return "\n".join(el.stripped_strings)

def get_title(soup):
    """
    Extract the page title from <title>, if present.
    """
    title = None
    if soup.title:
        title = get_stripped_text(soup.title)
    return title or None

def is_in_noise_container(el):
    """
    Determine whether an element is inside a “noise” container
    """
    for parent in el.parents:
        if parent.name in NOISE_PARENTS:
            return True
    return False

def get_blocks(soup):
    """
    Extract textual content blocks from the page body.
    """
    blocks = []
    for el in soup.body.find_all(TAGS):
        if is_in_noise_container(el):
            continue
        text = None
        if el.name in ["pre", "code"]:
            text = el.get_text()
        else:
            text = get_stripped_text(el)
        if not text:
            continue
        blocks.append(
            {
                "tag":el.name,
                "text":text
            }
        )
    return blocks

def get_links(soup):
    """
    Extract all anchor links from the page body
    """
    links = []
    for a in soup.body.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
        text = get_stripped_text(a)
        links.append(
            {
                "href":href,
                "text":text
            }
        )
    return links

def parse_page(html: str):
    """
    Parse raw HTML into a page representation
    """
    soup = make_soup(html)
    title = get_title(soup)
    blocks = get_blocks(soup)
    links = get_links(soup)
    output = {
        "title":title,
        "blocks":blocks,
        "links":links
    }
    return output
    
    

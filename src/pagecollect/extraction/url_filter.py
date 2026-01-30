from urllib.parse import urlparse

def should_keep(url: str,url_rules) -> bool:
    """
     Decide whether a normalized URL should be kept for crawling
    """
    url_info = urlparse(url)
    # If the url is a query, do not keep it 
    if url_info.query:
        return False
    
    path = url_info.path.rstrip("/") or "/"
    drop_prefix_lst = []
    if url_rules:
        drop_prefix_lst = url_rules.get("drop_prefix") or []
    for p in drop_prefix_lst:
        p = p.rstrip("/")
        if path == p or path.startswith(p + "/"):
            return False

    return True
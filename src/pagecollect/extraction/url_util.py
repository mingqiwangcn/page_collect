from urllib.parse import urljoin, urlparse, urlunparse

def get_normalized_host(url: str) -> str:
    """
     Extract and normalize the host from a URL
    """
    host = urlparse(url).netloc
    if host.startswith("www."):
        return host[4:]
    return host

def normalize_url(href: str, base_url: str) -> str:
    """
     Normalize a raw link into a canonical absolute URL
    """
    if not href:
        return None
    url = urljoin(base_url, href) if base_url else href
    url_info = urlparse(url)
    if url_info.scheme not in ["http", "https"]:
        return None
    
    url_info = url_info._replace(fragment="")
    path = url_info.path.rstrip("/") or "/"
    url_info = url_info._replace(path=path)
    
    out_url = urlunparse(url_info)
    return out_url

def is_internal_link(url: str, base_url: str) -> bool:
    """
     Check whether `url` belongs to the same host as `base_url`
    """
    return urlparse(url).netloc == urlparse(base_url).netloc
from pathlib import Path
import json
import asyncio
from pagecollect.storage.file_util import write_text_sync

class PageCache:
    """
    Persistent page cache.
    """
    def __init__(self, cache_file):
        self.cache = {}
        self.load_file(cache_file)
        out_path = Path(cache_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_file
        self.lock = asyncio.Lock()

    def load_file(self, cache_file: str):
        """
        Load an existing cache file into memory.
        """
        file_path = Path(cache_file)
        if not file_path.exists():
            return
        
        with open(cache_file, encoding="utf-8") as f:
            for line in f:
                page = json.loads(line)
                url = page["url"]
                self.cache[url] = page
    
    def exists_page(self, url: str) -> bool:
        """
        Check whether a page with this URL already exists in the cache.
        """
        return url in self.cache
    
    def get_inner_links(self, url: str) -> list[str]:
        """
        Retrieve cached inner links for a given URL
        """
        entry = self.cache.get(url)
        if not entry:
            return []
        return entry.get("inner_links", [])
    
    async def write(self, page_meta: dict):
        """
        Append a new page record to the cache file
        """
        text = json.dumps(page_meta, ensure_ascii=False)
        async with self.lock:
            await asyncio.to_thread(write_text_sync, self.cache_file, text)
    
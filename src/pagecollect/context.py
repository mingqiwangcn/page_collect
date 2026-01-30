from aiohttp import ClientSession
from pagecollect.crawl.robots import RobotsPolicy
from pagecollect.storage.page_cache import PageCache

class WorkerContext:
    """
    Shared runtime context for scrape workers
    """
    def __init__(self, session: ClientSession = None, 
                 robots_policy: RobotsPolicy = None,
                 page_cache: PageCache = None,
                 rules: dict = None
                 ):
        self.session = session
        self.robots_policy = robots_policy
        self.page_cache = page_cache
        self.rules = rules
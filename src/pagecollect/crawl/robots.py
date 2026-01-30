from urllib import robotparser
from urllib.parse import urlparse
import asyncio

class RobotsPolicy:
    """
    Per-host robots.txt cache and access policy.
    """
    def __init__(self):
        # Map: host -> RobotFileParser
        self.robot_cfg = {}

    async def allowed(self, url: str) -> bool:
        """
        Check whether `url` is allowed to be fetched according to robots.txt.
        """
        url_info = urlparse(url)
        host = url_info.netloc
        rp = self.robot_cfg.get(host)
        if rp is None:
            rp = robotparser.RobotFileParser()
            robots_url = f"{url_info.scheme}://{host}/robots.txt"
            rp.set_url(robots_url)
            try:
                await asyncio.to_thread(rp.read)
            except Exception:
                ...
                #If failed to read robots.txt, it will be allowed
                
            self.robot_cfg[host] = rp
        
        return rp.can_fetch("*", url)
    
    
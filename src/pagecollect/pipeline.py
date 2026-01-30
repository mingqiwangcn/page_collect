import logging
from pathlib import Path
import asyncio
from aiohttp import ClientSession
from asyncio import CancelledError

from pagecollect.context import WorkerContext
from pagecollect.frontier import Task, TaskQueue
from pagecollect.crawl.fetch import fetch_page
from pagecollect.extraction.extract import extract_page
from pagecollect.storage.json_writer import JsonWriter
from pagecollect.crawl.robots import RobotsPolicy
from pagecollect.storage.page_cache import PageCache
from pagecollect.extraction.transform import normalize_url
from pagecollect.storage.file_util import read_json
from pagecollect.extraction.url_util import get_normalized_host

logger = logging.getLogger(__name__)

def make_page_meta(url: str, out_page: dict) -> dict:
    """
    Build the minimal metadata stored in PageCache.
    """
    page_meta = {
        "url": url,
        "inner_links": out_page["inner_links"]
    }
    return page_meta

async def pipeline_worker(queue: TaskQueue, worker_context: WorkerContext, writer: JsonWriter):
    """
    Main workflow for a scrape worker
    """
    while (True):
        task = await queue.get()
        try:
            if queue.out_of_budget:
                continue

            inner_links = []
            if worker_context.page_cache.exists_page(task.url):
                #logger.info(f"Use cache, {task.url}")
                inner_links = worker_context.page_cache.get_inner_links(task.url)
            else:
                #logger.info(f"Fetching {task.url}")
                html = await fetch_page(task.url, worker_context)
                if html is None:
                    continue
                out_page = extract_page(html, task.url, worker_context.rules)
                page_meta = make_page_meta(task.url, out_page)
                await worker_context.page_cache.write(page_meta)
                doc = out_page["doc"]
                if doc:
                    doc["parent_url"] = task.parent_url
                    #logger.info(f"Writing documents, {task.url}")
                    await writer.write(doc)
                    queue.mark_collected()
                    if queue.collected_pages % 10 == 0:
                        logger.info(f"{queue.collected_pages} documents collected")
                else:
                    logger.info(f"No document from {task.url}")
                                
                inner_links = out_page["inner_links"]

            for lnk in inner_links:
                if not await worker_context.robots_policy.allowed(lnk):
                    continue
                new_task = Task(lnk, task.depth + 1, task.url)
                await queue.put(new_task)
            
        except CancelledError:
            raise
        except Exception as e:
            logger.error(f"Process Task failed, {task.url}, error: {e}")
            continue
        finally:
            queue.task_done()

def load_rules(url: str) -> dict:
    """
    Load site-specific extraction and URL rules based on host
    """
    host = get_normalized_host(url)

    def _load(rule_name, cfg_name=None):
        rule_path = Path(f"src/pagecollect/rules/{rule_name}/{cfg_name}.json")
        rules = None
        if rule_path:
            rules = read_json(rule_path)
        return rules
    
    rule_dict = {}

    page_type_rules = _load("page_types", host)
    page_type_rules.sort(key=lambda r: len(r["match"]), reverse=True)
    rule_dict["page_types"] = page_type_rules
    
    host_url_rule = _load("urls", host)
    if not host_url_rule:
        host_url_rule = _load("urls", "default")
    rule_dict["urls"] = host_url_rule
    
    return rule_dict

async def run_pipeline(
        start_url: str,
        out_file: str,
        num_workers,
        max_pages: int = None,
        max_depth: int = None,
        cache_file: str = None
):
    """
    Orchestrate the entire scraping pipeline.
    """
    url_queue = TaskQueue(max_pages=max_pages, max_depth=max_depth)

    nm_start_url = normalize_url(start_url, None)
    start_task = Task(nm_start_url, 0, None)
    await url_queue.put(start_task)

    page_cache = PageCache(cache_file)
    writer = JsonWriter(out_file)
    robots_policy = RobotsPolicy()

    rules = load_rules(nm_start_url)
    worker_lst = []
    
    n_wkrs = num_workers if num_workers and num_workers > 0 else 1
    session_lst = []
    for _ in range(n_wkrs):
        session = ClientSession()
        session_lst.append(session)
        worker_context = WorkerContext(session=session, 
                                       robots_policy=robots_policy, 
                                       page_cache=page_cache,
                                       rules=rules
                                       )
        worker = asyncio.create_task(pipeline_worker(url_queue, worker_context, writer))
        worker_lst.append(worker)

    await url_queue.join()

    for w in worker_lst:
        w.cancel()

    await asyncio.gather(*worker_lst, return_exceptions=True)

    for session in session_lst:
        await session.close()

    logger.info(f"Done, {url_queue.collected_pages} new documents collected in {out_file}")
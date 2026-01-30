import asyncio
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """
    A unit of work for a scrape worker.
    """
    url: str
    depth: int
    parent_url: str

class TaskQueue:
    """
    Frontier queue for scrape tasks with budget control.
    """
    def __init__(self, max_pages: int = None, max_depth: int = None):
        self.queue = asyncio.Queue()
        self.seen = set() # url already seen
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.collected_pages = 0
        self.out_of_budget = False
    
    def mark_collected(self):
        """
        Increment the count of successfully collected pages.
        """
        self.collected_pages += 1

    async def put(self, task: Task):
        """
        Enqueue a new task
        """
        if task.url in self.seen:
            return
        if self.max_pages is not None and self.collected_pages >= self.max_pages:
            if not self.out_of_budget:
                self.out_of_budget = True
                logger.info(f"Max Pages {self.max_pages} collected; Stopping")
        
            return
        if self.max_depth is not None and task.depth > self.max_depth:
            if not self.out_of_budget:
                self.out_of_budget = True
                logger.info(f"URL depth is greater than Max Depth {self.max_depth}; Stopping")
            return
        self.seen.add(task.url)
        await self.queue.put(task)
    
    async def get(self) -> Task:
        """
        Dequeue the next task
        """
        return await self.queue.get()

    def task_done(self):
        """
        Signal that a previously dequeued task has been fully processed.
        """
        self.queue.task_done()
    
    async def join(self):
        """
        Block until all enqueued tasks have been processed.
        """
        await self.queue.join()
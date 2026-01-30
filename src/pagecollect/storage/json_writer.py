import os
import json
from pathlib import Path
import asyncio
from pagecollect.storage.file_util import write_text_sync

class JsonWriter:
    def __init__(self, out_file: str):
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.out_file = out_file
        self.lock = asyncio.Lock()

    async def write(self, page: dict):
        """
        Write JSONL asynchronously
        """
        text = json.dumps(page, ensure_ascii=False)
        async with self.lock:
            await asyncio.to_thread(write_text_sync, self.out_file, text)
    
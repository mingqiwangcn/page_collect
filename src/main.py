import argparse
import asyncio
from pathlib import Path
import logging
from pagecollect.pipeline import run_pipeline

_FMT = "%(asctime)s | %(levelname)s | %(message)s"

def setup_logging(args, level=logging.INFO):
    """
    Configure application-wide logging
    """
    log_dir = Path(args.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    fmt = logging.Formatter(_FMT)

    fh = logging.FileHandler(args.log_file, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)

async def main(args):
    """
    Entry point for the async runtime
    """
    setup_logging(args)
    await run_pipeline(
       args.start_url,
       args.out_file,
       args.num_workers,
       max_pages=args.max_pages,
       max_depth=args.max_depth,
       cache_file=args.cache_file
    )

def get_args():
    """
    Get command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-url', type=str, required=True)
    parser.add_argument('--max-pages', type=int, default=100)
    parser.add_argument('--max-depth', type=int, default=3)
    parser.add_argument('--num-workers', type=int, default=2)
    parser.add_argument('--out-file', type=str, default="output/pages/out_pages.jsonl", required=True)
    parser.add_argument('--cache-file', type=str, default="output/cache/page_cache.jsonl")
    parser.add_argument('--log-file', type=str, default="output/logs/run.log", required=True)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    asyncio.run(main(args))

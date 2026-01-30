import asyncio
from pathlib import Path
from dotenv import load_dotenv
from pagecollect.crawl.fetch import fetch_page
from pagecollect.context import WorkerContext
from aiohttp import ClientSession

load_dotenv()

async def main():
    async def _fetch(url, out):
        async with ClientSession() as session:
            woker_context = WorkerContext(session=session)
            html = await fetch_page(url, woker_context)
            if not html:
                raise RuntimeError("Fetch failed")

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"Saved to {out.resolve()}")

    URL = "https://www.consumerfinance.gov/consumer-tools/debt-collection/"
    OUT = Path("tests/fixtures/cfpb_debt_collection.html")
    await _fetch(URL, OUT)

    URL = "https://www.consumerfinance.gov/find-a-housing-counselor"
    OUT = Path("tests/fixtures/find-a-housing-counselor.html")
    await _fetch(URL, OUT)

if __name__ == "__main__":
    asyncio.run(main())

# PageCollect — AI Collections Scraper

## 1. Overview
PageCollect is a lightweight, production-oriented web collection scraper designed for building high-quality, AI-ready document corpora from public websites. Unlike generic crawlers that indiscriminately mirror pages, PageCollect is opinionated about what to keep and how to structure it: it filters out low-signal and navigational pages, extracts only meaningful main content, and emits a clean, schema-stable JSONL dataset suitable for embedding, RAG, and downstream LLM workflows.

The system combines:

Rule-driven crawling – host-specific URL filters and page-type inference ensure that only semantically valuable pages are collected.

Content-aware extraction – boilerplate and navigation noise are removed, preserving only substantial, structured text.

AI-friendly output – each page is normalized into a single JSON object with explicit fields (title, content_text, page_type, parent_url, and rich metadata), making it immediately usable in vector databases and retrieval pipelines.

Production robustness – robots.txt compliance, rate limiting, retries, caching, and idempotent re-runs make the crawler safe and repeatable in real environments.

PageCollect is intended as the first stage of an AI collections pipeline: turning messy, heterogeneous websites into clean, typed, hierarchical document sets that LLM systems can reason over effectively. It bridges the gap between raw web content and structured knowledge sources, enabling reliable large-scale ingestion for search, RAG, and agentic systems.

---

## 2. How to Run

You can run the scraper either with Docker or directly in a Python environment.

### 2.1. Using Docker
Run the following in the repo folder
```bash
docker build -t page_collect .
```
```bash
docker run --rm \
  -v "$(pwd):/app" \
  page_collect \
  --start-url https://www.consumerfinance.gov/ \
  --max-pages 100 \
  --max-depth 3 \
  --num-workers 3 \
  --out-file output/pages/out_pages.jsonl \
  --cache-file output/cache/page_cache.jsonl \
  --log-file output/logs/run.log
```
The output pages is in `out-file`

### 2.2. Without Docker

Create a Conda environment with Python 3.10:
```bash
conda create -n page_collect python=3.10
conda activate page_collect

pip install -r requirements.txt

python src/main.py \
  --start-url https://www.consumerfinance.gov/ \
  --max-pages 100 \
  --max-depth 3 \
  --num-workers 3 \
  --out-file output/pages/out_pages.jsonl \
  --cache-file output/cache/page_cache.jsonl \
  --log-file output/logs/run.log
```

## 3. Data Schema
The output file is specified by --out-file.
It is a JSONL file where each line is a single JSON object:
```bash
{
  "url": "the url of the web page",
  "title": "the title of the page",
  "content_text": "the main body text of the page",
  "page_type": "the page type enum",
  "parent_url": "the url of the parent page; helps provide upstream context",
  "meta": {
    "language": "language code from langdetect",
    "word_count": "number of words in content_text",
    "char_count": "number of characters in content_text",
    "fetched_at": "timestamp when the page was collected"
  }
}
```
`page_type` is defined in src/pagecollect/rules/page_types/{host}.json; inferred from the URL (e.g. the page `/compliance/` is the `compliance` type.)


## 4. Design Decisions

### 4.1. How We Choose Which Pages to Keep

We ignore pages whose URLs start with:

```bash
[
  "/es",
  "/language/",
  "/about-us",
  "/privacy",
  "/tribal",
  "/search",
  "/complaint",
  "/your-story",
  "/accessibility"
]
```
These rules are configurable and defined in:

. src/pagecollect/rules/urls/default.json

. src/pagecollect/rules/urls/{host}.json

If a host-specific rule file is not present, the default rules are used.

This avoids obvious non-content, utility, and navigation-heavy pages, focusing the collection on high-value informational content.

### 4.2. How We Extract “Main Content”

1). Extract text from the following block-level tags:
```bash
["h1", "h2", "h3", "p", "li", "blockquote", "pre", "code"]
```

2). Ignore blocks that are inside noise sections:
```bash
{"nav", "header", "footer", "aside"}
```

3). For each block, keep it only if it is long enough (≥ 30 words).

4). If no block meets this threshold, the page is discarded.

5). Otherwise, concatenate all retained blocks using \n to form content_text.

This heuristic avoids navigation boilerplate and short, low-signal pages while preserving structured, meaningful content.

### 4.3. How These Choices Support an AI Collections Workflow

1). title

Many embedding and retrieval pipelines treat the title separately from body text.
Keeping it explicit improves retrieval quality and prompt construction.

2). page_type

Classifies the semantic role of the page (e.g., compliance, blog, guidance).
Different downstream tasks may prefer different page types.

3). parent_url

Enables hierarchical context. An LLM can retrieve or reason over a page together with its parent.

4). language

Critical for filtering and routing in multilingual systems.

5). word_count / char_count

Useful for Length-based filtering, ranking and quality heuristics

## 5. Crawler Robustness & Production Considerations

These design choices focus on making the pipeline robuts, polite, and resilient in a real-world environment.

### 5.1. robots.txt & Crawl Policy

- The crawler reads and respects the site’s `robots.txt` before fetching any pages.  
- Only paths explicitly allowed by the site policy are crawled. 

### 5.2. Rate Limiting & Throttling

- Each worker enforces a small delay between requests (right now, it is 0.3 second per request).  
- Global concurrency is bounded by `--num-workers`.  
- This prevents burst traffic and reduces the risk of overloading the target site.  

These controls make the crawler predictable and friendly to external services.

### 5.3. Error Handling & Resilience

- Network failures (timeouts, connection errors) are retried a limited number of times.  
- HTTP errors (4xx / 5xx) are logged and skipped without terminating the crawl.  

### 5.4. Idempotency & De-duplication

- A persistent cache file records visited URLs.  
- Re-running the scraper automatically skips already processed pages.  
- URLs are normalized (e.g., removing fragments and normalizing trailing slashes) to avoid duplicates.

### 5.5. Rules
Use configurable, host-specific rules to:
  - Decide which URL patterns should be ignored (e.g., search pages, legal notices, navigation-only sections).
  - Infer a semantic `page_type` from the URL structure (e.g., `/compliance/` → `compliance`).

This design allows the crawler to adapt to different sites without changing core code, making the pipeline easy to extend to new domains while preserving consistent semantics across collections.

## 6. Future Work

If this pipeline can be extended as following

### 6.1. Scheduling & Incremental Refresh
- Run the scraper on a schedule (e.g., daily/weekly) via Airflow, Cron, or a managed workflow system.
- Support *delta crawling*: only re-fetch pages whose `Last-Modified` changed.

### 6.2. Cross-Source De-duplication
- Add near-duplicate detection using MinHash / SimHash on `content_text`.

### 6.3. Support More Content-Typoes
- Currently it only crawls HTML pages. There are many good PDFs suitable for down-stream RAG abnd search. 

### 6.4. Filter Out Noise Documents
- Use domain keywords and some threshold to filter out more noise documents

### 6.5. External URLS
- Extend the crawler to support external URLs

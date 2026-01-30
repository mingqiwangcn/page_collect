import json
from pathlib import Path
from pagecollect.extraction.parse import parse_page

def test_title():
    html_file = "tests/fixtures/cfpb_debt_collection.html"
    html = Path(html_file).read_text(encoding="utf-8")
    output = parse_page(html)
    assert output["title"] == "Debt collection | Consumer Financial Protection Bureau"
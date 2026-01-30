import json
from pathlib import Path
from pagecollect.extraction.extract import extract_page

def test_extarct_page():
    url = "https://www.consumerfinance.gov/consumer-tools/debt-collection/"
    html_file = "tests/fixtures/cfpb_debt_collection.html"
    html = Path(html_file).read_text(encoding="utf-8")

    about_url = "https://www.consumerfinance.gov/about-us/contact-us"

    rules_1 = {}
    out_page = extract_page(html, url, rules_1)
    assert about_url in out_page["inner_links"]

    rules_2 = {
        "urls":{
            "drop_prefix" : [
                "/about-us"
            ]
        }
    }
    out_page = extract_page(html, url, rules_2)
    assert about_url not in out_page["inner_links"]

def test_page_content():
    url = "https://www.consumerfinance.gov/find-a-housing-counselor"
    html_file = "tests/fixtures/find-a-housing-counselor.html"
    html = Path(html_file).read_text(encoding="utf-8")
    rules_1 = {}
    out_page = extract_page(html, url, rules_1)
    example_str = "agencies at the Consumer Financial Protection Bureau’s (CFPB) website"
    assert example_str in out_page["doc"]["content_text"]
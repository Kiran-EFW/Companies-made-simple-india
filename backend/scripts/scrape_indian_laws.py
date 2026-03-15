"""
Scrape latest Indian government law requirements for document template compliance.

Uses Playwright (headless Chromium) to fetch content from:
- MCA (Ministry of Corporate Affairs) for Companies Act 2013
- India Code for LLP Act, IT Act, Stamp Act
- Legislative sources for DPDP Act, POSH Act

Output: JSON file with structured legal requirements.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_FILE = Path(__file__).parent.parent / "legal_research_results.json"

# Sources to scrape
SOURCES = [
    {
        "id": "table_f_aoa",
        "title": "Companies Act 2013 - Table F (Articles of Association)",
        "urls": [
            "https://www.indiacode.nic.in/show-data?actid=AC_CEN_2_29_00037_201318_1517807324077&sectionId=41825&sectionno=5&ordession=1",
            "https://blog.ipleaders.in/table-f-companies-act-2013/",
            "https://byjus.com/free-ias-prep/companies-act-2013/",
        ],
        "search_query": "site:indiacode.nic.in OR site:ipleaders.in Table F Schedule I Companies Act 2013",
    },
    {
        "id": "moa_requirements",
        "title": "Companies Act 2013 - MOA Requirements (Section 4, Schedule I)",
        "urls": [
            "https://blog.ipleaders.in/memorandum-of-association-under-companies-act-2013/",
            "https://www.toppr.com/guides/business-laws-cs/companies-act-2013/memorandum-of-association/",
            "https://byjus.com/commerce/memorandum-of-association/",
        ],
        "search_query": "site:ipleaders.in OR site:byjus.com memorandum association section 4 companies act 2013 clauses",
    },
    {
        "id": "llp_agreement",
        "title": "LLP Act 2008 - Section 23 (LLP Agreement)",
        "urls": [
            "https://blog.ipleaders.in/llp-agreement/",
            "https://www.toppr.com/guides/business-laws-cs/llp-act-2008/llp-agreement/",
            "https://vakilsearch.com/blog/llp-agreement/",
        ],
        "search_query": "site:ipleaders.in OR site:vakilsearch.com LLP Agreement Section 23 mandatory contents",
    },
    {
        "id": "stamp_duty",
        "title": "Indian Stamp Act - Stamp Duty on Company Documents",
        "urls": [
            "https://blog.ipleaders.in/stamp-duty-on-company-documents/",
            "https://vakilsearch.com/blog/stamp-duty/",
            "https://www.legalraasta.com/stamp-duty/",
        ],
        "search_query": "stamp duty MOA AOA company incorporation India state wise rates 2024 2025",
    },
    {
        "id": "esign_validity",
        "title": "IT Act 2000 - E-Signature Legal Validity (Section 3A, 5)",
        "urls": [
            "https://blog.ipleaders.in/electronic-signature-india/",
            "https://vakilsearch.com/blog/digital-signature-certificate/",
            "https://www.cca.gov.in/about-e-sign.html",
        ],
        "search_query": "electronic signature digital signature certificate India IT Act 2000 section 3A validity",
    },
    {
        "id": "dpdp_act",
        "title": "Digital Personal Data Protection Act 2023 - Privacy Policy Requirements",
        "urls": [
            "https://blog.ipleaders.in/dpdp-act-2023/",
            "https://taxguru.in/corporate-law/digital-personal-data-protection-act-2023.html",
            "https://prsindia.org/billtrack/digital-personal-data-protection-bill-2023",
        ],
        "search_query": "DPDP Act 2023 privacy policy requirements obligations data fiduciary India",
    },
    {
        "id": "posh_act",
        "title": "POSH Act 2013 - Workplace Harassment Policy Requirements",
        "urls": [
            "https://blog.ipleaders.in/posh-act-2013/",
            "https://taxguru.in/corporate-law/posh-act-2013-compliance.html",
            "https://vakilsearch.com/blog/posh-act/",
        ],
        "search_query": "POSH Act 2013 internal committee mandatory compliance requirements India",
    },
    {
        "id": "board_minutes",
        "title": "Companies Act 2013 - Section 118 (Board Meeting Minutes)",
        "urls": [
            "https://blog.ipleaders.in/section-118-companies-act-2013/",
            "https://www.toppr.com/guides/business-laws-cs/companies-act-2013/minutes-of-meetings/",
        ],
        "search_query": "Companies Act 2013 Section 118 board meeting minutes requirements format preservation",
    },
    {
        "id": "incorporation_rules",
        "title": "Companies (Incorporation) Rules 2014",
        "urls": [
            "https://blog.ipleaders.in/companies-incorporation-rules-2014/",
            "https://vakilsearch.com/blog/company-incorporation-india/",
        ],
        "search_query": "Companies Incorporation Rules 2014 SPICe INC-2 INC-3 MCA filing requirements India",
    },
    {
        "id": "agm_egm_requirements",
        "title": "Companies Act 2013 - AGM/EGM Requirements (Section 96, 100, 101)",
        "urls": [
            "https://blog.ipleaders.in/annual-general-meeting-companies-act-2013/",
            "https://www.toppr.com/guides/business-laws-cs/companies-act-2013/annual-general-meeting/",
        ],
        "search_query": "Companies Act 2013 AGM EGM Section 96 101 notice period quorum proxy requirements",
    },
]


async def scrape_page(page, url: str, timeout: int = 15000) -> dict:
    """Scrape a single URL and extract legal content."""
    result = {"url": url, "status": "failed", "content": "", "title": ""}
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        if resp and resp.status == 200:
            result["status"] = "success"
            result["title"] = await page.title()

            # Extract main content - try common selectors
            content = ""
            for selector in [
                "article",
                ".entry-content",
                ".post-content",
                ".article-content",
                ".content-area",
                "#content",
                "main",
                ".main-content",
            ]:
                try:
                    el = await page.query_selector(selector)
                    if el:
                        content = await el.inner_text()
                        if len(content) > 200:
                            break
                except Exception:
                    continue

            # Fallback: get body text
            if len(content) < 200:
                content = await page.inner_text("body")

            # Trim to reasonable size (first 15000 chars)
            result["content"] = content[:15000]
        else:
            result["status"] = f"http_{resp.status if resp else 'no_response'}"
    except Exception as e:
        result["status"] = f"error: {str(e)[:100]}"

    return result


async def search_google(page, query: str) -> list:
    """Search Google and extract result snippets."""
    results = []
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
        await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(2)

        # Extract search result snippets
        snippets = await page.query_selector_all(".VwiC3b, .IsZvec, .lEBKkf span")
        for s in snippets[:10]:
            text = await s.inner_text()
            if text and len(text) > 30:
                results.append(text.strip())

        # Extract featured snippets
        featured = await page.query_selector_all(".hgKElc, .ILfuVd, .LGOjhe")
        for f in featured[:3]:
            text = await f.inner_text()
            if text and len(text) > 50:
                results.insert(0, f"[FEATURED] {text.strip()}")

    except Exception as e:
        results.append(f"Search error: {str(e)[:100]}")

    return results


async def main():
    logger.info("Starting Indian law research scraper...")
    all_results = {
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "purpose": "Legal compliance verification for CMS India document templates",
        },
        "sources": {},
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for source in SOURCES:
            logger.info(f"Researching: {source['title']}")
            source_result = {
                "title": source["title"],
                "pages": [],
                "search_snippets": [],
            }

            # 1. Try direct URLs
            for url in source["urls"]:
                logger.info(f"  Fetching: {url}")
                page_result = await scrape_page(page, url)
                source_result["pages"].append(page_result)
                if page_result["status"] == "success":
                    logger.info(f"    OK - got {len(page_result['content'])} chars")
                else:
                    logger.info(f"    {page_result['status']}")

            # 2. Google search for additional context
            logger.info(f"  Searching: {source['search_query'][:60]}...")
            snippets = await search_google(page, source["search_query"])
            source_result["search_snippets"] = snippets
            logger.info(f"    Got {len(snippets)} search snippets")

            all_results["sources"][source["id"]] = source_result

        await browser.close()

    # Save results
    OUTPUT_FILE.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    logger.info(f"\nResults saved to: {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 70)
    print("RESEARCH SUMMARY")
    print("=" * 70)
    for sid, sdata in all_results["sources"].items():
        success_count = sum(1 for p in sdata["pages"] if p["status"] == "success")
        total_content = sum(len(p.get("content", "")) for p in sdata["pages"])
        snippet_count = len(sdata["search_snippets"])
        print(f"\n{sdata['title']}")
        print(f"  Pages fetched: {success_count}/{len(sdata['pages'])}")
        print(f"  Content chars: {total_content:,}")
        print(f"  Search snippets: {snippet_count}")

        # Print key findings from search snippets
        for snippet in sdata["search_snippets"][:3]:
            if snippet.startswith("[FEATURED]"):
                print(f"  >> {snippet[:150]}")


if __name__ == "__main__":
    asyncio.run(main())

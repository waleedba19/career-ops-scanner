"""
Playwright-based scraper for Arabic translation jobs.
Loads real web pages via headless Chromium to bypass anti-bot protections
that block simple HTTP requests (403s, Cloudflare, JS-rendered content).
"""

import asyncio
import re
import time
from typing import Optional


async def fetch_with_playwright(session=None) -> list[dict]:
    """
    Use Playwright to scrape Arabic translation jobs from blocked sites.
    Falls back gracefully if Playwright is not available.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("  Playwright not installed — skipping browser-based scraping")
        return []

    all_jobs: list[dict] = []
    browser = None

    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)

        # ── 1. ProZ.com (Arabic translation jobs) ──
        try:
            proz_jobs = await _scrape_proz(browser)
            all_jobs.extend(proz_jobs)
            print(f"  Playwright ProZ: {len(proz_jobs)} jobs")
        except Exception as e:
            print(f"  Playwright ProZ failed: {e}")

        await asyncio.sleep(2)

        # ── 2. LinkedIn Jobs (guest, remote Arabic translator) ──
        try:
            linkedin_jobs = await _scrape_linkedin(browser)
            all_jobs.extend(linkedin_jobs)
            print(f"  Playwright LinkedIn: {len(linkedin_jobs)} jobs")
        except Exception as e:
            print(f"  Playwright LinkedIn failed: {e}")

        await asyncio.sleep(2)

        # ── 3. For9a (Arabic freelance platform) ──
        try:
            for9a_jobs = await _scrape_for9a(browser)
            all_jobs.extend(for9a_jobs)
            print(f"  Playwright For9a: {len(for9a_jobs)} jobs")
        except Exception as e:
            print(f"  Playwright For9a failed: {e}")

        await asyncio.sleep(2)

        # ── 4. Mostaql (Arabic freelance platform) ──
        try:
            mostaql_jobs = await _scrape_mostaql(browser)
            all_jobs.extend(mostaql_jobs)
            print(f"  Playwright Mostaql: {len(mostaql_jobs)} jobs")
        except Exception as e:
            print(f"  Playwright Mostaql failed: {e}")

    except Exception as e:
        print(f"  Playwright overall error: {e}")
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass

    print(f"  Playwright total: {len(all_jobs)} jobs")
    return all_jobs


# ──────────────────────────────────────────────────────────────
# Site-specific scrapers
# ──────────────────────────────────────────────────────────────


async def _scrape_proz(browser) -> list[dict]:
    """Scrape Arabic translation jobs from ProZ.com."""
    url = "https://www.proz.com/jobs?langPair=ar%7Car&filter%5Bsearch%5D=arabic"
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        # Give JS-rendered content a moment
        await asyncio.sleep(2)

        jobs = await page.evaluate("""() => {
            const results = [];
            // ProZ job listing selectors — try multiple patterns
            const selectors = [
                'table.job-list tr',
                '.job-listing',
                '.search-result',
                'tr[class*="job"]',
                'div[class*="job"]',
                '.listing',
                'table tr',
            ];
            let rows = [];
            for (const sel of selectors) {
                rows = document.querySelectorAll(sel);
                if (rows.length > 0) break;
            }
            rows.forEach(row => {
                const link = row.querySelector('a[href*="/translation-job/"]')
                    || row.querySelector('a[href*="/jobs/"]')
                    || row.querySelector('a[href*="proz.com"]');
                if (!link) return;
                const title = (link.textContent || '').trim();
                if (!title || title.length < 3) return;
                let href = link.getAttribute('href') || '';
                if (href && !href.startsWith('http')) {
                    href = 'https://www.proz.com' + href;
                }
                // Try to find company/client name
                const cells = row.querySelectorAll('td, span, div');
                let company = '';
                cells.forEach(c => {
                    const txt = (c.textContent || '').trim();
                    if (txt && txt !== title && txt.length > 1 && txt.length < 80
                        && !txt.includes('\\n')) {
                        if (!company) company = txt;
                    }
                });
                // Try to find posted date
                let posted = '';
                cells.forEach(c => {
                    const txt = (c.textContent || '').trim();
                    if (txt && /\\d{1,2}[\\s\\-\\/](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i.test(txt)) {
                        posted = txt;
                    }
                });
                results.push({
                    title: title,
                    company: company,
                    url: href,
                    location: 'Remote',
                    posted: posted,
                    description: '',
                    salary: '',
                    source: 'proz_playwright',
                });
            });
            return results;
        }""")
        return jobs
    finally:
        await page.close()


async def _scrape_linkedin(browser) -> list[dict]:
    """Scrape remote Arabic translator jobs from LinkedIn (guest mode, no login)."""
    url = "https://www.linkedin.com/jobs/search/?keywords=arabic+translator&f_WT=2&sortBy=DD"
    page = await browser.new_page()
    try:
        # Set a realistic user agent to avoid bot detection
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(2)

        jobs = await page.evaluate("""() => {
            const results = [];
            // LinkedIn job card selectors
            const selectors = [
                '.base-card',
                '.base-search-card',
                'li.reusable-search__result-container',
                '.job-search-card',
                'div[class*="result-container"]',
                'section.jobs-search__results-list li',
            ];
            let cards = [];
            for (const sel of selectors) {
                cards = document.querySelectorAll(sel);
                if (cards.length > 0) break;
            }
            cards.forEach(card => {
                const titleEl = card.querySelector('.base-search-card__title, .screen-reader-text, h3, h2');
                const companyEl = card.querySelector('.base-search-card__subtitle, .hidden-nested-link, .entity-result__primary-subtitle');
                const linkEl = card.querySelector('a[href*="/jobs/"], a.base-card__full-link, a[data-tracking-control-name]');
                const locationEl = card.querySelector('.job-search-card__location, .entity-result__secondary-subtitle');
                if (!titleEl) return;
                const title = (titleEl.textContent || '').trim();
                if (!title || title.length < 3) return;
                let url = '';
                if (linkEl) {
                    url = linkEl.getAttribute('href') || '';
                    if (url && !url.startsWith('http')) url = 'https://www.linkedin.com' + url;
                    // Remove query params for cleaner URL
                    url = url.split('?')[0];
                }
                const company = (companyEl ? companyEl.textContent : '').trim();
                const location = (locationEl ? locationEl.textContent : '').trim() || 'Remote';
                results.push({
                    title: title,
                    company: company,
                    url: url,
                    location: location,
                    posted: '',
                    description: '',
                    salary: '',
                    source: 'linkedin_playwright',
                });
            });
            return results;
        }""")
        return jobs
    finally:
        await page.close()


async def _scrape_for9a(browser) -> list[dict]:
    """Scrape translation/editing jobs from For9a.com."""
    url = "https://for9a.com/jobs/fields/%D9%88%D8%B8%D8%A7%D8%A6%D9%81-%D8%A7%D9%84%D8%B5%D8%AD%D8%A7%D9%81%D8%A9-%D9%88%D8%A7%D9%84%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1-%D9%88%D8%A7%D9%84%D8%AA%D8%B1%D8%AC%D9%85%D8%A9"
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(2)

        jobs = await page.evaluate("""() => {
            const results = [];
            // For9a job card selectors
            const selectors = [
                '.job-item',
                '.project-item',
                '.list-group-item',
                'div[class*="job"]',
                'div[class*="project"]',
                'article',
                '.card',
            ];
            let cards = [];
            for (const sel of selectors) {
                cards = document.querySelectorAll(sel);
                if (cards.length > 0) break;
            }
            cards.forEach(card => {
                const link = card.querySelector('a[href*="/jobs/"], a[href*="/project/"]');
                if (!link) return;
                const title = (link.textContent || '').trim();
                if (!title || title.length < 3) return;
                let href = link.getAttribute('href') || '';
                if (href && !href.startsWith('http')) {
                    href = 'https://for9a.com' + href;
                }
                results.push({
                    title: title,
                    company: 'For9a',
                    url: href,
                    location: 'Remote',
                    posted: '',
                    description: '',
                    salary: '',
                    source: 'for9a_playwright',
                });
            });
            return results;
        }""")
        return jobs
    finally:
        await page.close()


async def _scrape_mostaql(browser) -> list[dict]:
    """Scrape translation projects from Mostaql.com."""
    url = "https://mostaql.com/projects?filter=translation"
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(2)

        jobs = await page.evaluate("""() => {
            const results = [];
            // Mostaql project card selectors
            const selectors = [
                '.project-item',
                'div[class*="project"]',
                '.card',
                'article',
                '.list-item',
            ];
            let cards = [];
            for (const sel of selectors) {
                cards = document.querySelectorAll(sel);
                if (cards.length > 0) break;
            }
            cards.forEach(card => {
                const link = card.querySelector('a[href*="/projects/"], a[href*="/project/"]');
                if (!link) return;
                const title = (link.textContent || '').trim();
                if (!title || title.length < 3) return;
                let href = link.getAttribute('href') || '';
                if (href && !href.startsWith('http')) {
                    href = 'https://mostaql.com' + href;
                }
                results.push({
                    title: title,
                    company: 'Mostaql',
                    url: href,
                    location: 'Remote',
                    posted: '',
                    description: '',
                    salary: '',
                    source: 'mostaql_playwright',
                });
            });
            return results;
        }""")
        return jobs
    finally:
        await page.close()

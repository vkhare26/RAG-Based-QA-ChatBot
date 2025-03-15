import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_trust_arts_calendar():
    """
    Scrapes events from trustarts.org with the given date range.
    Gathers event data (title, date, venue, organization, categories)
    plus a "description" from each detail page.
    Saves to 'trustarts_events.csv'.
    """

    # Starting URL for page 1
    start_url = (
        "https://trustarts.org/calendar?"
        "genre=All+Genres&organization_id=&start_date=2025%2F03%2F19&end_date=2026%2F01%2F01&"
        "filter%5Bmin%5D=2025-03-14T00%3A54%3A46-04%3A00&filter%5Bmax%5D=2026-09-14+00%3A54%3A46+-0400"
    )

    # Configure Selenium (headless Chrome)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(start_url)
    time.sleep(3)

    all_events = []

    page_number = 1
    while True:
        print(f"Scraping page {page_number}...")

        # 1) Find all <article class="event ..."> blocks
        #    This should include both the main "events-group" and "exhibitions" section
        articles = driver.find_elements(By.CSS_SELECTOR, "article.event")
        print(f"Found {len(articles)} events/articles on page {page_number}.")

        for art in articles:
            # Title & detail link
            try:
                title_elem = art.find_element(By.CSS_SELECTOR, "h3.title a")
                title = title_elem.text.strip()
                detail_link = title_elem.get_attribute("href")
            except:
                title = "N/A"
                detail_link = "N/A"

            # Date/time from <time class="range" datetime="...">
            try:
                time_elem = art.find_element(By.CSS_SELECTOR, ".time-wrapper time.range, .time-wrapper div.time.range")
                date_text = time_elem.text.strip()
            except:
                date_text = "N/A"

            # Venue (if present)
            try:
                venue_elem = art.find_element(By.CSS_SELECTOR, ".venue")
                venue_text = venue_elem.text.strip()
            except:
                # Some events might not have .venue (like an "Online Event" or "See Event Description")
                venue_text = "N/A"

            # Organization
            try:
                org_elem = art.find_element(By.CSS_SELECTOR, ".organization")
                org_text = org_elem.text.strip()
            except:
                org_text = "N/A"

            # Categories
            # For example: <ul class="category-group"><li class="category"><a>Concert</a></li>...
            try:
                cat_lis = art.find_elements(By.CSS_SELECTOR, ".category-group li.category a")
                categories = [c.text.strip() for c in cat_lis]
            except:
                categories = []

            # 2) Now gather description from detail link (open in new tab)
            description = "N/A"
            if detail_link != "N/A" and detail_link.startswith("https://trustarts.org"):
                # Or you can check if detail_link is relative, then prepend domain
                # If the link is relative like "/production/xyz", do:
                # detail_link = "https://trustarts.org" + detail_link
                pass
            elif detail_link != "N/A" and detail_link.startswith("/"):
                # The link is relative, so prefix the domain
                detail_link = "https://trustarts.org" + detail_link

            if detail_link and detail_link != "N/A":
                driver.execute_script("window.open(arguments[0], '_blank');", detail_link)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

                # Gather paragraphs as a fallback
                # If you see a specific container for the event info, refine the selector
                try:
                    detail_paras = driver.find_elements(By.CSS_SELECTOR, "p")
                    desc_texts = []
                    for p_elem in detail_paras:
                        p_text = p_elem.text.strip()
                        if p_text:
                            desc_texts.append(p_text)

                    if desc_texts:
                        description = "\n\n".join(desc_texts)
                except:
                    pass

                # Close detail tab
                driver.close()
                # Switch back to main listing tab
                driver.switch_to.window(driver.window_handles[0])

            # Build dictionary
            event_data = {
                "page": page_number,
                "title": title,
                "date_range": date_text,
                "venue": venue_text,
                "organization": org_text,
                "categories": ", ".join(categories),
                "detail_link": detail_link,
                "description": description
            }
            all_events.append(event_data)

        # 3) Attempt to go to next page
        #    The pager is <section class="pager"> with <div class="pages"><div class="pagination"> ...
        #    There's an <a class="next_page" href="..."> if next is available
        try:
            next_link = driver.find_element(By.CSS_SELECTOR, "div.pagination a.next_page")
            if next_link:
                next_url = next_link.get_attribute("href")
                print(f"Moving to next page: {next_url}")
                driver.get(next_url)
                page_number += 1
                time.sleep(3)
            else:
                print("No next_page link found. Done.")
                break
        except:
            print("No next_page link found or not clickable. Done.")
            break

    driver.quit()

    # Convert to DataFrame and save
    df = pd.DataFrame(all_events)
    df.to_csv("trustarts_events.csv", index=False, encoding="utf-8")
    print(f"Scraped {len(df)} events total. Results in 'trustarts_events.csv'.")

if __name__ == "__main__":
    scrape_trust_arts_calendar()

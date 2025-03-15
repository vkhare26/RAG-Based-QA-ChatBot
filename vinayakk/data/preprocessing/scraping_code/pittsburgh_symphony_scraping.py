import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_pso_events_about():
    """
    Scrapes multiple pages of Pittsburgh Symphony Orchestra events,
    focusing on the <article class='description'> block in each event's detail page.
    - Locates headings containing the word 'about' (case-insensitive).
    - Collects <p> paragraphs until the next heading.
    - Expands the read-more section if a data-readmore-toggle button is found.
    Saves results to 'pso_events_about.csv'.
    """

    # Base URL with pagination
    base_url = (
        "https://www.pittsburghsymphony.org/calendar?"
        "end_date=2026%2F09%2F07&filter%5Bcurrent_page%5D=production&"
        "filter%5Bmax%5D=2026-09-07+14%3A22%3A23+-0400&"
        "filter%5Bmin%5D=2025-03-07T14%3A22%3A23-05%3A00&"
        "genre=All+Genres&organization_id=2&start_date=2025%2F03%2F19&page="
    )

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    all_events = []

    # Loop through however many pages you need, e.g. 1-6
    for page_num in range(1, 7):
        url = f"{base_url}{page_num}"
        print(f"Scraping page {page_num}: {url}")
        driver.get(url)
        time.sleep(3)

        # Find event <article class="event">
        event_articles = driver.find_elements(By.CSS_SELECTOR, "article.event")
        print(f"  Found {len(event_articles)} events on page {page_num}.")

        for article in event_articles:
            # Extract listing info
            try:
                title_elem = article.find_element(By.CSS_SELECTOR, ".event-details-wrap h3.title a")
                event_title = title_elem.text.strip()
                detail_link = title_elem.get_attribute("href")
            except:
                event_title = "N/A"
                detail_link = "N/A"

            try:
                time_elem = article.find_element(By.CSS_SELECTOR, ".time-wrapper time.range")
                date_text = time_elem.text.strip()
                date_attr = time_elem.get_attribute("datetime")
            except:
                date_text = "N/A"
                date_attr = "N/A"

            try:
                venue_elem = article.find_element(By.CSS_SELECTOR, ".venue")
                venue_text = venue_elem.text.strip()
            except:
                venue_text = "N/A"

            try:
                org_elem = article.find_element(By.CSS_SELECTOR, ".organization")
                org_text = org_elem.text.strip()
            except:
                org_text = "N/A"

            try:
                cat_elems = article.find_elements(By.CSS_SELECTOR, ".category-group li.category a")
                categories = [c.text.strip() for c in cat_elems]
            except:
                categories = []

            # Now gather "about" text from the detail page
            about_text = "N/A"
            if detail_link and detail_link != "N/A":
                # Open detail link in new tab
                driver.execute_script("window.open(arguments[0], '_blank');", detail_link)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

                try:
                    # 1) Attempt to locate <article class="description"> if it exists
                    desc_article = driver.find_element(By.CSS_SELECTOR, "article.description")

                    # 2) Possibly expand if there's a "read more" toggle
                    #    with data-readmore-toggle attribute
                    try:
                        read_more_btn = desc_article.find_element(By.CSS_SELECTOR, "[data-readmore-toggle]")
                        read_more_btn.click()
                        time.sleep(1)
                    except:
                        pass  # no read-more toggle found

                    # 3) Gather headings + paragraphs inside that article
                    #    in DOM order
                    elements = desc_article.find_elements(
                        By.XPATH,
                        ".//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6 or self::p]"
                    )

                    found_about_heading = False
                    paragraphs = []

                    for elem in elements:
                        tag_name = elem.tag_name.lower()
                        text = elem.text.strip()
                        if not text:
                            continue

                        if tag_name in ["h1","h2","h3","h4","h5","h6"]:
                            # If we were collecting paragraphs, next heading => stop
                            if found_about_heading:
                                break
                            # If heading CONTAINS "about" ignoring case
                            # e.g. "About this Speaker", "ABOUT THE CONCERT", etc.
                            if "about" in text.lower():
                                found_about_heading = True
                        else:
                            # If it's a <p> and we've found the about heading
                            if found_about_heading and tag_name == "p":
                                paragraphs.append(text)

                    if paragraphs:
                        about_text = "\n\n".join(paragraphs)
                    else:
                        about_text = "N/A"

                except:
                    pass

                # Close tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # Save event data
            event_data = {
                "page": page_num,
                "title": event_title,
                "date_text": date_text,
                "date_attr": date_attr,
                "venue": venue_text,
                "organization": org_text,
                "categories": ", ".join(categories),
                "description": about_text
            }
            all_events.append(event_data)

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(all_events)
    df.to_csv("pso_events_about.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} events to 'pso_events_about.csv'.")

if __name__ == "__main__":
    scrape_pso_events_about()

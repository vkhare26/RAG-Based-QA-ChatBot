import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_trust_arts_events():
    # Base URL: note the &page= at the end (no numeric value)
    base_url = (
        "https://trustarts.org/calendar?"
        "genre=All+Genres&organization_id=1&start_date=2025%2F03%2F19&end_date=2026%2F09%2F07&"
        "filter%5Bmin%5D=2025-03-07T16%3A35%3A08-05%3A00&"
        "filter%5Bmax%5D=2026-09-07+16%3A35%3A08+-0400&"
        "filter%5Bcurrent_page%5D=production&page="
    )

    # Configure Selenium (headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    all_events = []

    # Loop from page 1 to 7
    for page_num in range(1, 8):
        url = f"{base_url}{page_num}"
        print(f"Scraping page {page_num}: {url}")
        driver.get(url)
        
        # Give the page a few seconds to load
        time.sleep(3)

        # Locate all <article class="event"> blocks (assuming same structure)
        event_articles = driver.find_elements(By.CSS_SELECTOR, "article.event")

        for article in event_articles:
            # Title
            try:
                title_elem = article.find_element(By.CSS_SELECTOR, ".event-details-wrap h3.title a")
                event_title = title_elem.text.strip()
            except:
                event_title = "N/A"

            # Date from <time class="range" datetime="...">
            try:
                time_elem = article.find_element(By.CSS_SELECTOR, ".time-wrapper time.range")
                date_text = time_elem.text.strip()
                date_attr = time_elem.get_attribute("datetime")
            except:
                date_text = "N/A"
                date_attr = "N/A"

            # Venue
            try:
                venue_elem = article.find_element(By.CSS_SELECTOR, ".venue")
                venue_text = venue_elem.text.strip()
            except:
                venue_text = "N/A"

            # Organization
            try:
                org_elem = article.find_element(By.CSS_SELECTOR, ".organization")
                org_text = org_elem.text.strip()
            except:
                org_text = "N/A"

            # Categories
            try:
                cat_elems = article.find_elements(By.CSS_SELECTOR, ".category-group li.category a")
                categories = [c.text.strip() for c in cat_elems]
            except:
                categories = []

            event_info = {
                "page": page_num,
                "title": event_title,
                "date_text": date_text,
                "date_attr": date_attr,
                "venue": venue_text,
                "organization": org_text,
                "categories": ", ".join(categories),
            }
            all_events.append(event_info)

    driver.quit()

    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(all_events)

    # Save the DataFrame to a CSV file
    df.to_csv("trust_arts_events.csv", index=False)
    print("Scraped events saved to 'trust_arts_events.csv'.")

if __name__ == "__main__":
    scrape_trust_arts_events()

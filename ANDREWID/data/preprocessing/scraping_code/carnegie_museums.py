import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_carnegie_museums_events_paragraphs_only():
    """
    Scrapes the first 3 pages of Carnegie Museums events, and for each event:
      - start_date, end_date, date_text
      - title
      - link
      - venue
      - categories, audiences
      - description: only the text from <p> elements on the detail page, skipping common boilerplate lines.
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    all_events = []

    for page_num in range(1, 4):  # pages 1 through 3
        if page_num == 1:
            url = "https://carnegiemuseums.org/events/"  # Page 1
        else:
            url = f"https://carnegiemuseums.org/events/page/{page_num}/"
        
        print(f"Scraping listing page {page_num}: {url}")
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Find all <article class="event-card ..."> blocks
        articles = driver.find_elements(By.CSS_SELECTOR, "article.event-card")

        for art in articles:
            # 1) Start/End Dates
            start_date = art.get_attribute("data-event-start") or "N/A"
            end_date = art.get_attribute("data-event-end") or "N/A"

            # 2) date_text from the <time> element, or fallback
            try:
                time_elem = art.find_element(By.CSS_SELECTOR, ".event-card__date")
                date_text = time_elem.text.strip()
            except:
                date_text = f"{start_date} - {end_date}"

            # 3) Title
            try:
                title_elem = art.find_element(By.CSS_SELECTOR, "div.event-card__content a h2")
                title = title_elem.text.strip()
            except:
                title = "N/A"

            # 4) Link
            try:
                link_elem = art.find_element(By.CSS_SELECTOR, "div.event-card__content a")
                link = link_elem.get_attribute("href")
            except:
                link = "N/A"

            # 5) Venue
            try:
                venue_elem = art.find_element(By.CSS_SELECTOR, ".event-card__venue a")
                venue = venue_elem.text.strip()
            except:
                venue = "N/A"

            # 6) Categories
            try:
                details_section = art.find_element(By.CSS_SELECTOR, "div.event-card__details")
                category_links = details_section.find_elements(By.CSS_SELECTOR, "a.event-card__event-type")
                categories = [c.text.strip() for c in category_links]
            except:
                categories = []

            # 7) Audiences
            try:
                audience_links = details_section.find_elements(By.CSS_SELECTOR, "a.event-card__audience-type")
                audiences = [a.text.strip() for a in audience_links]
            except:
                audiences = []

            # 8) Description from <p> elements in the detail page
            description = "N/A"
            if link and link != "N/A":
                # Open detail page in a new tab
                driver.execute_script("window.open(arguments[0], '_blank');", link)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)  # wait for the detail page to load

                try:
                    # Find all paragraphs <p>
                    paragraph_elems = driver.find_elements(By.CSS_SELECTOR, "p")
                    desc_paragraphs = []
                    for p in paragraph_elems:
                        text = p.text.strip()
                        if not text:
                            continue
                        # Skip lines that contain certain boilerplate phrases
                        # Adjust these checks as needed
                        lower_text = text.lower()
                        if any(phrase in lower_text for phrase in ["skip to content", "buy tickets"]):
                            continue
                        desc_paragraphs.append(text)

                    # Join them with blank lines in between
                    if desc_paragraphs:
                        description = "\n\n".join(desc_paragraphs)
                    else:
                        description = "N/A"

                except:
                    pass

                # Close the detail tab
                driver.close()
                # Switch back to the listing tab
                driver.switch_to.window(driver.window_handles[0])

            # Build a dictionary of the extracted data
            event_info = {
                "page": page_num,
                "start_date": start_date,
                "end_date": end_date,
                "date_text": date_text,
                "title": title,
                "link": link,
                "venue": venue,
                "categories": ", ".join(categories),
                "audiences": ", ".join(audiences),
                "description": description
            }
            all_events.append(event_info)

    driver.quit()

    # Convert to a DataFrame and save to CSV
    df = pd.DataFrame(all_events)
    df.to_csv("carnegie_museums_events_paragraphs.csv", index=False)
    print("Scraped events saved to 'carnegie_museums_events_paragraphs.csv'.")

if __name__ == "__main__":
    scrape_carnegie_museums_events_paragraphs_only()

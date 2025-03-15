import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_pittsburgh_opera_calendar():
    """
    Scrapes events from Pittsburgh Opera's calendar from March to July (or
    until 'Next' is no longer available).
    Collects title, date, time, location, detail link, and a description from
    each event's detail page.
    Saves the results to 'pittsburgh_opera_events.csv'.
    """

    # Starting URL (March 1 - March 31 in the snippet)
    start_url = "https://pittsburghopera.org/calendar?timequery=month&prev=-1&start=1740805200000&end=1743461940000"

    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(start_url)
    time.sleep(3)  # Wait for initial page to load

    all_events = []

    while True:
        # 1) Find all .event-container blocks
        event_containers = driver.find_elements(By.CSS_SELECTOR, "div.event-container")
        print(f"Found {len(event_containers)} events on this page.")

        for container in event_containers:
            try:
                event_div = container.find_element(By.CSS_SELECTOR, "div.event")
            except:
                # If there's no div.event, skip
                continue

            # Extract event info
            try:
                title_elem = event_div.find_element(By.CSS_SELECTOR, "h4")
                title = title_elem.text.strip()
            except:
                title = "N/A"

            # The site has multiple <p class="date"> lines. Typically:
            #  1st p.date => day and date, e.g. "Saturday, March 1, 2025"
            #  2nd p.date => time range, e.g. "12:00 PM - 03:00 PM"
            # Possibly 3rd p => location if it's not included above
            paragraphs = event_div.find_elements(By.CSS_SELECTOR, "p")
            date_str = "N/A"
            time_str = "N/A"
            location_str = "N/A"

            # We'll do a quick parse of each <p> in order
            # The site uses <p class="date"> for date/time, so we can check that
            # Then a <p> without class might be location
            date_count = 0
            for p in paragraphs:
                text = p.text.strip()
                # If p has class="date", it's date or time
                if "date" in p.get_attribute("class"):
                    date_count += 1
                    if date_count == 1:
                        # e.g. "Saturday, March 1, 2025"
                        date_str = text
                    elif date_count == 2:
                        # e.g. "12:00 PM - 03:00 PM"
                        time_str = text
                    else:
                        # If there's a 3rd .date, might be location or we skip
                        pass
                else:
                    # Possibly the location or extra info
                    # If there's something like "Benedum Center"
                    if text:
                        location_str = text

            # "View Details" link
            try:
                details_link = event_div.find_element(By.PARTIAL_LINK_TEXT, "View Details")
                detail_url = details_link.get_attribute("href")
            except:
                detail_url = "N/A"

            # 2) Now open detail link in new tab, gather description
            description = "N/A"
            if detail_url != "N/A":
                driver.execute_script("window.open(arguments[0], '_blank');", detail_url)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)  # wait for detail page

                try:
                    # We'll gather all <p> paragraphs from the detail page
                    detail_paras = driver.find_elements(By.CSS_SELECTOR, "p")
                    desc_texts = []
                    for dp in detail_paras:
                        dtext = dp.text.strip()
                        if dtext:
                            desc_texts.append(dtext)

                    if desc_texts:
                        description = "\n\n".join(desc_texts)
                except:
                    pass

                # Close the detail tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            # 3) Store event data
            event_data = {
                "title": title,
                "date": date_str,
                "time": time_str,
                "location": location_str,
                "detail_link": detail_url,
                "description": description
            }
            all_events.append(event_data)

        # 4) Attempt to click "Next" button to load more events
        #    If not found or not clickable, break
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, ".event-listing__navigation .next a.button--primary")
            # If "Next" is just a button without an actual link/href or if it's disabled, we might break
            # But let's try to click
            print("Clicking 'Next' to load more events...")
            next_button.click()
            time.sleep(3)
        except:
            print("No 'Next' button found or not clickable. Ending loop.")
            break

    # Done scraping
    driver.quit()

    # Save data to CSV
    df = pd.DataFrame(all_events)
    df.to_csv("pittsburgh_opera_events.csv", index=False, encoding="utf-8")
    print(f"Scraped {len(df)} events total. Saved to 'pittsburgh_opera_events.csv'.")

if __name__ == "__main__":
    scrape_pittsburgh_opera_calendar()

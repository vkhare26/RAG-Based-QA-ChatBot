import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_heinz_history_center_events():
    """
    Scrapes event listings from Heinz History Center's events page,
    including date, location, time, title, short description, ticket info,
    and also opens each event link to gather the full text from that page's <p> tags.
    The combined short + detail text is stored in the 'description' column.
    """

    url = (
        "https://www.heinzhistorycenter.org/events/?query=&filters%5Bcategory%5D="
        "&filters%5Blocation%5D=&filters%5Bmonth%5D=#filter_results"
    )

    # Configure Selenium (headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)  # Give the page time to load

    # Locate the <ul class="events_list_items">
    events_list = driver.find_element(By.CSS_SELECTOR, "ul.events_list_items")

    # Find all <li class="events_list_item">
    event_items = events_list.find_elements(By.CSS_SELECTOR, "li.events_list_item")

    all_events = []

    for item in event_items:
        # Each item contains a <div class="card ...">
        try:
            card = item.find_element(By.CSS_SELECTOR, "div.card")
        except:
            continue

        # 1) Date from <p class="card_date"> (e.g. "March 7")
        try:
            date_elem = card.find_element(By.CSS_SELECTOR, "p.card_date")
            date_text = date_elem.text.strip()
        except:
            date_text = "N/A"

        # 2) Location from <span class="card_location"> (e.g. "Heinz History Center")
        try:
            loc_elem = card.find_element(By.CSS_SELECTOR, "span.card_location")
            location = loc_elem.text.strip()
        except:
            location = "N/A"

        # 3) Time from <span class="card_time"> (e.g. "7:30 PM")
        try:
            time_elem = card.find_element(By.CSS_SELECTOR, "span.card_time")
            time_text = time_elem.text.strip()
        except:
            time_text = "N/A"

        # 4) Title & Link from <h3 class="card_title"> <a> ... </a>
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, "h3.card_title a")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")
        except:
            title = "N/A"
            link = "N/A"

        # 5) Short Description from <div class="card_description"><p> ... </p></div>
        try:
            desc_elem = card.find_element(By.CSS_SELECTOR, "div.card_description p")
            short_desc = desc_elem.text.strip()
        except:
            short_desc = "N/A"

        # 6) Ticket requirement from <p class="card_ticket_label">Tickets Required</p> or similar
        try:
            ticket_elem = card.find_element(By.CSS_SELECTOR, "p.card_ticket_label")
            ticket_label = ticket_elem.text.strip()
        except:
            ticket_label = "N/A"

        # 7) Open the detail link in a new tab to gather full text
        detail_paragraphs = []
        if link != "N/A":
            driver.execute_script("window.open(arguments[0], '_blank');", link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            try:
                # Gather all <p> paragraphs from the detail page
                p_elems = driver.find_elements(By.CSS_SELECTOR, "p")
                for p in p_elems:
                    text = p.text.strip()
                    if text:
                        detail_paragraphs.append(text)
            except:
                pass

            # Close the detail tab
            driver.close()
            # Switch back to the main listing tab
            driver.switch_to.window(driver.window_handles[0])

        # Combine the short description + detail text
        # e.g. short description + blank line + detail paragraphs
        detail_text = ""
        if detail_paragraphs:
            detail_text = "\n\n".join(detail_paragraphs)

        # Final combined description
        combined_description = short_desc
        if detail_text:
            combined_description += "\n\n" + detail_text

        event_info = {
            "date": date_text,
            "location": location,
            "time": time_text,
            "title": title,
            "link": link,
            "description": combined_description,
            "tickets": ticket_label
        }
        all_events.append(event_info)

    driver.quit()

    # Convert to DataFrame & save as CSV
    df = pd.DataFrame(all_events)
    df.to_csv("heinz_history_events.csv", index=False, encoding="utf-8")
    print("Scraped events saved to 'heinz_history_events.csv'.")

if __name__ == "__main__":
    scrape_heinz_history_center_events()

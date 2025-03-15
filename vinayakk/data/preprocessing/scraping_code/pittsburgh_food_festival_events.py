import time
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_visit_pittsburgh_pages_df():
    base_url = (
        "https://www.visitpittsburgh.com/events-festivals/"
        "?hitsPerPage=24"
        "&startDate=1742342400"
        "&endDate=1773187199"
        "&page="
    )

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # Add a user-agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    all_events = []

    # We will scrape pages 1 to 5
    for page_num in range(1, 6):
        url = f"{base_url}{page_num}"
        print(f"Scraping page {page_num}: {url}")
        driver.get(url)

        # Optional: scroll to bottom if the site is lazy-loading
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Print snippet of page source for debugging
        print(driver.page_source[:2000])

        # Explicit wait up to 15 seconds for event cards
        try:
            wait = WebDriverWait(driver, 15)
            event_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card.card--common.card--listing"))
            )
        except:
            print(f"No event cards found on page {page_num} after 15s wait.")
            continue

        print(f"Found {len(event_cards)} cards on page {page_num}.")

        # Remember the original window handle, so we can switch back
        original_window = driver.current_window_handle

        for card in event_cards:
            # Title
            try:
                title = card.get_attribute("data-title").strip()
            except:
                title = "N/A"

            # Date
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, "p.date-heading.card__date-heading")
                date_text = date_elem.text.strip()
            except:
                date_text = "N/A"

            # Venue & Address
            venue = "N/A"
            full_address = "N/A"
            summary_div = None
            try:
                summary_div = card.find_element(By.CSS_SELECTOR, "div.card__summary")
                address_div = summary_div.find_element(By.CSS_SELECTOR, "div.card__address")
                spans = address_div.find_elements(By.TAG_NAME, "span")
                address_lines = [sp.text.strip() for sp in spans]
                if address_lines:
                    venue = address_lines[0]
                if len(address_lines) > 1:
                    full_address = ", ".join(address_lines[1:])
            except:
                pass

            # Phone
            phone = "N/A"
            if summary_div:
                try:
                    phone_div = summary_div.find_element(By.CSS_SELECTOR, "div.card__phone a")
                    phone = phone_div.text.strip()
                except:
                    pass

            # Links
            learn_more_link = "N/A"
            website_link = "N/A"
            description = "N/A"
            try:
                actions_div = card.find_element(By.CSS_SELECTOR, "div.card__actions.action-bar")
                try:
                    learn_more_a = actions_div.find_element(By.CSS_SELECTOR, "a.card__link.btn.btn--alt")
                    learn_more_link = learn_more_a.get_attribute("href")
                except:
                    pass
                try:
                    website_a = actions_div.find_element(By.CSS_SELECTOR, "a.btn.btn--link")
                    website_link = website_a.get_attribute("href")
                except:
                    pass
            except:
                pass

            # If we have a valid Learn More link, open it in a new tab to scrape description
            if learn_more_link != "N/A":
                try:
                    # Open new tab
                    driver.switch_to.new_window('tab')
                    driver.get(learn_more_link)
                    
                    # Optional wait so page can load (or use explicit wait)
                    time.sleep(2)
                    
                    # Parse page source with BeautifulSoup
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")

                    # Adjust this selector to whatever container holds the event description
                    detail_container = soup.select_one("div.detail__main, div.detail__description")
                    if detail_container:
                        description = detail_container.get_text(separator="\n", strip=True)
                    else:
                        # Fallback: get entire page text
                        description = soup.get_text(separator="\n", strip=True)

                except Exception as e:
                    print(f"Error retrieving description from {learn_more_link}: {e}")
                finally:
                    # Close the new tab
                    driver.close()
                    # Switch back to the original window
                    driver.switch_to.window(original_window)

            event_data = {
                "page": page_num,
                "title": title,
                "date_range": date_text,
                "venue": venue,
                "address": full_address,
                "phone": phone,
                "learn_more_link": learn_more_link,
                "website_link": website_link,
                "description": description
            }
            all_events.append(event_data)

    driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(all_events)
    # Print or return the DataFrame
    print(df)
    return df

if __name__ == "__main__":
    df_events = scrape_visit_pittsburgh_pages_df()
    # Optionally save to CSV if you want:
    df_events.to_csv("visit_pittsburgh_events_pages1to5.csv", index=False)

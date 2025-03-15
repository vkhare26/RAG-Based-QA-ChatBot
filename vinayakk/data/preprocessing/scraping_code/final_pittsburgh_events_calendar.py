import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

# ----- DRIVER SETUP FUNCTIONS -----
def get_standard_driver():
    """
    Returns a standard (headful) Selenium Chrome driver using webdriver_manager.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_undetected_driver():
    """
    Returns an undetected Chrome driver (headful) using undetected_chromedriver.
    (Use this if you run into bot detection issues.)
    """
    return uc.Chrome(headless=False)

# ----- SCRAPING FUNCTIONS -----
def scrape_events_for_month(month, min_events=600):
    """
    Visit the monthly URL for a given month (e.g. 'march' -> https://pittsburgh.events/march/)
    and click the "Show More" button repeatedly until at least min_events events are loaded
    (or until no more button is found). Then extract event details.
    Returns a list of event dictionaries.
    """
    driver = get_standard_driver()
    url = f"https://pittsburgh.events/{month}/"
    print(f"Scraping events for {month.capitalize()} at {url}")
    driver.get(url)
    time.sleep(5)  # wait for the page to load

    # Keep clicking "Show More" until we have at least min_events or no more button is found
    while True:
        event_elements = driver.find_elements(By.CSS_SELECTOR, "li.date-row")
        print(f"[{month.capitalize()}] Currently loaded events: {len(event_elements)}")
        if len(event_elements) >= min_events:
            print(f"[{month.capitalize()}] Reached {min_events} events.")
            break
        
        try:
            show_more = driver.find_element(
                By.XPATH, "//span[@class='gsb-textnode' and contains(text(), 'Show More')]"
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more)
            time.sleep(10)
            show_more.click()
            print(f"[{month.capitalize()}] Clicked 'Show More'...")
            time.sleep(10)
        except Exception as e:
            print(f"[{month.capitalize()}] No more 'Show More' buttons found or click failed: {e}")
            break

    # After loading, re-collect the event elements.
    event_elements = driver.find_elements(By.CSS_SELECTOR, "li.date-row")
    print(f"[{month.capitalize()}] Total events loaded: {len(event_elements)}")

    month_events = []
    for event in event_elements:
        # Extract image alt text
        try:
            img = event.find_element(By.TAG_NAME, "img")
            alt_text = img.get_attribute("alt")
        except Exception:
            alt_text = ""
        
        # Extract date (month, day, year)
        try:
            date_div = event.find_element(By.CLASS_NAME, "date")
            m = date_div.find_element(By.CLASS_NAME, "month").text.strip()
            d = date_div.find_element(By.CLASS_NAME, "day").text.strip()
            y = date_div.find_element(By.CLASS_NAME, "year").text.strip()
            event_date = f"{m} {d}, {y}"
        except Exception:
            event_date = ""
        
        # Extract time
        try:
            time_text = event.find_element(By.CLASS_NAME, "time").text.strip()
        except Exception:
            time_text = ""
        
        # Extract venue (first <a> inside the venue container)
        try:
            venue_div = event.find_element(By.CLASS_NAME, "venue")
            venue = venue_div.find_element(By.TAG_NAME, "a").text.strip()
        except Exception:
            venue = ""
        
        # Extract schedule link (text and URL) from the date-desc div
        schedule_link_text = ""
        schedule_link_url = ""
        try:
            schedule_elem = event.find_element(By.CSS_SELECTOR, "div.date-desc a.schedule-link")
            schedule_link_text = schedule_elem.text.strip()
            schedule_link_url = schedule_elem.get_attribute("href")
        except Exception:
            pass
        
        # Extract location from the span with class "location"
        try:
            location_elem = event.find_element(By.CSS_SELECTOR, "span.location")
            location_text = location_elem.text.strip()
        except Exception:
            location_text = ""
        
        # Extract the "from price" text
        try:
            from_price = event.find_element(By.CLASS_NAME, "from-price").text.strip()
        except Exception:
            from_price = ""
        
        # Extract the "Avg. price" text
        try:
            avg_price_elem = event.find_element(By.XPATH, './/div[contains(text(), "Avg. price")]')
            avg_price = avg_price_elem.text.strip()
        except Exception:
            avg_price = ""
        
        month_events.append({
            "Month": month.capitalize(),
            "Image Alt": alt_text,
            "Date": event_date,
            "Time": time_text,
            "Venue": venue,
            "Schedule Link Text": schedule_link_text,
            "Schedule Link URL": schedule_link_url,
            "Location": location_text,
            "From Price": from_price,
            "Avg Price": avg_price
        })
    
    driver.quit()
    return month_events

# ----- MAIN SCRIPT -----
if __name__ == '__main__':
    # List of month names (lowercase) to iterate through.
    months = [
         "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    
    all_events = []
    for month in months:
        events = scrape_events_for_month(month, min_events=600)
        print(f"Scraped {len(events)} events for {month.capitalize()}.")
        all_events.extend(events)
        # Optional: wait a bit between months to be polite to the server
        time.sleep(2)
    
    print(f"Total events scraped from all months: {len(all_events)}")
    
    # Save the aggregated events to CSV.
    df = pd.DataFrame(all_events)
    csv_filename = "pittsburgh_events_all_months_with_price.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

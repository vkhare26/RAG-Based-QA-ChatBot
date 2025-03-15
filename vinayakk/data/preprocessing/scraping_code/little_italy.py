import time
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# If you need to explicitly wait for elements:
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

def scrape_little_italy_days_schedule_selenium():
    url = "https://littleitalydays.com/entertainment-schedule/"

    # Set up headless Chrome with a custom user agent
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Optional: You can do an explicit wait for certain elements to appear if needed:
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.x-col")))

    # Or just sleep a bit to allow the page to load:
    time.sleep(5)

    # Get the final rendered HTML
    html = driver.page_source
    driver.quit()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Each "day" is in a div with classes that contain "x-col"
    day_divs = soup.find_all("div", class_=lambda c: c and "x-col" in c)

    all_events = []

    for day_div in day_divs:
        # 1) Find the day heading, e.g. "Thursday, August 15", in <h1 class="x-text-content-text-primary">
        day_heading = day_div.find("h1", class_="x-text-content-text-primary")
        if not day_heading:
            continue
        day_text = day_heading.get_text(strip=True)

        # 2) Inside each day column, we have multiple <p> tags. 
        #    Some lines are STAGE headings (e.g., "Mini of Pittsburgh & First National Bank Stage at ..."),
        #    others are actual events with time + performer + description.
        current_stage = None
        p_tags = day_div.find_all("p")

        for p in p_tags:
            p_text = p.get_text(separator=" ", strip=True)

            # If this <p> looks like a stage heading (contains "Stage at"):
            if "Stage at" in p_text:
                current_stage = p_text
                continue

            # Otherwise, check if there's a <strong> tag that likely holds the time (e.g., "5:30pm")
            strong_tag = p.find("strong")
            if not strong_tag:
                continue

            time_text = strong_tag.get_text(strip=True)
            # Remove that time from the full text so we can parse performer & description
            remaining_text = p_text.replace(time_text, "", 1).strip(" -:–")

            # Many lines are in format: "Performer - Description"
            performer = remaining_text
            description = ""
            if " - " in remaining_text:
                parts = remaining_text.split(" - ", 1)
                performer = parts[0].strip()
                description = parts[1].strip()

            event_data = {
                "day": day_text,
                "stage": current_stage,
                "time": time_text,
                "performer": performer,
                "description": description
            }
            all_events.append(event_data)

    # Convert list of dicts to a DataFrame
    df = pd.DataFrame(all_events)
    return df

if __name__ == "__main__":
    df_schedule = scrape_little_italy_days_schedule_selenium()
    print(df_schedule)

    # Save to CSV
    df_schedule.to_csv("little_italy_days_schedule.csv", index=False)

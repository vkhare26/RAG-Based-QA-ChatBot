import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure your webdriver (make sure chromedriver is installed and in your PATH)
driver = webdriver.Chrome()  # or provide Service('path/to/chromedriver')

# URL to scrape
url = ("https://tickets-center.com/search/Byham-Theater-tickets/?venueId=1982&venueName=Byham+Theater&"
       "vaid=1532&tagid=207&nid=1&accid=9493575329&campaignid=284247242&adgroupid=177185326729&"
       "cid=732009609514&akwd=byham%20theatre%20pittsburgh&mt=p&network=g&dist=s&adposition=&device=c&"
       "ismobile=false&devicemodel=&placement=&target=&random=7915366315994365886&loc_physical_ms=9005913&"
       "loc_interest_ms=9060378&exid=&fiid=&vx=0&gad_source=1&gclid=CjwKCAjwp8--BhBREiwAj7og17zf-blaxjj5Hjketiu3W77uM54SEanU22lpb-oNA59TSWLZzfcHlxoCh9sQAvD_BwE")

driver.get(url)

# Wait until the event items are present (adjust timeout as needed)
wait = WebDriverWait(driver, 10)
event_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.event-item.event-search-result")))

data = []
for event in event_items:
    # Extracting event details. Adjust the selectors if the page structure differs.
    try:
        event_name = event.find_element(By.CSS_SELECTOR, "div.event-name").text
    except Exception:
        event_name = ""
    try:
        date_text = event.find_element(By.CSS_SELECTOR, "div.cal-box span.month-day").text
    except Exception:
        date_text = ""
    try:
        time_text = event.find_element(By.CSS_SELECTOR, "div.cal-box span.time").text
    except Exception:
        time_text = ""
    try:
        location = event.find_element(By.CSS_SELECTOR, "div.event-location").text
    except Exception:
        location = ""
    try:
        note = event.find_element(By.CSS_SELECTOR, "div.event-note").text
    except Exception:
        note = ""
    link = event.get_attribute("href")
    
    data.append({
        "Event Name": event_name,
        "Date": date_text,
        "Time": time_text,
        "Location": location,
        "Note": note,
        "Link": link
    })

# Write data to CSV
if data:
    keys = data[0].keys()
    with open("byham.csv", "w", newline="", encoding="utf-8") as csvfile:
        dict_writer = csv.DictWriter(csvfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print("Data saved to events.csv")
else:
    print("No event data found.")

driver.quit()

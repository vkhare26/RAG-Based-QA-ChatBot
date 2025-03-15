import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def store_events_txt(events_data, filename="spring_carnival.txt"):
    """
    Stores the flat list of event dictionaries into a text file,
    writing each event on a new line in a readable format.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for event in events_data:
            f.write(json.dumps(event, indent=4) + "\n\n")
    print(f"Stored {len(events_data)} events in {filename}")

# Set up Selenium WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no GUI)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.cmu.edu/engage/alumni/events/campus/index.html")
wait = WebDriverWait(driver, 15)

event_data = []

# Wait for the event elements to load
grid_container = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "div.grid.column3.darkgrey.boxes.js-list")
))

# Find all event containers inside the grid
event_divs = grid_container.find_elements(By.XPATH, "./div")
event_links = []
event_titles = []

for event in event_divs:
    anchors = event.find_elements(By.TAG_NAME, "a")
    event_link = None
    for a in anchors:
        href = a.get_attribute("href")
        if href and "flickr.com" not in href and a.text.strip():
            event_link = href
            break
    try:
        title = event.find_element(By.TAG_NAME, "strong").text.strip()
    except Exception:
        title = "No title found"
    
    if event_link:
        event_links.append(event_link)
        event_titles.append(title)
        print("Event link found:", event_link)
    else:
        try:
            description = event.find_element(By.TAG_NAME, "span").text.strip()
            eventObj = {
                "title": title,
                "description": description
            }
            event_data.append(eventObj)
        except Exception:
            pass

for link, title in zip(event_links, event_titles):
    driver.get(link)
    content_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content > div")))

    try:
        h1_element = content_div.find_element(By.TAG_NAME, "h1")
        h1_text = h1_element.text.strip()
        lines = [line.strip() for line in h1_text.splitlines() if line.strip()]
        title = lines[0] if lines else ""
        date_text = lines[1] if len(lines) > 1 else ""
    except Exception:
        date_text = ""

    paragraphs = content_div.find_elements(By.TAG_NAME, "p")
    description = "\n\n".join(p.text.strip() for p in paragraphs if p.text.strip())
    
    print("Title:", title)
    print("Date:", date_text)
    print("Description:\n", description)
    
    eventObj = {
        "title": title,
        "date": date_text,
        "description": description,
        "event_url": link
    }
    event_data.append(eventObj)

store_events_txt(event_data)
driver.quit()

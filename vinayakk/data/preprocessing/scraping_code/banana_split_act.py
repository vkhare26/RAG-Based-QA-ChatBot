import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the Selenium driver (here using Chrome)
options = webdriver.ChromeOptions()
# Uncomment below for headless mode if desired
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Replace with your target URL
url = "https://bananasplitfest.com/activities/"
driver.get(url)

# Wait for the page to load completely (adjust time as needed)
time.sleep(5)

# Locate the container with the content
page_content = driver.find_element(By.CSS_SELECTOR, "div.page-content")

# Within this container, find all elements of interest: headings, paragraphs, and links.
elements = page_content.find_elements(By.XPATH, ".//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6 or self::p or self::a]")

# Prepare a list to store rows (each row: tag, text, link if any)
rows = []
for el in elements:
    tag = el.tag_name
    text = el.text.strip()
    link = ""
    # For links, get the href attribute
    if tag.lower() == "a":
        link = el.get_attribute("href") or ""
    rows.append([tag, text, link])

# Write the extracted details to a CSV file
csv_filename = "banana_split_details.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Tag", "Text", "Link"])
    writer.writerows(rows)

print(f"CSV file '{csv_filename}' created with the extracted details.")

# Clean up and close the browser
driver.quit()

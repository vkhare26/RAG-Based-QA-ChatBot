import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_carnegie_museums_about():
    """
    Scrapes text from:
      - The main "About Us" content on https://carnegiemuseums.org/about-us/
      - Each item in the item-grid, including the short summary on the main page
        and the full text from that item's detail link.
    Saves results to 'carnegie_about.csv'.
    """

    start_url = "https://carnegiemuseums.org/about-us/"

    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(start_url)
    time.sleep(3)  # wait for the page to load

    results = []

    # 1) Scrape the main "About Us" text from the first content-container
    #    that's NOT the item-grid. There are at least two .content-container elements:
    #    - The main "About Us" block
    #    - The "item-grid" block
    # We can find them all, then pick the first that doesn't have 'item-grid'.
    all_containers = driver.find_elements(By.CSS_SELECTOR, "div.content-container")
    about_container = None
    for c in all_containers:
        classes = c.get_attribute("class")
        if "item-grid" not in classes:
            about_container = c
            break

    about_text = "N/A"
    if about_container:
        # Gather all paragraphs from about_container
        paras = about_container.find_elements(By.CSS_SELECTOR, "p")
        about_paras = []
        for p in paras:
            txt = p.text.strip()
            if txt:
                about_paras.append(txt)
        if about_paras:
            about_text = "\n\n".join(about_paras)

    # We'll store it as a single row
    results.append({
        "type": "about-us",
        "title": "About Us (main)",
        "summary": "",  # no short summary
        "full_text": about_text
    })

    # 2) Scrape each item in .content-container.item-grid
    try:
        item_grid = driver.find_element(By.CSS_SELECTOR, "div.content-container.item-grid")
        items = item_grid.find_elements(By.CSS_SELECTOR, "div.activity")
    except:
        items = []

    for item in items:
        # a) Title from <h3>
        title = "N/A"
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, "h3")
            title = title_elem.text.strip()
        except:
            pass

        # b) Short summary from the <p> in each .activity
        summary = "N/A"
        try:
            p_elem = item.find_element(By.CSS_SELECTOR, "p")
            summary = p_elem.text.strip()
        except:
            pass

        # c) Link from <a> child
        detail_link = "N/A"
        try:
            a_elem = item.find_element(By.CSS_SELECTOR, "a")
            detail_link = a_elem.get_attribute("href")
        except:
            pass

        # d) Now open that link in a new tab to get full text
        full_text = "N/A"
        if detail_link and detail_link != "N/A":
            driver.execute_script("window.open(arguments[0], '_blank');", detail_link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            try:
                # We'll gather all <p> paragraphs from that page
                detail_paras = driver.find_elements(By.CSS_SELECTOR, "p")
                text_list = []
                for dp in detail_paras:
                    t = dp.text.strip()
                    if t:
                        text_list.append(t)
                if text_list:
                    full_text = "\n\n".join(text_list)
            except:
                pass

            # close detail tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # e) Store in results
        results.append({
            "type": "grid-item",
            "title": title,
            "summary": summary,
            "full_text": full_text
        })

    driver.quit()

    # 3) Save to CSV
    df = pd.DataFrame(results)
    df.to_csv("carnegie_about.csv", index=False, encoding="utf-8")
    print(f"Saved {len(df)} records to 'carnegie_about.csv'.")

if __name__ == "__main__":
    scrape_carnegie_museums_about()

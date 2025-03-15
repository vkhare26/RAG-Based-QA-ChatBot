import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_ps_about_landing():
    """
    Scrapes subnav-item links and biography links from the Pittsburgh Symphony
    'About' landing page. Gathers short text from the page, plus all <p> paragraphs
    from the linked detail page. Saves each item as a separate paragraph in a .txt file.
    """

    start_url = "https://www.pittsburghsymphony.org/pso_home/web/about-landing"

    # Headless Chrome config
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(start_url)
    time.sleep(3)

    # We'll store each item as a big string (a "paragraph").
    paragraphs = []

    # 1) SCRAPE ALL subnav-item blocks
    subnav_items = driver.find_elements(By.CSS_SELECTOR, "article.subnav-item")
    print(f"Found {len(subnav_items)} subnav-item blocks.")

    for item in subnav_items:
        # Title from h3.subnav-item-title
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, "h3.subnav-item-title")
            title_text = title_elem.text.strip()
        except:
            title_text = "N/A"

        # Short text from .subnav-item-description
        try:
            desc_elem = item.find_element(By.CSS_SELECTOR, ".subnav-item-description")
            short_text = desc_elem.text.strip()
        except:
            short_text = "N/A"

        # Link from subnav-item-description a
        detail_link = "N/A"
        try:
            link_elem = item.find_element(By.CSS_SELECTOR, ".subnav-item-description a")
            detail_link = link_elem.get_attribute("href")
        except:
            pass

        # Now open detail_link in new tab to gather paragraphs
        detail_paras = []
        if detail_link != "N/A":
            driver.execute_script("window.open(arguments[0], '_blank');", detail_link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            try:
                # Gather all <p> paragraphs from that page
                p_elems = driver.find_elements(By.CSS_SELECTOR, "p")
                for p in p_elems:
                    txt = p.text.strip()
                    if txt:
                        detail_paras.append(txt)
            except:
                pass

            # Close tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Combine everything into one paragraph
        # (You can format differently if you prefer.)
        # We'll do: 
        # 1) Title line
        # 2) Short text
        # 3) Blank line
        # 4) Detail paragraphs
        item_paragraph = f"TITLE: {title_text}\n\nSHORT:\n{short_text}"
        if detail_paras:
            item_paragraph += "\n\nDETAIL:\n" + "\n".join(detail_paras)

        paragraphs.append(item_paragraph)

    # 2) SCRAPE BIOGRAPHY SECTIONS (e.g., biography1, biography)
    # They each have a link as well, let's do similarly
    # We'll look for section.biography or section.biography1
    biography_sections = driver.find_elements(By.CSS_SELECTOR, "section.biography, section.biography1")
    print(f"Found {len(biography_sections)} biography sections.")

    for bio_sec in biography_sections:
        # Each has a <article> inside, or .bio, .bio1
        try:
            article = bio_sec.find_element(By.CSS_SELECTOR, "article.bio, article.bio1")
        except:
            article = None

        if article:
            # Title from h3
            try:
                h3_elem = article.find_element(By.CSS_SELECTOR, "h3")
                bio_title = h3_elem.text.strip()
            except:
                bio_title = "N/A"

            # Short text from .bio-text or .bio1
            try:
                bio_text_elem = article.find_element(By.CSS_SELECTOR, ".bio-text")
                short_text = bio_text_elem.text.strip()
            except:
                short_text = "N/A"

            # Link inside that article (like "Learn More →")
            detail_link = "N/A"
            try:
                link_elem = article.find_element(By.CSS_SELECTOR, "a")
                detail_link = link_elem.get_attribute("href")
            except:
                pass

            detail_paras = []
            if detail_link != "N/A":
                driver.execute_script("window.open(arguments[0], '_blank');", detail_link)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

                try:
                    # gather paragraphs
                    p_elems = driver.find_elements(By.CSS_SELECTOR, "p")
                    for p in p_elems:
                        txt = p.text.strip()
                        if txt:
                            detail_paras.append(txt)
                except:
                    pass

                # close
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            item_paragraph = f"TITLE: {bio_title}\n\nSHORT:\n{short_text}"
            if detail_paras:
                item_paragraph += "\n\nDETAIL:\n" + "\n".join(detail_paras)

            paragraphs.append(item_paragraph)

    driver.quit()

    # 3) WRITE TO A .txt FILE
    # Each item is a separate paragraph separated by blank lines
    output_text = "\n\n--------------------------------\n\n".join(paragraphs)
    with open("pso_about_items.txt", "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Scraped {len(paragraphs)} items total. Saved to 'pso_about_items.txt'.")

if __name__ == "__main__":
    scrape_ps_about_landing()

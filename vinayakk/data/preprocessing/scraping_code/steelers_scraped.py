import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fpdf import FPDF

def scrape_steelers_2025_opponents_to_pdf(pdf_filename="steelers_2025_opponents.pdf"):
    url = "https://www.steelers.com/news/steelers-2025-opponents-determined"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # optional user-agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    time.sleep(3)  # wait for the page to load

    # 1) Find the article container
    try:
        container = driver.find_element(By.CSS_SELECTOR, "div.nfl-c-article__container")
    except:
        print("Could not find the main article container.")
        driver.quit()
        return

    # 2) Find all paragraphs in <div class="nfl-c-body-part nfl-c-body-part--text"> -> <p>
    paragraphs = container.find_elements(By.CSS_SELECTOR, "div.nfl-c-body-part.nfl-c-body-part--text p")

    all_paragraphs = []
    for p in paragraphs:
        text = p.text.strip()
        if text:
            all_paragraphs.append(text)

    driver.quit()

    # --- Create a PDF with FPDF ---
    # If you encounter Unicode errors, consider adding a TrueType font that supports extended chars.
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "steelers", ln=True, align="C")  # center-aligned

    # Paragraphs
    pdf.set_font("Arial", "", 12)
    for paragraph in all_paragraphs:
        pdf.multi_cell(0, 10, paragraph, align="L")
        pdf.ln(5)  # extra space after each paragraph

    pdf.output(pdf_filename, "F")
    print(f"Scraped paragraphs saved to '{pdf_filename}'.")

if __name__ == "__main__":
    scrape_steelers_2025_opponents_to_pdf("steelers_2025_opponents.pdf")

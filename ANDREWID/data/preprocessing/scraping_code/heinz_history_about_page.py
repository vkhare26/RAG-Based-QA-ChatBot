import requests
from bs4 import BeautifulSoup

def scrape_headings_and_paragraphs(url):
    """
    Scrapes all textual information from <h1>...<h6> and <p> tags,
    preserving their order in the HTML.
    Returns a list of tuples: (tag_name, text_content).
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all heading and paragraph tags in the order they appear
    elements = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"])

    results = []
    for el in elements:
        # Clean up the text
        text_content = el.get_text(strip=True)
        # Skip empty texts
        if text_content:
            results.append((el.name, text_content))

    return results

if __name__ == "__main__":
    # Replace with the actual URL of the page you want to scrape
    url = "https://www.example.com"
    scraped_data = scrape_headings_and_paragraphs(url)

    # Print or process the scraped data
    for tag, text in scraped_data:
        print(f"[{tag.upper()}] {text}")

import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.thefrickpittsburgh.org"

def get_page_url(page_number=1):
    """
    Build the URL for a given page number.
    This matches the pattern from the question:
    ?search=1&page=<page_number>&search_date_from=3/01/2025&search_date_to=8/31/2025
    """
    return (
        f"{BASE_URL}/calendar?search=1"
        f"&page={page_number}"
        f"&search_date_from=3%2F01%2F2025"
        f"&search_date_to=8%2F31%2F2025"
    )

def scrape_main_listing(page_number=1):
    """
    Scrapes the main listing on a given calendar page (1 or 2).
    Returns a list of dictionaries, each describing one event.
    """
    url = get_page_url(page_number)
    print(f"Scraping main listing from: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events_data = []

    # Each event is in a <div class="item"> inside .calendar-event-listing
    event_items = soup.select("div.calendar-event-listing div.item")
    for item in event_items:
        title_el = item.select_one("h3.item-title")
        event_title = title_el.get_text(strip=True) if title_el else ""

        # Extract the date/time from <div class="event-info">
        date_span = item.select_one(".event-info span.date")
        time_span = item.select_one(".event-info span.time")
        date_text = date_span.get_text(" ", strip=True) if date_span else ""
        time_text = time_span.get_text(" ", strip=True) if time_span else ""

        # Short description from <div class="textbox">
        short_text_el = item.select_one(".textbox")
        short_text = short_text_el.get_text(strip=True) if short_text_el else ""

        # The "Learn More" button typically is the first link in .btn-block
        learn_more_el = item.select_one(".btn-block a.btn-default")
        learn_more_url = ""
        if learn_more_el and learn_more_el.has_attr("href"):
            learn_more_url = learn_more_el["href"]
            # If it's a relative link, build the absolute URL
            if learn_more_url.startswith("/"):
                learn_more_url = BASE_URL + learn_more_url
            elif not learn_more_url.startswith("http"):
                learn_more_url = BASE_URL + "/" + learn_more_url

        event_dict = {
            "title": event_title,
            "date": date_text,
            "time": time_text,
            "short_text": short_text,
            "learn_more_url": learn_more_url,
            "description": ""  # Will fill this after scraping the "Learn More" page
        }
        events_data.append(event_dict)

    return events_data

def scrape_learn_more_description(event):
    """
    Given an event dictionary that has a 'learn_more_url',
    scrape the "Learn More" page to get additional info and
    add it to the event["description"].
    """
    if not event["learn_more_url"]:
        return event  # Nothing to do if there's no link

    print(f"   Scraping description from: {event['learn_more_url']}")
    try:
        resp = requests.get(event["learn_more_url"])
        soup = BeautifulSoup(resp.text, "html.parser")
        # In real usage, figure out the best selector for the main content:
        # For demonstration, let's assume the event description is in a <div class="textbox">
        desc_el = soup.select_one("div.textbox, div.content-body")
        if desc_el:
            event["description"] = desc_el.get_text("\n", strip=True)
        else:
            # Fallback if the main content is not found
            event["description"] = soup.get_text("\n", strip=True)
    except Exception as e:
        print(f"   Error scraping description: {e}")
        event["description"] = ""

    return event

def main():
    all_events = []
    # We only want pages 1 and 2
    for page_num in [1, 2]:
        events_on_page = scrape_main_listing(page_num)
        # For each event, scrape the "Learn More" description
        for ev in events_on_page:
            ev = scrape_learn_more_description(ev)
            all_events.append(ev)
        # Sleep to be polite (optional)
        time.sleep(1)

    # Write the final data to a CSV
    csv_filename = "frick_events.csv"
    print(f"\nWriting data to CSV: {csv_filename}")
    # Define the field names/columns we want
    fieldnames = ["title", "date", "time", "short_text", "learn_more_url", "description"]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for event in all_events:
            # Optionally, you can replace newlines in the description if you want one-line CSV
            # event["description"] = event["description"].replace("\n", " ")
            writer.writerow(event)

    print("Scraping and CSV export complete!")

if __name__ == "__main__":
    main()

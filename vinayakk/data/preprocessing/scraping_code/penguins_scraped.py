import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_pens_schedule_by_week():
    """
    Scrapes the Penguins schedule from 2025-03-14 to 2025-04-11
    by looping every 7 days and constructing the URL:
      https://www.nhl.com/penguins/schedule/YYYY-MM-DD/list

    For each page, we parse:
      - <h3 id="YYYY-MM-DD"> headings
      - Each day's table rows (matchup, time, broadcasters, tickets link)

    We collect them all in a DataFrame, then filter to keep
    only games from 2025-03-14 through 2025-04-11.
    """

    start_date = datetime.date(2025, 3, 14)
    end_date = datetime.date(2025, 4, 11)
    delta_7_days = datetime.timedelta(days=7)

    # Selenium options
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

    all_games = []

    current_date = start_date
    while current_date <= end_date:
        # Build the URL, e.g. "2025-03-14" => "https://www.nhl.com/penguins/schedule/2025-03-14/list"
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://www.nhl.com/penguins/schedule/{date_str}/list"
        print(f"Scraping weekly URL: {url}")

        driver.get(url)
        time.sleep(3)  # wait for the page to load

        # Find all day headings: <h3 id="YYYY-MM-DD">
        day_headings = driver.find_elements(By.CSS_SELECTOR, "h3[id^='2025-']")
        for heading in day_headings:
            day_str = heading.get_attribute("id").strip()  # e.g. "2025-03-15"
            try:
                day_obj = datetime.datetime.strptime(day_str, "%Y-%m-%d").date()
            except:
                continue

            # The schedule for this day is in the next sibling container
            try:
                day_container = heading.find_element(
                    By.XPATH,
                    "./ancestor::div[contains(@class,'sc-bSywJw')]/following-sibling::div[1]"
                )
                tables = day_container.find_elements(By.CSS_SELECTOR, "table.rt-table")
                if not tables:
                    continue
                day_table = tables[0]
                rows = day_table.find_elements(By.CSS_SELECTOR, "tbody.rt-tbody > tr.rt-tr")
            except:
                rows = []

            for row in rows:
                matchup = "N/A"
                game_time = "N/A"
                tv_networks = "N/A"
                tickets_link = "N/A"

                # Matchup
                try:
                    matchup_col = row.find_element(By.CSS_SELECTOR, "th[scope='row']")
                    matchup = matchup_col.text.strip()  # e.g. "Devils @ Penguins"
                except:
                    pass

                # Time
                try:
                    time_col = row.find_element(By.CSS_SELECTOR, "td.scheduleColumn.fullWidth")
                    time_span = time_col.find_element(By.CSS_SELECTOR, "span.sc-cLsBkd")
                    game_time = time_span.text.strip()  # e.g. "3:00 PM EDT"
                except:
                    pass

                # Broadcasters
                try:
                    broadcast_col = row.find_element(By.CSS_SELECTOR, "td.networksColumn")
                    networks_text = broadcast_col.text.strip()
                    # e.g. "ABC\nESPN+"
                    tv_networks = networks_text.replace("\n", ", ")
                except:
                    pass

                # Tickets link
                try:
                    links_col = row.find_element(By.CSS_SELECTOR, "td.gameLinksColumn")
                    tickets_a = links_col.find_element(By.XPATH, ".//a[contains(text(),'Tickets')]")
                    tickets_link = tickets_a.get_attribute("href")
                except:
                    pass

                game_data = {
                    "date": day_obj.isoformat(),
                    "matchup": matchup,
                    "time": game_time,
                    "broadcasters": tv_networks,
                    "tickets_link": tickets_link
                }
                all_games.append(game_data)

        # Move to the next week
        current_date += delta_7_days

    driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(all_games)

    if df.empty:
        print("No games found.")
        return df

    # Filter for 2025-03-14 <= date <= 2025-04-11
    df["date"] = pd.to_datetime(df["date"]).dt.date
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    df_filtered = df[mask].copy()

    return df_filtered

if __name__ == "__main__":
    df_schedule = scrape_pens_schedule_by_week()
    print(df_schedule)
    df_schedule.to_csv("penguins_schedule_2025_mar14_apr11_byweek.csv", index=False)
    print("Done! Data saved to penguins_schedule_2025_mar14_apr11_byweek.csv")

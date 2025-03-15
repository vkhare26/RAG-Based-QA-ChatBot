import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_pirates_schedule_2025():
    """
    Scrapes the Pittsburgh Pirates schedule from March 2025 to September 2025.
    For each month, parse each game row:
      - Date & Day (with the year appended)
      - Opponent
      - Home/Away
      - Time
      - TV Broadcast
      - Tickets link
    Then store everything in a DataFrame.
    """

    base_url = "https://www.mlb.com/pirates/schedule/2025-{:02d}/list"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # Optional user-agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    all_games = []

    # Loop from March (3) to September (9)
    for month in range(3, 10):
        url = base_url.format(month)
        print(f"Scraping month {month:02d}: {url}")
        driver.get(url)

        time.sleep(3)  # Wait for the page to load

        # Find all schedule tables on the page
        tables = driver.find_elements(By.CSS_SELECTOR, "div.list-mode-table-wrapper table")

        for tbl in tables:
            # Each game is typically in <tr class="primary-row-tr">
            rows = tbl.find_elements(By.CSS_SELECTOR, "tr.primary-row-tr")
            for row in rows:
                # 1) Date from <td class="date-td"> -> <div class="month-date">, <div class="weekday">
                try:
                    date_td = row.find_element(By.CSS_SELECTOR, "td.date-td")
                    month_date_elem = date_td.find_element(By.CSS_SELECTOR, "div.month-date")
                    month_date = month_date_elem.text.strip()  # e.g. "Mar 11"
                    weekday_elem = date_td.find_element(By.CSS_SELECTOR, "div.weekday")
                    weekday = weekday_elem.text.strip()       # e.g. "Tue"

                    # Append the year 2025 to the month_date
                    # e.g. "Mar 11" => "Mar 11, 2025"
                    final_date = f"{month_date}, 2025"
                except:
                    final_date = "N/A"
                    weekday = "N/A"

                # 2) Opponent & Home/Away
                opponent = "N/A"
                home_or_away = "N/A"
                try:
                    matchup_td = row.find_element(By.CSS_SELECTOR, "td.matchup-td")

                    # Opponent name
                    try:
                        opp_name_elem = matchup_td.find_element(By.CSS_SELECTOR, "div.opponent-name")
                        opponent = opp_name_elem.text.strip()
                    except:
                        pass

                    # Check if <div class="at"> is displayed => "Away", <div class="vs"> => "Home"
                    try:
                        at_div = matchup_td.find_element(By.CSS_SELECTOR, "div.at")
                        if at_div.is_displayed():
                            home_or_away = "Away"
                    except:
                        pass

                    try:
                        vs_div = matchup_td.find_element(By.CSS_SELECTOR, "div.vs")
                        if vs_div.is_displayed():
                            home_or_away = "Home"
                    except:
                        pass

                except:
                    pass

                # 3) Time
                game_time = "N/A"
                try:
                    time_td = row.find_element(By.CSS_SELECTOR, "td.time-or-score-td-large")
                    time_link = time_td.find_element(By.CSS_SELECTOR, "a.time")
                    primary_time_elem = time_link.find_element(By.CSS_SELECTOR, "div.primary-time")
                    game_time = primary_time_elem.text.strip()  # e.g. "1:05 pm EDT"
                except:
                    pass

                # 4) TV Broadcast
                tv_broadcast = "N/A"
                try:
                    broadcast_td = row.find_element(By.CSS_SELECTOR, "td.broadcasters-or-watch-td-large")
                    tv_div = broadcast_td.find_element(By.CSS_SELECTOR, "div.broadcasters div.tv span.list")
                    tv_broadcast = tv_div.text.strip()  # e.g. "SportsNet-PIT"
                except:
                    pass

                # 5) Tickets link
                tickets_link = "N/A"
                try:
                    tickets_td = row.find_element(By.CSS_SELECTOR, "td.tickets-td-large")
                    link_elem = tickets_td.find_element(By.CSS_SELECTOR, "a.p-button__link")
                    tickets_link = link_elem.get_attribute("href")
                except:
                    pass

                # Build a dictionary for this game
                game_info = {
                    "month_url": f"{month:02d}",   # e.g. "03" for March
                    "date": final_date,           # e.g. "Mar 11, 2025"
                    "weekday": weekday,           # e.g. "Tue"
                    "opponent": opponent,         # e.g. "Yankees"
                    "home_or_away": home_or_away, # "Home" or "Away"
                    "time": game_time,            # e.g. "1:05 pm EDT"
                    "tv_broadcast": tv_broadcast, # e.g. "SportsNet-PIT"
                    "tickets_link": tickets_link
                }
                all_games.append(game_info)

    driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(all_games)
    return df

if __name__ == "__main__":
    df_schedule = scrape_pirates_schedule_2025()
    print(df_schedule)
    # Optionally, save to CSV
    df_schedule.to_csv("pirates_schedule_2025_mar_sep.csv", index=False)
    print("Done! Data saved to pirates_schedule_2025_mar_sep.csv")

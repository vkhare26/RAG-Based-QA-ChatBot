import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def fetch_and_append_honorary_chair_text():
    options = webdriver.ChromeOptions()
    # Uncomment the next line for headless mode if desired:
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    # Load the Banana Split Fest History page (adjust the URL if needed)
    driver.get("https://bananasplitfest.com/history/")
    
    # Wait for the page to load fully
    time.sleep(5)
    
    # Locate the container that holds the "Honorary Chair" details.
    # This XPath finds a div with a class containing "elementor-widget-wrap" that has a descendant h2 with text "Honorary Chair"
    container = driver.find_element(By.XPATH, "//div[contains(@class, 'elementor-widget-wrap') and .//h2[contains(text(),'Honorary Chair')]]")
    text_content = container.text.strip()
    
    driver.quit()
    
    # Append the fetched text to the file
    with open("bananasplitfest_history1.txt", "a", encoding="utf-8") as f:
        f.write(text_content + "\n\n")
    
    print("Text appended to bananasplitfest_history1.txt")

if __name__ == "__main__":
    fetch_and_append_honorary_chair_text()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium_stealth import stealth
import math
import json
import requests

def search_google_web_automation(query, num_results, json_file_name='durchsuchte-webseiten.json'):
    # Enforce limits on num_results
    if num_results < 5:
        num_results = 5
    elif num_results > 100:
        num_results = 100

    # Calculate the number of pages
    n_pages = math.ceil(num_results / 10)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=chrome_options)

    stealth(
        driver,
        languages=["DE", "de"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    results = []
    counter = 0
    for page in range(1, n_pages + 1):
        url = (
            "http://www.google.de/search?q="
            + str(query)
            + "&start="
            + str((page - 1) * 10)
        )

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        search = soup.find_all("div", class_="yuRUbf")
        
        for h in search:
            if counter == num_results:
                break
            counter += 1
            title_tag = h.a.find('h3')
            title = title_tag.text if title_tag else ''

            link = h.a.get("href")
            rank = counter

            # Extract titles (headings) from the page
            try:
                soup_page = BeautifulSoup(requests.get(link).content, 'html.parser')
                titles = [element.text.strip() for element in soup_page.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            except Exception as e:
                print(f"Error extracting titles from {link}: {e}")
                titles = []

            results.append(
                {
                    "title": title,
                    "url": link,
                    "domain": urlparse(link).netloc,
                    "rank": rank,
                    "titles": titles
                }
            )

        if counter == num_results:
            break

    driver.quit()

    # Store results in the specified JSON file
    with open(json_file_name, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    return results

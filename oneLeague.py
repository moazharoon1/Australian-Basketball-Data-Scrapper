from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time
import os

def extract_2023_urls(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        time.sleep(5)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a') if '2023' in link.get('href', '')]

    return links

def extract_table_data(section):
    all_tables_data = []

    # Grab the tables inside the 'dataTables_scrollBody' divs
    data_tables = section.find_all('div', {'class': 'dataTables_scrollBody'})

    for dt in data_tables:
        table = dt.find('table')
        # Extract table headers
        headers = [header.text.strip() for header in table.thead.find_all('th') if header.text.strip()]

        # Extract table rows
        data = []
        tbody = table.tbody or table  # Use tbody if it exists, otherwise use table itself
        for row in tbody.find_all('tr'):
            values = [col.text.strip() for col in row.find_all('td')]
            data.append(values)

        all_tables_data.append((headers, data))
    
    return all_tables_data

def extract_and_save_data(url, gender):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        time.sleep(5)
        
        if "404 Not Found" in browser.page_source:
            print(f"Skipping URL due to 404 error: {url}")
            return

        html_content = browser.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    scoring_tables_data = extract_table_data(soup.find('div', {'id': 'scoring-2'}))
    nonscoring_tables_data = extract_table_data(soup.find('div', {'id': 'non-scoring-2'}))

    sheet_names = ["Season Total", "Season Per Game", "Wins", "Losses", "Home", "Away"]

    # Extract the portion after "2023" and join all alphabets without spaces
    split_url = url.split('2023')
    if len(split_url) > 1:
        file_name_base = ''.join(split_url[1].split('%20')).rstrip(".html")
    else:
        print(f"Unexpected URL format: {url}")
        print(url)
        print

    scoring_path = os.path.join("NBA 1 WEST", f"NBA {gender.upper()}", "SCORING", f'{file_name_base}_Scoring.xlsx')
    nonscoring_path = os.path.join("NBA 1 WEST", f"NBA {gender.upper()}", "NON SCORING", f'{file_name_base}_Nonscoring.xlsx')

    with pd.ExcelWriter(scoring_path) as writer:
        for index, (headers, data) in enumerate(scoring_tables_data):
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(writer, sheet_name=sheet_names[index], index=False)

    with pd.ExcelWriter(nonscoring_path) as writer:
        for index, (headers, data) in enumerate(nonscoring_tables_data):
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(writer, sheet_name=sheet_names[index], index=False)

if __name__ == "__main__":
    # Extract URLs from the main page
    url = "http://hoopsdb.net/NBL1West.html"
    all_links = extract_2023_urls(url)

    men_links = [link for link in all_links if "Men" in link]
    women_links = [link for link in all_links if "Women" in link]

    with open("2023_links.txt", "w") as f:
        for link in all_links:
            f.write(link + "\n")

    for link in men_links:
        extract_and_save_data(link, "MEN")

    for link in women_links:
        extract_and_save_data(link, "WOMEN")

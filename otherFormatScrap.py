from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def extract_tables_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the desired tables based on the trajectory provided
    player_stats = soup.find(id="player-stats")
    tables = player_stats.find_all('table')

    table_data = []

    for table in tables:
        thead = table.find('thead')
        tbody = table.find('tbody')

        if thead and tbody:
            headers = [th.text for th in thead.find_all('th')]
            rows = tbody.find_all('tr')
            data = []

            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append(cols)

            table_data.append({
                'headers': headers,
                'data': data
            })

    return table_data

def main():
    url = "http://hoopsdb.net/reports/NBL1-West-M-2021-Cockburn.html"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        time.sleep(5)  # Wait for the page to load
        html_content = browser.page_source

    tables = extract_tables_from_html(html_content)

    with pd.ExcelWriter("output.xlsx") as writer:
        for index, table in enumerate(tables):
            if len(table['headers']) > 1:  # Filtering tables with only one column
                df = pd.DataFrame(table['data'], columns=table['headers'])
                df.to_excel(writer, sheet_name=f"Table_{index+1}", index=False)

if __name__ == "__main__":
    main()

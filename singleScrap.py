from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time

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

# ... [rest of your imports and functions]

def main():
    url = "http://hoopsdb.net/reports/NBL1%20West%20Women%202023%20SW%20Slammers.html"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)
        time.sleep(5)  # Wait for the page to load
        html_content = browser.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    scoring_tables_data = extract_table_data(soup.find('div', {'id': 'scoring-2'}))
    nonscoring_tables_data = extract_table_data(soup.find('div', {'id': 'non-scoring-2'}))

    sheet_names = ["Season Total", "Season Per Game", "Wins", "Losses", "Away", "Home"]

    # Extract file name from the URL
    file_name_base = url.rstrip(".html").split('%20')[-1]

    with pd.ExcelWriter(f'{file_name_base} scoring.xlsx') as writer:
        for index, (headers, data) in enumerate(scoring_tables_data):
            # Skip if the length of data doesn't match the headers
            if not data or len(data[0]) != len(headers):
                continue
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(writer, sheet_name=sheet_names[index], index=False)

    with pd.ExcelWriter(f'{file_name_base} nonscoring.xlsx') as writer:
        for index, (headers, data) in enumerate(nonscoring_tables_data):
            # Skip if the length of data doesn't match the headers
            if not data or len(data[0]) != len(headers):
                continue
            df = pd.DataFrame(data, columns=headers)
            df.to_excel(writer, sheet_name=sheet_names[index], index=False)

if __name__ == "__main__":
    main()
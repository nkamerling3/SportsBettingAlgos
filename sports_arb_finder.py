import requests
from bs4 import BeautifulSoup


def find_arb(url):
    website = url
    response = requests.get(website)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return response.text
        # pe_ratios = []
        #
        # table = soup.find('table', class_='historical_data_table')
        # rows = table.find_all('tr')[1:]
        #
        # for row in rows:
        #     cells = row.find_all('td')
        #     date = cells[0].text
        #     pe_ratio = cells[1].text
        #     pe_ratios.append((date, pe_ratio))
        #
        # # Print or process the P/E ratios
        # for date, pe_ratio in pe_ratios:
        #     print(f"Date: {date}, P/E Ratio: {pe_ratio}")
    else:
        print("Failed to retrieve data. Status code:", response.status_code)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    info = find_arb(url="https://sportsbook.draftkings.com/leagues/football/nfl")
    print(info)

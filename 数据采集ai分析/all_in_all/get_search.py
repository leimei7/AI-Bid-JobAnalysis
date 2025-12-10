import requests
from bs4 import BeautifulSoup

def search(keyword,cookies, headers):
    params = {
        'key': keyword,
    }

    response = requests.get('https://www.tianyancha.com/nsearch', params=params, cookies=cookies, headers=headers)

    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    target_links = soup.find_all('a', class_='index_alink__zcia5 link-click')

    if len(target_links) > 0:
        return target_links[0]
    else:
        return None

if __name__ == '__main__':
    pass
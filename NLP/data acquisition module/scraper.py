import csv
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def parse_date(date_str):
    try:
        date_str = date_str.split('-', 1)[-1].strip()
        date_obj = datetime.strptime(date_str, '%B %d, %Y, %I:%M %p')
        return date_obj
    except ValueError:
        return None


def scrape_api_and_parse_html(scrape_page_url, csv_file):
    response = requests.get(scrape_page_url)

    if response.status_code == 200:
        data = response.json()

        html_content = data['html']

        soup = BeautifulSoup(html_content, 'html.parser')

        articles = soup.find_all('article', class_='widget-post-two')

        headlines_and_urls = [(article.find('div', class_='text').find('a').text.strip(),
                               article.find('div', class_='text').find('a')['href'])
                              for article in articles]

        for idx, (headline, url) in enumerate(headlines_and_urls, start=1):
            print(f"{idx}. {headline}")
            print(f"   URL: {url}\n")
            scrape_news_content(url, csv_file)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)


def scrape_news_content(url, csv_filename):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h2').text.strip()

        post_meta = soup.find('ul', class_='post-meta hidden-xs')
        meta_items = post_meta.find_all('li', class_='news-section-bar')

        publish_date_str = None
        update_date_str = None
        location = None

        for item in meta_items:
            text = item.get_text(strip=True)
            if 'Publish-' in text:
                publish_date_str = text
            elif 'Update-' in text:
                update_date_str = text
            elif 'fa-map-marker' in item.find('span', class_='icon').attrs.get('class', []):
                location = text

        publish_date = parse_date(publish_date_str) if publish_date_str else None
        update_date = parse_date(update_date_str) if update_date_str else None

        article_text_divs = soup.find_all('div', class_='news-article-text-block text-patter-edit ref-link')
        html_text = ''
        raw_text = ''

        for article_text_div in article_text_divs:
            paragraphs = article_text_div.find_all('p')
            for p in paragraphs:
                for a in p.find_all('a'):
                    a.extract()

                html_text += str(p) + '\n'
                raw_text += p.get_text(strip=True) + '\n'

        file_exists = os.path.isfile(csv_filename)

        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['publication_date', 'update_date', 'meta_location', 'title', 'HTML_text', 'raw_text',
                          'article_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({'publication_date': publish_date, 'update_date': update_date,
                             'meta_location': location, 'title': title,
                             'HTML_text': html_text, 'raw_text': raw_text
                                , 'article_url': url})
        print(f"Data appended to {csv_filename} successfully.")
    else:
        print("Failed to retrieve data. Status code:", response.status_code)


def scrape_multiple_urls(base_url, start_item, end_item, csv_filename):
    for item in range(start_item, end_item + 1):
        url = f"{base_url}&item={item}"
        scrape_api_and_parse_html(url, csv_filename)


def scrape_news(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h2').text.strip()

        post_meta = soup.find('ul', class_='post-meta hidden-xs')
        meta_items = post_meta.find_all('li', class_='news-section-bar')

        publish_date_str = None
        update_date_str = None
        location = None

        for item in meta_items:
            text = item.get_text(strip=True)
            if 'Publish-' in text:
                publish_date_str = text
            elif 'Update-' in text:
                update_date_str = text
            elif 'fa-map-marker' in item.find('span', class_='icon').attrs.get('class', []):
                location = text

        publish_date = parse_date(publish_date_str) if publish_date_str else None
        update_date = parse_date(update_date_str) if update_date_str else None

        article_text_divs = soup.find_all('div', class_='news-article-text-block text-patter-edit ref-link')
        html_text = ''
        raw_text = ''

        for article_text_div in article_text_divs:
            paragraphs = article_text_div.find_all('p')
            for p in paragraphs:
                for a in p.find_all('a'):
                    a.extract()

                html_text += str(p) + '\n'
                raw_text += p.get_text(strip=True) + '\n'

        return {
            'publication_date': publish_date,
            'update_date': update_date,
            'meta_location': location,
            'title': title,
            'HTML_text': html_text,
            'raw_text': raw_text,
            'article_url': url
        }
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None


if __name__ == '__main__':
    scraped_data = scrape_news(
        "https://www.unb.com.bd/category/Bangladesh/reckless-driving-triggers-multi-vehicle-collision-in-ctgs-bangabandhu-tunnel/130693")
    print(scraped_data)
    # base_url = 'https://www.unb.com.bd/api/tag-news?tag_id=54'
    # start_item = 1
    # end_item = 100  
    # csv_filename = 'scraped_data.csv'
    # scrape_multiple_urls(base_url, start_item, end_item, csv_filename)

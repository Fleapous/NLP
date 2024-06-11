import csv
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def parse_date(date_str):
    try:
        # Remove 'Publish-' or 'Update-' and leading/trailing spaces
        date_str = date_str.split('-', 1)[-1].strip()
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y, %I:%M %p')
        return date_obj
    except ValueError:
        return None  # Return None if the date string cannot be parsed


# Function to scrape the website and extract data
def scrape_api_and_parse_html(scrape_page_url, csv_file):
    # Send a GET request to the API URL
    response = requests.get(scrape_page_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Get the HTML content from the response
        html_content = data['html']

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the components with the given structure
        articles = soup.find_all('article', class_='widget-post-two')

        # Extract headlines and URLs from each article
        headlines_and_urls = [(article.find('div', class_='text').find('a').text.strip(),
                               article.find('div', class_='text').find('a')['href'])
                              for article in articles]

        # Print the extracted headlines and URLs
        for idx, (headline, url) in enumerate(headlines_and_urls, start=1):
            print(f"{idx}. {headline}")
            print(f"   URL: {url}\n")
            scrape_news_content(url, csv_file)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)


def scrape_news_content(url, csv_filename):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('h2').text.strip()

        # Extract publication date, update date, and location
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

        # Parse dates
        publish_date = parse_date(publish_date_str) if publish_date_str else None
        update_date = parse_date(update_date_str) if update_date_str else None

        # Extract article text
        article_text_divs = soup.find_all('div', class_='news-article-text-block text-patter-edit ref-link')
        html_text = ''
        raw_text = ''

        for article_text_div in article_text_divs:
            paragraphs = article_text_div.find_all('p')
            for p in paragraphs:
                # Remove <a> tags within <p> tags
                for a in p.find_all('a'):
                    a.extract()

                # Add HTML and raw text
                html_text += str(p) + '\n'
                raw_text += p.get_text(strip=True) + '\n'

        # Check if the CSV file exists
        file_exists = os.path.isfile(csv_filename)

        # Write the data to a CSV file
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['publication_date', 'update_date', 'meta_location', 'title', 'HTML_text', 'raw_text',
                          'article_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if the file doesn't exist
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
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('h2').text.strip()

        # Extract publication date, update date, and location
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

        # Parse dates
        publish_date = parse_date(publish_date_str) if publish_date_str else None
        update_date = parse_date(update_date_str) if update_date_str else None

        # Extract article text
        article_text_divs = soup.find_all('div', class_='news-article-text-block text-patter-edit ref-link')
        html_text = ''
        raw_text = ''

        for article_text_div in article_text_divs:
            paragraphs = article_text_div.find_all('p')
            for p in paragraphs:
                # Remove <a> tags within <p> tags
                for a in p.find_all('a'):
                    a.extract()

                # Add HTML and raw text
                html_text += str(p) + '\n'
                raw_text += p.get_text(strip=True) + '\n'

        # Return the extracted data as a dictionary
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scraped_data = scrape_news("https://www.unb.com.bd/category/Bangladesh/reckless-driving-triggers-multi-vehicle-collision-in-ctgs-bangabandhu-tunnel/130693")
    print(scraped_data)
    # base_url = 'https://www.unb.com.bd/api/tag-news?tag_id=54'
    # start_item = 1
    # end_item = 100  # Set the number of iterations here
    # csv_filename = 'scraped_data.csv'
    # scrape_multiple_urls(base_url, start_item, end_item, csv_filename)

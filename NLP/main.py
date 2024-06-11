from nlp_module import processArticles, scrape_news
import spacy
import sys


def wrapper(url):
    print('initialising transformer model')
    nlp_trf = spacy.load('en_core_web_trf')
    print('scrapping')
    scraped_data = scrape_news(url)
    print('processing article')
    processed_data = processArticles(scraped_data, nlp_trf)
    processed_data.to_csv('output.csv', sep=';', index=None)
    print('output.csv')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python main.py <url>')
        exit()
    url = sys.argv[1]  # "https://www.unb.com.bd/category/Bangladesh/3-dead-as-truck-hits-autorickshaw-in-gazipurs-kaliakair/131193"
    wrapper(url)
    #print("url: {}".format(url))

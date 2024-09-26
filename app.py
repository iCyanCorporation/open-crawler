import os
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from pathlib import Path
from markdownify import markdownify as md
import chardet  # For detecting encoding when necessary
from publicsuffix2 import get_sld
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError

# Function to fetch and parse robots.txt


def parse_robots_txt(url):
    # Create robots.txt URL from base URL
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = urljoin(base_url, '/robots.txt')

    # Fetch the content of robots.txt
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        # print(f"Error reading robots.txt: {robots_url} - {e}")
        pass

    return rp

# Function to extract the root domain using the Public Suffix List


def get_root_domain(url):
    parsed_url = urlparse(url)
    # Get the registrable domain (e.g., example.com, example.co.jp)
    root_domain = get_sld(parsed_url.netloc)
    return root_domain

# Function to safely generate a filename


def safe_filename(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.hostname if parsed_url.hostname else parsed_url.netloc.split(':')[
        0]
    path = parsed_url.path
    file_name = f"{netloc}{path}"

    # Replace all characters that are not allowed in filenames
    sign_list = ['/', '?', '*', '|', '<', '>', '"']
    for sign in sign_list:
        file_name = file_name.replace(sign, '_')

    # If the filename does not end with .txt, append .txt
    if not file_name.endswith('.txt'):
        file_name += '.txt'
    return file_name


# Definition of Scrapy crawler spider
class DomainSpider(scrapy.Spider):
    name = 'domain_spider'

    def __init__(self, start_urls, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.init_dir()

        self.start_urls = start_urls
        self.visited_urls = set()
        self.count = 0

        # Parse robots.txt for each URL and create a dictionary to manage allowed paths
        self.allowed_paths = {}
        for url in start_urls:
            rp = parse_robots_txt(url)
            base_url = get_root_domain(url)  # Use root domain for storage
            self.allowed_paths[base_url] = rp

    # Directory initialization function
    def init_dir(self):
        # Read top-level domains from the table
        tld_csv_path = 'tables/top_level_domains.csv'
        if not os.path.exists(tld_csv_path):
            raise FileNotFoundError(f"File not found: {tld_csv_path}")

        tld_df = pd.read_csv(tld_csv_path, header=None)
        tld_list = tld_df[0].tolist()

        # Create folders for each top-level domain under the domains folder
        for tld in tld_list:
            tld_path = os.path.join('domains', tld)
            self.create_dir(tld_path)

    def format_link(self, link):
        # Remove port number
        parsed_url = urlparse(link)
        netloc = parsed_url.hostname if parsed_url.hostname else parsed_url.netloc.split(
            ':')[0]  # Use hostname to avoid issues
        path = parsed_url.path
        return f"{parsed_url.scheme}://{netloc}{path}"

    def parse(self, response):
        self.count += 1
        print(f"count: {self.count}", end="\r")

        # Parse the URL and extract the root domain
        root_domain = get_root_domain(response.url)
        tld = root_domain.split('.')[-1]

        # Determine the save directory and filename
        filename = safe_filename(response.url)
        # Use root domain here
        save_dir = os.path.join('domains', tld, root_domain)
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        # Ensure response encoding is correct
        response_encoding = response.encoding
        if not response_encoding:
            # Fallback: Try to detect the encoding if it's not provided
            detected_encoding = chardet.detect(response.body)['encoding']
            response_encoding = detected_encoding or 'utf-8'

        # Convert to UTF-8 and handle errors if necessary
        try:
            html_content = response.body.decode(
                response_encoding, errors='replace')
        except Exception as e:
            # print(f"Encoding error for {response.url}: {e}")
            html_content = response.text  # Use default encoding as a fallback

        # Convert HTML to Markdown
        # markdown_content = md(html_content)

        # Save to file with UTF-8 encoding
        if os.path.exists(file_path):
            # print(f"create: {file_path}, skipping...")
            pass
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                # file.write(markdown_content)
                file.write("")

        # Check the allowed status of the current page's robots.txt
        rp = self.allowed_paths.get(root_domain)
        if not rp or not rp.can_fetch('*', response.url):
            # print(f"This URL is disallowed: {response.url}")
            return

        # Extract links from the page and add them to the visited_urls array
        links = response.css('a::attr(href)').getall()
        for link in links:
            if link.startswith('http') and link not in self.visited_urls:
                # Check robots.txt
                if rp and rp.can_fetch('*', link):
                    # Check if the corresponding directory already exists
                    new_link = self.format_link(link)
                    # link_tld = link_root_domain.split('.')[-1]
                    # link_save_dir = os.path.join('domains', link_tld, link_root_domain)
                    # if os.path.exists(link_save_dir):
                    #     print(f"Directory already exists for {link}, skipping...")
                    #     continue

                    # If not visited and directory does not exist, process the link
                    self.visited_urls.add(new_link)
                    yield scrapy.Request(new_link, callback=self.parse, errback=self.errback_handler)

    def errback_handler(self, failure):
        """"""
        # エラー時の処理
        # self.logger.error(repr(failure))

        # if failure.check(DNSLookupError):
        #     self.logger.error(f"DNSLookupError on {failure.request.url}")
        #     # DNSLookupError発生時に特定の処理を行う（例: ログに記録し、スキップ）
        # elif failure.check(TimeoutError, TCPTimedOutError):
        #     self.logger.error(f"TimeoutError on {failure.request.url}")

    def create_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            # print(f"Directory created: {path}")

# Main function


def main():
    # Initialize directories
    print("Initializing directories...")

    # Set start URLs (e.g., 5 major sites)
    start_urls = [
        'https://www.wikipedia.org',
        'https://www.xploredomains.com/'
        # 'https://www.amazon.com',
        # 'https://www.youtube.com',
        # 'https://www.ebay.com',
        # 'https://www.twitter.com'
    ]

    # Set up and start the Scrapy process
    process = CrawlerProcess(settings={
        # Set log level (change to 'DEBUG' for debug information)
        'LOG_LEVEL': 'ERROR',
        'CONCURRENT_REQUESTS': 100,  # 最大スレッドで並行処理
        'DOWNLOAD_DELAY': 0.25,
        'RETRY_TIMES': 2, 
        'DNS_TIMEOUT': 3,   
        'DOWNLOAD_TIMEOUT': 5, 
    })

    # Run the crawler spider
    print("Running the crawler...")
    process.crawl(DomainSpider, start_urls=start_urls)
    process.start()  # Blocking execution, wait until all crawlers finish


# Entry point of the script
if __name__ == '__main__':
    main()

import os
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from pathlib import Path
from markdownify import markdownify as md
import chardet  # For detecting encoding when necessary

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
        print(f"Error reading robots.txt: {robots_url} - {e}")
    
    return rp

# Function to extract the root domain
def get_root_domain(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    # Return the last two parts of the domain, like google.com or apple.com
    if len(domain_parts) > 2:
        return ".".join(domain_parts[-2:])
    return parsed_url.netloc

# Function to safely generate a filename
def safe_filename(url):
    parsed_url = urlparse(url)
    # Convert URL path to filename and replace invalid characters
    file_name = parsed_url.netloc + parsed_url.path
    file_name = file_name.strip('/').replace('/', '_').replace(':', '_')
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

    def parse(self, response):
        # Parse the URL and extract the root domain
        root_domain = get_root_domain(response.url)
        tld = root_domain.split('.')[-1]
        
        # Determine the save directory and filename
        filename = safe_filename(response.url)
        save_dir = os.path.join('domains', tld, root_domain)  # Use root domain here
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
            html_content = response.body.decode(response_encoding, errors='replace')
        except Exception as e:
            print(f"Encoding error for {response.url}: {e}")
            html_content = response.text  # Use default encoding as a fallback

        # Convert HTML to Markdown
        # markdown_content = md(html_content)

        # Save to file with UTF-8 encoding
        if os.path.exists(file_path):
            print(f"create: {file_path}, skipping...")
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                # file.write(markdown_content)
                file.write("")
                print(f"Saved: {file_path}")

        # Check the allowed status of the current page's robots.txt
        rp = self.allowed_paths.get(root_domain)
        if not rp or not rp.can_fetch('*', response.url):
            print(f"This URL is disallowed: {response.url}")
            return

        # Extract links from the page and add them to the visited_urls array
        links = response.css('a::attr(href)').getall()
        for link in links:
            if link.startswith('http') and link not in self.visited_urls:
                # Check robots.txt
                if rp and rp.can_fetch('*', link):
                    # Check if the corresponding directory already exists
                    link_root_domain = get_root_domain(link)
                    link_tld = link_root_domain.split('.')[-1]
                    link_save_dir = os.path.join('domains', link_tld, link_root_domain)
                    # if os.path.exists(link_save_dir):
                    #     print(f"Directory already exists for {link}, skipping...")
                    #     continue

                    # If not visited and directory does not exist, process the link
                    self.visited_urls.add(link)
                    yield scrapy.Request(link, callback=self.parse)

    def create_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory created: {path}")

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
        'LOG_LEVEL': 'INFO',  # Set log level (change to 'DEBUG' for debug information)
    })
    
    # Run the crawler spider
    print("Running the crawler...")
    process.crawl(DomainSpider, start_urls=start_urls)
    process.start()  # Blocking execution, wait until all crawlers finish

# Entry point of the script
if __name__ == '__main__':
    main()

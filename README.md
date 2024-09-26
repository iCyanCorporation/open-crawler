# Web Crawler Project

This project is a web crawler built using Scrapy that can crawl websites and save their content in Markdown format. It respects the `robots.txt` rules and saves content in UTF-8 encoding to prevent garbled characters when dealing with various languages.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project is designed to crawl websites and save the content in a structured way. It focuses on:
- Respecting `robots.txt` to avoid crawling disallowed pages.
- Converting HTML content into Markdown format.
- Saving all content in UTF-8 encoding to handle multiple languages.

## Features

- **Domain-based Directory Structure**: Organizes the crawled content into directories based on root domains.
- **Markdown Conversion**: Converts HTML content into Markdown for easier readability.
- **UTF-8 Encoding**: Saves all content in UTF-8 encoding to prevent character encoding issues.
- **Robots.txt Compliance**: Respects the crawling rules defined in `robots.txt`.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/your-repository.git
    ```
2. **Navigate to the project directory:**
    ```bash
    cd your-repository
    ```
3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Prepare the `tables/top_level_domains.csv` file:**
    - Add the top-level domains you want to crawl in the file, one per line. For example:
    ```
    com
    net
    org
    ```

2. **Run the crawler:**
    ```bash
    python app.py
    ```

3. **Crawled data:**
    - The crawled data will be saved in the `domains` directory, organized by root domains.

## Project Structure
```
your-repository/ 
│ ├── app.py # Main script to run the crawler 
├── requirements.txt # Dependencies required for the project 
├── tables/ 
│ 
└── top_level_domains.csv # List of top-level domains to create directories for 
└── domains/ # Directory where crawled data will be stored
```

## Configuration

- **Start URLs**: You can modify the `start_urls` list in the `app.py` file to specify the initial URLs to start crawling from.
- **robots.txt Handling**: The crawler automatically checks and respects the `robots.txt` rules of each website.

## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

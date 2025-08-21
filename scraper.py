import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json

print("Fidelity Learning Center Scraper Started!")


def scrape_fidelity_articles(base_url="https://www.fidelity.com/learning-center"):
    """
    Scrapes article titles and contents from Fidelity Learning Center.
    
    Args:
        base_url: The base URL of the Fidelity Learning Center
        
    Returns:
        A list of dictionaries containing article titles and contents
    """
    try:
        print(f"Fetching Fidelity Learning Center: {base_url}")
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Look for article links in the main content area
        article_links = []
        
        # Find article tiles - these contain links to individual articles
        link_selectors = [
            'a[href*="/learning-center/"]',  # Links containing learning-center
            '.tile a',  # Links within tile elements
            '.article-tile a',  # Article tile links
            '.content-tile a',  # Content tile links
            'article a',  # Links within article elements
            '.ellipsis a',  # Links in ellipsis containers
            '.content-item a',  # Content item links
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and href not in article_links:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = 'https://www.fidelity.com' + href
                    elif not href.startswith('http'):
                        href = base_url.rstrip('/') + '/' + href.lstrip('/')
                    
                    # Only include learning center articles
                    if '/learning-center/' in href and href not in article_links:
                        article_links.append(href)
        
        print(f"Found {len(article_links)} potential article links")
        
        # Limit to first 20 articles to avoid overwhelming the server
        article_links = article_links[:20]
        
        for i, article_url in enumerate(article_links, 1):
            try:
                print(f"Processing article {i}/{len(article_links)}: {article_url}")
                
                article_response = requests.get(article_url, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                
                # Extract title - try multiple selectors
                title = None
                title_selectors = [
                    'h1',
                    '.article-title',
                    '.page-title', 
                    '.heading',
                    'title'
                ]
                
                for selector in title_selectors:
                    title_element = article_soup.select_one(selector)
                    if title_element:
                        title = title_element.get_text(strip=True)
                        if title and len(title) > 5:  # Ensure we get a meaningful title
                            break
                
                if not title:
                    print(f"  Warning: Could not extract title from {article_url}")
                    continue
                
                # Extract content - try multiple selectors
                content = None
                content_selectors = [
                    '.article-body',
                    '.content-body', 
                    '.article-content',
                    '.main-content',
                    '.page-content',
                    'main article',
                    'main',
                    '.learn-content',
                    '.rich-text',
                    'article'
                ]
                
                for selector in content_selectors:
                    content_element = article_soup.select_one(selector)
                    if content_element:
                        # Remove navigation, ads, and other non-content elements
                        for unwanted in content_element.select('nav, .nav, .advertisement, .sidebar, .footer, script, style, .promo, .related, .breadcrumb'):
                            unwanted.decompose()
                        
                        content = content_element.get_text(strip=True)
                        if content and len(content) > 200:  # Ensure we get meaningful content
                            break
                
                # If no substantial content found, try to get paragraphs
                if not content or len(content) < 200:
                    paragraphs = article_soup.find_all('p')
                    if paragraphs:
                        content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                
                # Final fallback - get text from body but filter out navigation
                if not content or len(content) < 100:
                    body = article_soup.find('body')
                    if body:
                        for unwanted in body.select('nav, .nav, header, footer, .advertisement, .sidebar, script, style'):
                            unwanted.decompose()
                        content = body.get_text(strip=True)
                
                if not content:
                    print(f"  Warning: Could not extract content from {article_url}")
                    continue
                
                # Clean up content
                content = re.sub(r'\s+', ' ', content)  # Remove extra whitespace
                content = re.sub(r'\n+', '\n', content)  # Normalize line breaks
                
                articles.append({
                    "title": title,
                    "content": content,
                    "url": article_url
                })
                
                print(f"  Successfully extracted: {title[:50]}...")
                
                # Be respectful - wait between requests
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"  Error fetching {article_url}: {e}")
                continue
            except Exception as e:
                print(f"  Error processing {article_url}: {e}")
                continue
        
        print(f"Successfully extracted {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"Error scraping Fidelity Learning Center: {e}")
        return []


def scrape_specific_fidelity_topics(topics=None):
    """
    Scrapes specific topic areas from Fidelity Learning Center.
    
    Args:
        topics: List of topic URLs to scrape. If None, uses default financial topics.
        
    Returns:
        List of dictionaries containing article titles and contents
    """
    if topics is None:
        # Default topics that are likely to have substantial content
        topics = [
            "https://www.fidelity.com/learning-center/investment/getting-started-investing",
            "https://www.fidelity.com/learning-center/investment/the-basics",
            "https://www.fidelity.com/learning-center/investment/cryptocurrency",
            "https://www.fidelity.com/learning-center/investment/stock-market-basics",
            "https://www.fidelity.com/learning-center/investment/etfs",
            "https://www.fidelity.com/learning-center/investment/mutual-funds", 
            "https://www.fidelity.com/learning-center/personal-finance/retirement/retirement-planning",
            "https://www.fidelity.com/learning-center/personal-finance/retirement/401k-basics",
            "https://www.fidelity.com/learning-center/personal-finance/retirement/ira-basics",
            "https://www.fidelity.com/learning-center/personal-finance/taxes",
        ]
    
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for i, topic_url in enumerate(topics, 1):
        try:
            print(f"Processing topic {i}/{len(topics)}: {topic_url}")
            
            response = requests.get(topic_url, headers=headers)
            if response.status_code == 404:
                print(f"  Topic not found (404): {topic_url}")
                continue
                
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            for selector in ['h1', '.page-title', '.article-title', 'title']:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 5:
                        break
            
            if not title:
                title = f"Financial Topic {i}"
                
            # Extract content with multiple strategies
            content = None
            
            # Strategy 1: Look for main content areas
            for selector in ['.main-content', '.article-body', '.content-body', 'main']:
                content_element = soup.select_one(selector)
                if content_element:
                    for unwanted in content_element.select('nav, .nav, .sidebar, .advertisement, script, style'):
                        unwanted.decompose()
                    content = content_element.get_text(strip=True)
                    if content and len(content) > 300:
                        break
            
            # Strategy 2: If no main content, collect all paragraphs
            if not content or len(content) < 300:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
            
            if content and len(content) > 100:
                # Clean up content
                content = re.sub(r'\s+', ' ', content)
                content = re.sub(r'\n+', '\n', content)
                
                articles.append({
                    "title": title,
                    "content": content,
                    "url": topic_url
                })
                print(f"  Successfully extracted: {title[:50]}...")
            else:
                print(f"  Warning: Insufficient content found for {topic_url}")
            
            time.sleep(2)  # Be respectful
            
        except Exception as e:
            print(f"  Error processing {topic_url}: {e}")
            continue
    
    return articles


def save_articles_to_json(articles, filename="fidelity_articles.json"):
    """
    Saves extracted articles to a JSON file.
    
    Args:
        articles: List of dictionaries containing article data
        filename: Name of the output file
    """
    if articles:
        try:
            if not os.path.exists("output"):
                os.makedirs("output")
            
            with open(os.path.join("output", filename), 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(articles)} articles to {filename}")
        except Exception as e:
            print(f"Error saving articles to JSON: {e}")
    else:
        print("No articles to save.")


if __name__ == "__main__":
    print("Fidelity Learning Center Scraper")
    print("Choose scraping method:")
    print("1. Browse-based scraper (discover articles from main page)")
    print("2. Targeted topics scraper (specific financial topics)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Scrape Fidelity Learning Center (browse approach)
        articles = scrape_fidelity_articles()
        if articles:
            save_articles_to_json(articles, "fidelity_articles.json")
        else:
            print("No articles were extracted")
    else:
        # Scrape specific Fidelity topics (targeted approach)
        articles = scrape_specific_fidelity_topics()
        if articles:
            save_articles_to_json(articles, "fidelity_specific_topics.json")
        else:
            print("No articles were extracted")
    
    print("Scraping completed!")
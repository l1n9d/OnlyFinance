import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

def scrape_learning_center_articles():
    """
    Scrapes actual articles from Fidelity Learning Center (not Viewpoints).
    Focuses on the learning-center section specifically.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🎓 Scraping Fidelity Learning Center articles...")
    
    # Learning Center main sections
    learning_center_sections = [
        "https://www.fidelity.com/learning-center",
        "https://www.fidelity.com/learning-center/investment",
        "https://www.fidelity.com/learning-center/investment/getting-started-investing",
        "https://www.fidelity.com/learning-center/investment/the-basics",
        "https://www.fidelity.com/learning-center/investment/stock-market-basics",
        "https://www.fidelity.com/learning-center/investment/mutual-funds",
        "https://www.fidelity.com/learning-center/investment/etfs",
        "https://www.fidelity.com/learning-center/investment/bonds",
        "https://www.fidelity.com/learning-center/investment/cryptocurrency",
        "https://www.fidelity.com/learning-center/personal-finance",
        "https://www.fidelity.com/learning-center/personal-finance/retirement",
        "https://www.fidelity.com/learning-center/personal-finance/retirement/retirement-planning",
        "https://www.fidelity.com/learning-center/personal-finance/retirement/401k-basics",
        "https://www.fidelity.com/learning-center/personal-finance/retirement/ira-basics",
        "https://www.fidelity.com/learning-center/personal-finance/budgeting",
        "https://www.fidelity.com/learning-center/personal-finance/taxes",
        "https://www.fidelity.com/learning-center/personal-finance/college-planning",
        "https://www.fidelity.com/learning-center/personal-finance/home-buying",
        "https://www.fidelity.com/learning-center/trading",
        "https://www.fidelity.com/learning-center/trading/getting-started-trading",
        "https://www.fidelity.com/learning-center/trading/options",
    ]
    
    all_articles = []
    discovered_urls = set()
    
    for section_url in learning_center_sections:
        print(f"\n📚 Exploring section: {section_url}")
        
        try:
            response = requests.get(section_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract content from this page
                article_data = extract_learning_center_content(soup, section_url)
                if article_data:
                    all_articles.append(article_data)
                    print(f"  ✅ Extracted content: {article_data['title'][:60]}...")
                
                # Find links to other learning center articles
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href:
                        # Convert relative to absolute
                        if href.startswith('/'):
                            href = f"https://www.fidelity.com{href}"
                        
                        # Only include learning-center URLs (not viewpoints)
                        if '/learning-center/' in href and href not in discovered_urls:
                            # Avoid pagination and utility links
                            if not any(skip in href for skip in ['?', '#', 'page=', 'sort=', 'filter=']):
                                discovered_urls.add(href)
                                print(f"    Found: {href}")
            
            else:
                print(f"  ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(1)  # Be respectful
    
    # Now scrape the discovered learning center URLs
    print(f"\n🔍 Found {len(discovered_urls)} additional Learning Center URLs")
    
    for url in list(discovered_urls)[:20]:  # Limit to avoid too many requests
        print(f"\n📖 Scraping: {url}")
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                article_data = extract_learning_center_content(soup, url)
                if article_data:
                    all_articles.append(article_data)
                    print(f"  ✅ Extracted: {article_data['title'][:60]}...")
                else:
                    print(f"  ⚠️  No substantial content found")
            else:
                print(f"  ❌ Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(1)
    
    return all_articles

def extract_learning_center_content(soup, url):
    """
    Extracts content specifically from Learning Center pages.
    """
    
    # Get title
    title = None
    title_selectors = [
        'h1',
        '.hero-title',
        '.page-title',
        '.learn-title',
        '.content-title'
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            title = title_elem.get_text(strip=True)
            if title and len(title) > 5:
                break
    
    if not title:
        title = url.split('/')[-1].replace('-', ' ').title()
    
    # Get content - Learning Center specific selectors
    content = None
    content_selectors = [
        '.learn-content',
        '.learn-article-content', 
        '.learning-center-content',
        '.page-content .rich-text',
        'main .content',
        '.main-content',
        '.article-content',
        '.content-area',
        'main'
    ]
    
    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.select('nav, .nav, header, footer, .advertisement, .sidebar, .breadcrumb, .social-share, .related-content, script, style'):
                unwanted.decompose()
            
            content = content_elem.get_text(separator=' ', strip=True)
            if content and len(content) > 500:  # Substantial content
                break
            content = None
    
    # Fallback: Get meaningful paragraphs
    if not content:
        main_area = soup.find('main') or soup.find('body')
        if main_area:
            # Remove navigation elements
            for unwanted in main_area.select('nav, header, footer, .sidebar, .navigation, .menu, aside, script, style'):
                unwanted.decompose()
            
            paragraphs = main_area.find_all('p')
            meaningful_paragraphs = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if (len(text) > 50 and 
                    not any(nav_word in text.lower() for nav_word in ['sign in', 'menu', 'search', 'subscribe', 'contact', 'privacy', 'terms']) and
                    not text.startswith('©') and
                    len(text.split()) > 8):
                    meaningful_paragraphs.append(text)
            
            if meaningful_paragraphs:
                content = ' '.join(meaningful_paragraphs[:15])  # Limit content
    
    # Clean and validate content
    if content:
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[\r\n]+', ' ', content)
        content = content.strip()
        
        if len(content) < 300:
            return None
            
        return {
            "title": title,
            "content": content[:5000],  # Limit length
            "url": url
        }
    
    return None

def save_learning_center_articles(articles):
    """Save learning center articles to JSON file"""
    if not articles:
        print("No articles to save!")
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", "fidelity_learning_center_articles.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(articles)} Learning Center articles to {filepath}")
        
        print("\nLearning Center Articles Summary:")
        for i, article in enumerate(articles, 1):
            print(f"  {i:2d}. {article['title'][:70]}...")
            print(f"      Content: {len(article['content'])} chars")
            print(f"      URL: {article['url']}")
            print()
            
    except Exception as e:
        print(f"Error saving articles: {e}")

if __name__ == "__main__":
    print("Starting Fidelity Learning Center scraper...")
    print("This will focus on learning-center URLs, not viewpoints.")
    
    articles = scrape_learning_center_articles()
    
    if articles:
        save_learning_center_articles(articles)
        print(f"\n🎉 Successfully scraped {len(articles)} Learning Center articles!")
        print("These are actual educational content from the Learning Center section.")
    else:
        print("❌ No articles were successfully scraped.")
    
    print("Learning Center scraping completed!")

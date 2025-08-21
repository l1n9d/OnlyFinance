import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from urllib.parse import urljoin, urlparse

def explore_learning_center_structure():
    """
    Properly explore the 5 main categories in Fidelity Learning Center:
    1. Financial Essentials
    2. Life Events  
    3. Investing and Trading
    4. Investment Products
    5. Advanced Trading
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🏗️ Exploring Full Fidelity Learning Center Structure...")
    
    base_url = "https://www.fidelity.com/learning-center"
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("✅ Successfully loaded main Learning Center page")
        
        # Find all links on the main page
        all_links = soup.find_all('a', href=True)
        learning_center_links = set()
        
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href:
                # Convert relative to absolute URLs
                if href.startswith('/'):
                    href = f"https://www.fidelity.com{href}"
                
                # Only include learning-center URLs
                if '/learning-center/' in href:
                    # Avoid utility pages
                    if not any(skip in href for skip in ['?', '#', 'page=', 'sort=', 'filter=', 'favorites', 'overview']):
                        learning_center_links.add((href, text))
        
        print(f"🔍 Found {len(learning_center_links)} Learning Center links")
        
        # Categorize the links
        categories = {
            'Financial Essentials': [],
            'Life Events': [],
            'Investing and Trading': [], 
            'Investment Products': [],
            'Advanced Trading': [],
            'Other': []
        }
        
        for url, text in learning_center_links:
            if any(keyword in url.lower() for keyword in ['personal-finance', 'budgeting', 'saving', 'debt', 'taxes', 'health-care', 'estate']):
                categories['Financial Essentials'].append((url, text))
            elif any(keyword in url.lower() for keyword in ['life-events', 'college', 'house', 'marriage', 'divorce', 'aging', 'career', 'parenting']):
                categories['Life Events'].append((url, text))
            elif any(keyword in url.lower() for keyword in ['trading-investing', 'investing', 'trading', 'technical-analysis', 'fundamental']):
                categories['Investing and Trading'].append((url, text))
            elif any(keyword in url.lower() for keyword in ['investment-products', 'stocks', 'bonds', 'etf', 'mutual-funds', 'options', 'annuities']):
                categories['Investment Products'].append((url, text))
            elif any(keyword in url.lower() for keyword in ['active-trader', 'margin', 'strategy-guide', 'technical-indicator']):
                categories['Advanced Trading'].append((url, text))
            else:
                categories['Other'].append((url, text))
        
        # Print category breakdown
        print("\n📊 Learning Center Categories:")
        for category, links in categories.items():
            if links:
                print(f"\n🏷️  {category}: {len(links)} articles")
                for url, text in links[:5]:  # Show first 5
                    print(f"    • {text[:50]}... -> {url}")
                if len(links) > 5:
                    print(f"    ... and {len(links) - 5} more")
        
        return categories
        
    except Exception as e:
        print(f"❌ Error exploring structure: {e}")
        return {}

def get_article_content(url, headers):
    """
    Extract actual article content from a Learning Center URL.
    """
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title
        title = None
        title_selectors = ['h1', '.hero-title', '.page-title', '.article-title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5:
                    break
        
        if not title:
            title = url.split('/')[-1].replace('-', ' ').title()
        
        # Get content
        content = None
        content_selectors = [
            '.rich-text',
            '[data-module="RichText"]',
            '.article-body',
            '.learn-content',
            '.content-area',
            'main .content',
            '.page-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for unwanted in content_elem.select('nav, .nav, header, footer, .sidebar, .breadcrumb, script, style, .social-share'):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator=' ', strip=True)
                if content and len(content) > 500:
                    break
                content = None
        
        # Fallback: extract meaningful paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            meaningful_paragraphs = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if (len(text) > 50 and 
                    not any(skip in text.lower() for skip in ['sign in', 'menu', 'search', 'subscribe', 'copyright', '©']) and
                    len(text.split()) > 8):
                    meaningful_paragraphs.append(text)
            
            if meaningful_paragraphs:
                content = ' '.join(meaningful_paragraphs[:10])
        
        # Clean and validate
        if content:
            content = re.sub(r'\s+', ' ', content).strip()
            if len(content) > 300:
                return {
                    "title": title,
                    "content": content[:4000],  # Limit content length
                    "url": url
                }
        
        return None
        
    except Exception as e:
        print(f"    ❌ Error scraping {url}: {e}")
        return None

def scrape_all_learning_center_articles():
    """
    Scrape ALL articles from all 5 main categories in Learning Center.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🎓 Starting COMPREHENSIVE Learning Center scraping...")
    
    # First, explore the structure
    categories = explore_learning_center_structure()
    
    if not categories:
        print("❌ Failed to explore structure")
        return []
    
    all_articles = []
    total_urls = sum(len(links) for links in categories.values())
    current_count = 0
    
    print(f"\n🚀 Starting to scrape {total_urls} total articles...")
    
    for category_name, links in categories.items():
        if not links:
            continue
            
        print(f"\n📚 Scraping {category_name} ({len(links)} articles)...")
        
        category_success = 0
        for url, text_preview in links:
            current_count += 1
            print(f"  [{current_count}/{total_urls}] {text_preview[:50]}...")
            
            article_data = get_article_content(url, headers)
            if article_data:
                article_data['category'] = category_name
                all_articles.append(article_data)
                category_success += 1
                print(f"    ✅ Success: {len(article_data['content'])} chars")
            else:
                print(f"    ❌ Failed to extract content")
            
            # Be respectful with timing
            time.sleep(0.5)
        
        print(f"  📊 {category_name}: {category_success}/{len(links)} successful")
    
    print(f"\n🎉 TOTAL: Successfully scraped {len(all_articles)} articles!")
    return all_articles

def save_comprehensive_articles(articles):
    """Save all Learning Center articles with category information."""
    if not articles:
        print("No articles to save!")
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", "fidelity_full_learning_center.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(articles)} articles to {filepath}")
        
        # Show breakdown by category
        categories = {}
        for article in articles:
            category = article.get('category', 'Unknown')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print("\n📊 Articles by Category:")
        for category, count in categories.items():
            print(f"  {category}: {count} articles")
        
        print(f"\n📋 Sample articles:")
        for i, article in enumerate(articles[:10], 1):
            print(f"  {i:2d}. [{article.get('category', 'Unknown')}] {article['title'][:60]}...")
        
        if len(articles) > 10:
            print(f"       ... and {len(articles) - 10} more articles")
            
    except Exception as e:
        print(f"Error saving articles: {e}")

if __name__ == "__main__":
    print("Starting COMPREHENSIVE Fidelity Learning Center scraper...")
    print("This will properly explore all 5 main categories and scrape ALL articles.")
    
    articles = scrape_all_learning_center_articles()
    
    if articles:
        save_comprehensive_articles(articles)
        print(f"\n🎊 SUCCESS! Scraped {len(articles)} comprehensive Learning Center articles!")
        print("Now you'll have articles covering:")
        print("  • Financial Essentials (budgeting, saving, taxes, etc.)")
        print("  • Life Events (college, home buying, marriage, etc.)")  
        print("  • Investing and Trading (basics to advanced)")
        print("  • Investment Products (stocks, bonds, ETFs, etc.)")
        print("  • Advanced Trading (technical analysis, options, etc.)")
    else:
        print("❌ No articles were successfully scraped.")
    
    print("Comprehensive scraping completed!")

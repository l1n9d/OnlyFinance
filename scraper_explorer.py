import requests
from bs4 import BeautifulSoup
import re
import time
import json

def explore_fidelity_learning_center():
    """
    Explores the actual structure of Fidelity Learning Center to find real articles.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🔍 Exploring Fidelity Learning Center structure...")
    
    # Main learning center page
    base_url = "https://www.fidelity.com/learning-center"
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Successfully loaded: {base_url}")
        
        # Find actual article links
        article_links = set()
        
        # Look for various link patterns
        link_selectors = [
            'a[href*="/viewpoints/"]',
            'a[href*="/learning-center/"]',
            'a[href*="/insights/"]',
            '.content-tile a',
            '.article-tile a',
            '.tile a',
            'article a'
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative to absolute URLs
                    if href.startswith('/'):
                        href = f"https://www.fidelity.com{href}"
                    
                    # Filter for actual article URLs
                    if ('viewpoints' in href or 'learning-center' in href) and href not in article_links:
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:
                            article_links.add(href)
                            print(f"  Found: {title[:60]}... -> {href}")
        
        print(f"\n📊 Found {len(article_links)} unique article URLs")
        
        # Test a few URLs to see what content we can actually get
        print("\n🧪 Testing sample URLs for content...")
        sample_urls = list(article_links)[:5]
        
        for i, url in enumerate(sample_urls, 1):
            print(f"\n{i}. Testing: {url}")
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Get title
                    title_elem = soup.find('h1') or soup.find('title')
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    
                    # Try to find main content
                    content_selectors = [
                        '.rich-text',
                        '[data-module="RichText"]',
                        '.article-body',
                        'main article',
                        '.content-area'
                    ]
                    
                    content_found = False
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            content = content_elem.get_text(strip=True)
                            if len(content) > 500:
                                print(f"   ✅ Title: {title}")
                                print(f"   ✅ Content: {len(content)} characters (Good!)")
                                print(f"   📄 Preview: {content[:200]}...")
                                content_found = True
                                break
                    
                    if not content_found:
                        print(f"   ⚠️  Title: {title}")
                        print(f"   ❌ Content: Limited content found")
                        
                else:
                    print(f"   ❌ Status: {response.status_code}")
                    
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return list(article_links)
        
    except Exception as e:
        print(f"❌ Error exploring learning center: {e}")
        return []

def find_working_articles():
    """
    Find articles that actually have substantial content.
    """
    
    # These are URLs we know work based on our previous success
    known_working_urls = [
        "https://www.fidelity.com/viewpoints/investing-ideas/guide-to-diversification",
        "https://www.fidelity.com/viewpoints/retirement/how-much-do-i-need-to-retire",
    ]
    
    # Common Fidelity Viewpoints patterns that are more likely to exist
    potential_urls = [
        # Investment topics
        "https://www.fidelity.com/viewpoints/investing-ideas/investment-basics",
        "https://www.fidelity.com/viewpoints/investing-ideas/stock-basics",
        "https://www.fidelity.com/viewpoints/investing-ideas/bond-investing",
        "https://www.fidelity.com/viewpoints/investing-ideas/mutual-fund-basics",
        "https://www.fidelity.com/viewpoints/investing-ideas/etf-basics",
        
        # Retirement
        "https://www.fidelity.com/viewpoints/retirement/retirement-savings",
        "https://www.fidelity.com/viewpoints/retirement/401k-basics",
        "https://www.fidelity.com/viewpoints/retirement/ira-basics",
        
        # Personal finance
        "https://www.fidelity.com/viewpoints/personal-finance/budgeting",
        "https://www.fidelity.com/viewpoints/personal-finance/emergency-savings",
        "https://www.fidelity.com/viewpoints/personal-finance/debt-payoff",
        
        # Life events
        "https://www.fidelity.com/viewpoints/life-events/buying-a-home",
        "https://www.fidelity.com/viewpoints/life-events/college-planning",
        "https://www.fidelity.com/viewpoints/life-events/having-a-baby",
        
        # Tax topics
        "https://www.fidelity.com/viewpoints/personal-finance/tax-strategies",
        "https://www.fidelity.com/viewpoints/personal-finance/tax-loss-harvesting",
    ]
    
    print("🔍 Testing potential article URLs...")
    
    working_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_urls = known_working_urls + potential_urls
    
    for url in all_urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for substantial content
                content_elem = soup.select_one('.rich-text, [data-module="RichText"], .article-body')
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    if len(content) > 1000:  # Substantial content
                        title_elem = soup.find('h1')
                        title = title_elem.get_text(strip=True) if title_elem else url.split('/')[-1]
                        working_urls.append(url)
                        print(f"  ✅ {title} ({len(content)} chars)")
                    else:
                        print(f"  ⚠️  {url} (limited content: {len(content)} chars)")
                else:
                    print(f"  ❌ {url} (no content found)")
            else:
                print(f"  ❌ {url} (status: {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ {url} (error: {e})")
        
        time.sleep(0.5)  # Be respectful
    
    print(f"\n📊 Found {len(working_urls)} working URLs with substantial content")
    return working_urls

if __name__ == "__main__":
    print("Starting Fidelity Learning Center exploration...")
    
    # Method 1: Explore the main page
    print("\n" + "="*60)
    print("METHOD 1: Exploring main learning center page")
    print("="*60)
    discovered_urls = explore_fidelity_learning_center()
    
    # Method 2: Test known patterns
    print("\n" + "="*60)
    print("METHOD 2: Testing common URL patterns")
    print("="*60)
    working_urls = find_working_articles()
    
    # Combine results
    all_working_urls = list(set(working_urls))
    
    print(f"\n🎉 SUMMARY:")
    print(f"📄 Discovered URLs from main page: {len(discovered_urls)}")
    print(f"✅ Working URLs with content: {len(working_urls)}")
    print(f"🎯 Total unique working URLs: {len(all_working_urls)}")
    
    if all_working_urls:
        print(f"\n📋 Working URLs:")
        for i, url in enumerate(all_working_urls, 1):
            print(f"  {i:2d}. {url}")
    
    print("\nExploration completed!")

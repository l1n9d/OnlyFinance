import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json

print("Comprehensive Fidelity Learning Center Scraper Started!")

def scrape_fidelity_article_content(url, headers):
    """
    Scrapes content from a specific Fidelity article URL.
    """
    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title - try multiple selectors
        title = None
        title_selectors = [
            'h1',
            '.page-title',
            '.article-title', 
            '.hero-title',
            'title',
            '.content-title'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                if title and len(title) > 5 and "Fidelity" not in title[:20]:
                    break
                title = None
        
        # If no good title found, extract from URL
        if not title:
            title = url.split('/')[-1].replace('-', ' ').title()
        
        # Get content - try multiple strategies for Fidelity pages
        content = None
        
        # Strategy 1: Look for main article content
        main_content_selectors = [
            'main .rich-text',
            '[data-module="RichText"]',
            '.viewpoints-article-body',
            '.article-body .rich-text',
            '.learn-article-content',
            '.page-content .rich-text',
            'main article',
            '.content-area .rich-text'
        ]
        
        for selector in main_content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove unwanted elements
                for unwanted in content_element.select('nav, .nav, .advertisement, .sidebar, .footer, script, style, .social-share, .related-content, .breadcrumb, .navigation'):
                    unwanted.decompose()
                
                content = content_element.get_text(separator=' ', strip=True)
                if content and len(content) > 300:
                    break
                content = None
        
        # Strategy 2: Look for specific Fidelity content structures
        if not content:
            fidelity_selectors = [
                '.pvd-container .rich-text',
                '.learn-content-body',
                '.article-content-body',
                '.main-content-area',
                '[class*="content"] p',
                '.page-wrapper main'
            ]
            
            for selector in fidelity_selectors:
                elements = soup.select(selector)
                if elements:
                    texts = []
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 50:
                            texts.append(text)
                    
                    if texts:
                        content = ' '.join(texts)
                        if len(content) > 300:
                            break
                    content = None
        
        # Strategy 3: Extract from paragraphs in main content area
        if not content:
            main_area = soup.find('main') or soup.find('body')
            if main_area:
                # Remove navigation and sidebar content first
                for unwanted in main_area.select('nav, header, footer, .sidebar, .navigation, .menu, aside, .related, .promo, script, style'):
                    unwanted.decompose()
                
                paragraphs = main_area.find_all('p')
                meaningful_paragraphs = []
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if (len(text) > 30 and 
                        not any(nav_word in text.lower() for nav_word in ['sign in', 'menu', 'search', 'subscribe', 'follow us', 'contact']) and
                        not text.startswith('©') and
                        len(text.split()) > 5):
                        meaningful_paragraphs.append(text)
                
                if meaningful_paragraphs:
                    content = ' '.join(meaningful_paragraphs[:20])
        
        # Clean up content
        if content:
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'[\r\n]+', ' ', content)
            content = re.sub(r'(Skip to main content|Sign In|Register|Help|Contact Us|Privacy|Terms)', '', content, flags=re.IGNORECASE)
            content = content.strip()
            
            if len(content) < 200:
                print(f"    Warning: Content too short ({len(content)} chars)")
                return None
            
            print(f"    ✓ Extracted {len(content)} characters of content")
            return {
                "title": title,
                "content": content[:5000],
                "url": url
            }
        else:
            print(f"    ✗ No content found")
            return None
            
    except Exception as e:
        print(f"    Error processing {url}: {e}")
        return None

def scrape_comprehensive_fidelity_topics():
    """
    Scrapes a comprehensive set of financial topics from Fidelity.
    """
    
    # Comprehensive list covering major financial topics
    article_urls = [
        # Investment Basics
        "https://www.fidelity.com/viewpoints/investing-ideas/how-to-invest-your-first-1000-dollars",
        "https://www.fidelity.com/viewpoints/investing-ideas/guide-to-diversification",
        "https://www.fidelity.com/viewpoints/investing-ideas/what-to-do-with-10000-dollars",
        "https://www.fidelity.com/viewpoints/investing-ideas/asset-allocation-age",
        "https://www.fidelity.com/viewpoints/investing-ideas/stock-market-basics",
        "https://www.fidelity.com/viewpoints/investing-ideas/what-are-etfs",
        "https://www.fidelity.com/viewpoints/investing-ideas/mutual-funds-vs-etfs",
        "https://www.fidelity.com/viewpoints/investing-ideas/index-funds-vs-active-funds",
        
        # Retirement Planning
        "https://www.fidelity.com/viewpoints/retirement/how-much-do-i-need-to-retire",
        "https://www.fidelity.com/viewpoints/retirement/401k-contribution-limits",
        "https://www.fidelity.com/viewpoints/retirement/roth-ira-vs-traditional-ira",
        "https://www.fidelity.com/viewpoints/retirement/retirement-planning-checklist",
        "https://www.fidelity.com/viewpoints/retirement/ira-contribution-limits",
        "https://www.fidelity.com/viewpoints/retirement/social-security-benefits",
        
        # Personal Finance & Budgeting
        "https://www.fidelity.com/viewpoints/personal-finance/emergency-fund",
        "https://www.fidelity.com/viewpoints/personal-finance/budgeting-tips",
        "https://www.fidelity.com/viewpoints/personal-finance/pay-off-debt-or-invest",
        "https://www.fidelity.com/viewpoints/personal-finance/how-to-save-money",
        "https://www.fidelity.com/viewpoints/personal-finance/debt-management",
        
        # Home Buying & Real Estate
        "https://www.fidelity.com/viewpoints/personal-finance/saving-for-house",
        "https://www.fidelity.com/viewpoints/personal-finance/first-time-home-buyer",
        "https://www.fidelity.com/viewpoints/personal-finance/mortgage-basics",
        "https://www.fidelity.com/viewpoints/personal-finance/refinancing-mortgage",
        
        # College & Education Planning
        "https://www.fidelity.com/viewpoints/personal-finance/college-planning",
        "https://www.fidelity.com/viewpoints/personal-finance/529-plan-basics",
        "https://www.fidelity.com/viewpoints/personal-finance/paying-for-college",
        "https://www.fidelity.com/viewpoints/personal-finance/student-loans",
        "https://www.fidelity.com/viewpoints/personal-finance/education-savings-accounts",
        
        # Taxes
        "https://www.fidelity.com/viewpoints/personal-finance/taxes",
        "https://www.fidelity.com/viewpoints/personal-finance/tax-planning",
        "https://www.fidelity.com/viewpoints/personal-finance/tax-deductions",
        "https://www.fidelity.com/viewpoints/personal-finance/tax-refund",
        
        # Insurance & Protection
        "https://www.fidelity.com/viewpoints/personal-finance/life-insurance",
        "https://www.fidelity.com/viewpoints/personal-finance/health-insurance",
        "https://www.fidelity.com/viewpoints/personal-finance/disability-insurance",
        
        # Career & Income
        "https://www.fidelity.com/viewpoints/personal-finance/salary-negotiation",
        "https://www.fidelity.com/viewpoints/personal-finance/side-hustles",
        "https://www.fidelity.com/viewpoints/personal-finance/career-development",
        
        # Advanced Topics
        "https://www.fidelity.com/viewpoints/personal-finance/estate-planning",
        "https://www.fidelity.com/viewpoints/investing-ideas/cryptocurrency",
        "https://www.fidelity.com/viewpoints/investing-ideas/bond-basics",
        "https://www.fidelity.com/viewpoints/investing-ideas/dollar-cost-averaging"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    articles = []
    successful = 0
    
    print(f"Attempting to scrape {len(article_urls)} comprehensive articles...")
    
    for url in article_urls:
        article_data = scrape_fidelity_article_content(url, headers)
        if article_data:
            articles.append(article_data)
            successful += 1
            print(f"  ✓ Success: {article_data['title'][:60]}...")
        else:
            print(f"  ✗ Failed: {url}")
        
        # Be respectful - wait between requests
        time.sleep(1)
    
    print(f"\nScraping completed!")
    print(f"Successfully extracted {successful}/{len(article_urls)} articles")
    
    return articles

def save_articles_to_json(articles, filename="fidelity_comprehensive_articles.json"):
    """Save articles to JSON file"""
    if not articles:
        print("No articles to save!")
        return
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(articles)} articles to {filepath}")
        
        # Show summary by category
        print("\nArticles saved by category:")
        categories = {
            'Investment': ['invest', 'stock', 'etf', 'fund', 'portfolio', 'diversif'],
            'Retirement': ['retire', '401k', 'ira', 'social security'],
            'Personal Finance': ['budget', 'emergency', 'debt', 'save'],
            'Home/Real Estate': ['house', 'home', 'mortgage', 'refinanc'],
            'Education': ['college', '529', 'student', 'education'],
            'Taxes': ['tax', 'deduction', 'refund'],
            'Insurance': ['insurance', 'life', 'health', 'disability'],
            'Career': ['salary', 'career', 'side hustle'],
            'Advanced': ['estate', 'crypto', 'bond', 'dollar cost']
        }
        
        for category, keywords in categories.items():
            count = sum(1 for article in articles if any(keyword in article['title'].lower() for keyword in keywords))
            if count > 0:
                print(f"  {category}: {count} articles")
                
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting comprehensive Fidelity Learning Center scraper...")
    
    articles = scrape_comprehensive_fidelity_topics()
    
    if articles:
        save_articles_to_json(articles)
        print(f"\n🎉 Successfully scraped {len(articles)} comprehensive articles!")
        print("This should now cover home buying, college planning, and many more topics!")
    else:
        print("❌ No articles were successfully scraped.")
    
    print("Scraping completed!")

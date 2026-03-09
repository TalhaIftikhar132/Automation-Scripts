# import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Function to detect if site is WordPress ---
def is_wordpress_site(soup):
    generator = soup.find("meta", attrs={"name": "generator"})
    if generator and "wordpress" in generator.get("content", "").lower():
        return True
    # Also check for common WordPress assets
    for link in soup.find_all("link", href=True):
        if "wp-content" in link["href"] or "wp-includes" in link["href"]:
            return True
    return False

# --- Function to get metadata from a single URL ---
def get_metadata(url, use_selenium=False):
    title, description, keywords = None, None, None
    print(f"Scraping {url}...")

    try:
        if not use_selenium:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.content, 'html.parser')
        else:
            chrome_opts = Options()
            chrome_opts.add_argument("--headless")
            chrome_opts.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_opts)
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return title, description, keywords

    try:
        # Meta title
        title = soup.title.string.strip() if soup.title else None

        # Description, keywords, and WordPress SEO plugin fields
        for meta in soup.find_all('meta'):
            name = meta.attrs.get('name', '').lower()
            prop = meta.attrs.get('property', '').lower()
            content = meta.attrs.get('content', '').strip()

            if name == 'description' or prop == 'og:description' or name == 'twitter:description':
                description = description or content
            if name == 'keywords':
                keywords = content
            if prop == 'og:title' or name == 'twitter:title':
                title = title or content

    except Exception as e:
        print(f"Error parsing metadata for {url}: {e}")

    return title, description, keywords

# --- Function to get URLs from multiple possible sitemap locations ---
def get_urls_from_sitemaps(base_domain):
    sitemap_candidates = [
        f"{base_domain}/sitemap.xml",
        f"{base_domain}/wp-sitemap.xml",           # WordPress default since v5.5
        f"{base_domain}/sitemap_index.xml",        # Yoast SEO plugin
        f"{base_domain}/post-sitemap.xml",
        f"{base_domain}/page-sitemap.xml"
    ]

    urls = []
    for sitemap_url in sitemap_candidates:
        try:
            print(f"Checking sitemap: {sitemap_url}")
            resp = requests.get(sitemap_url, timeout=10)
            if resp.status_code == 200 and "<urlset" in resp.text or "<sitemapindex" in resp.text:
                soup = BeautifulSoup(resp.content, 'xml')
                for loc in soup.find_all('loc'):
                    url = loc.text.strip()
                    if url.startswith(base_domain):
                        urls.append(url)
        except Exception:
            continue
    return list(set(urls))

# --- Main function to scrape meta data ---
def scrape_website_meta_to_excel(start_url, output_excel_path):
    base_domain = f"https://{start_url.split('://')[-1].split('/')[0]}"

    print(f"Scanning {base_domain} for sitemap URLs...")
    urls_to_scrape = get_urls_from_sitemaps(base_domain)

    if not urls_to_scrape:
        print("No sitemap found. Collecting links directly from home page...")
        try:
            response = requests.get(start_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.content, 'html.parser')

            # Detect if it's WordPress
            if is_wordpress_site(soup):
                print("✅ WordPress site detected.")
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(base_domain, href)
                if full_url.startswith(base_domain):
                    urls_to_scrape.append(full_url)
        except Exception as e:
            print(f"Error fetching links: {e}")

    urls_to_scrape = list(set(urls_to_scrape))
    print(f"Found {len(urls_to_scrape)} URLs to scrape.")

    all_data = []
    for url in urls_to_scrape:
        title, desc, keywords = get_metadata(url)
        if not title and not desc:
            print(f"⚠️ Retrying {url} with Selenium...")
            title, desc, keywords = get_metadata(url, use_selenium=True)

        all_data.append({
            "URL": url,
            "Meta Title": title,
            "Meta Description": desc,
            "Meta Keywords": keywords
        })

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_excel(output_excel_path, index=False)
        print(f"\n✅ Metadata scraping completed. Saved to {output_excel_path}")
    else:
        print("❌ No metadata found. Please check site accessibility or JS rendering.")

# --- Run Example ---
if __name__ == "__main__":
    website_url = "https://Example "  # Example: can be WordPress or custom
    output_file = "website_metadata_updated.xlsx"
    scrape_website_meta_to_excel(website_url, output_file)


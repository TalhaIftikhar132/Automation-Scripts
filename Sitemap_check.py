

import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time

# --- CONFIGURATION ---
# Replace with your sitemap URL (e.g., https://example.com/sitemap.xml)
SITEMAP_URL = 'https://Example/sitemap' 

# Priorities you want to specifically target (as strings, matching sitemap format)
TARGET_PRIORITIES = ['1.0000', '0.9000', '0.8000']

# Add any specific URLs here that you want to include regardless of priority
MANUAL_URLS = [
    # 'https://example.com/special-page',
]
# ---------------------

def get_sitemap_urls(sitemap_url):
    """Recursively extracts URLs and priorities from a sitemap or sitemap index using requests."""
    print(f"Fetching sitemap: {sitemap_url}")
    urls = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(sitemap_url, headers=headers, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        # Namespace for sitemap tags
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Check for nested sitemaps (sitemap index)
        for sitemap in root.findall('sitemap:sitemap', ns):
            loc_element = sitemap.find('sitemap:loc', ns)
            if loc_element is not None and loc_element.text:
                print(f"Found nested sitemap: {loc_element.text}")
                urls.extend(get_sitemap_urls(loc_element.text)) # Recursive call

        # Extract URLs and priorities from the current sitemap
        for url_element in root.findall('sitemap:url', ns):
            loc_element = url_element.find('sitemap:loc', ns)
            priority_element = url_element.find('sitemap:priority', ns)
            
            loc = loc_element.text if loc_element is not None else None
            priority = priority_element.text if priority_element is not None else 'N/A'
            
            if loc:
                urls.append({'url': loc, 'priority': priority})

    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
    except ET.ParseError as e:
        print(f"Error parsing XML from {sitemap_url}: {e}. Content might not be valid XML or has unexpected structure.")
    except Exception as e:
        print(f"An unexpected error occurred while processing {sitemap_url}: {e}")
    return urls

def check_url_status(url):
    """Checks the HTTP status code of a given URL."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    print(f"Fetching URLs from {SITEMAP_URL}...")
    all_extracted_urls = get_sitemap_urls(SITEMAP_URL)
    print(f"Found {len(all_extracted_urls)} URLs from sitemap(s).")

    # Filter based on priority and add manual URLs
    filtered_list = []
    seen_urls = set()

    for item in all_extracted_urls:
        if item['priority'] in TARGET_PRIORITIES and item['url'] not in seen_urls:
            filtered_list.append(item)
            seen_urls.add(item['url'])

    for m_url in MANUAL_URLS:
        if m_url not in seen_urls:
            filtered_list.append({'url': m_url, 'priority': 'Manual'})
            seen_urls.add(m_url)

    if not filtered_list:
        print("No URLs found matching your criteria. Check your SITEMAP_URL and TARGET_PRIORITIES.")
        return

    # Check status codes
    print(f"Auditing {len(filtered_list)} URLs...")
    results = []
    for item in filtered_list:
        url = item['url']
        status = check_url_status(url)
        
        results.append({
            'URL': url,
            'Priority': item['priority'],
            'Status Code': status,
            'Is Broken': 'Yes' if (isinstance(status, int) and status >= 400) or isinstance(status, str) else 'No'
        })
        print(f"Checked: {url} - Status: {status}")
        time.sleep(0.2) # Polite delay to avoid overwhelming the server

    # Sort and Export
    df = pd.DataFrame(results)
    
    # Define custom sorting order for priority
    priority_order = {'1.0000': 0, '0.9000': 1, '0.8000': 2, 'Manual': 3, 'N/A': 4}
    df['sort_order'] = df['Priority'].map(priority_order).fillna(5)
    df = df.sort_values('sort_order').drop('sort_order', axis=1)

    # Export to Excel
    output_file = 'OWR AE sitemap_audit_report.xlsx'
    try:
        df.to_excel(output_file, index=False)
        print(f"\nAudit complete! Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")

if __name__ == "__main__":
    main()
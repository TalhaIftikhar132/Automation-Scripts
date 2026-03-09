import requests
import time
import pandas as pd
from requests.auth import HTTPBasicAuth

# List of websites to audit
websites = [
    "https://Example/blog",
    "http://Example"
    

]

# Common WordPress endpoints
endpoints = {
    "Posts": "/wp-json/wp/v2/posts",
    "Pages": "/wp-json/wp/v2/pages",
    "Users": "/wp-json/wp/v2/users",
    "Categories": "/wp-json/wp/v2/categories",
    "Tags": "/wp-json/wp/v2/tags",
    "Media": "/wp-json/wp/v2/media",
    "Comments": "/wp-json/wp/v2/comments",
    "Settings": "/wp-json/wp/v2/settings"
}

# Admin credentials (optional — only if you have access)
username = "admin"
password = "application_password"

results = []

for site in websites:
    for name, endpoint in endpoints.items():

        url = site + endpoint
        start_time = time.time()

        try:
            if name == "Settings":
                response = requests.get(url, auth=HTTPBasicAuth(username, password))
            else:
                response = requests.get(url)

            response_time = round(time.time() - start_time, 2)

            status_code = response.status_code

            try:
                data = response.json()
                response_type = type(data).__name__
            except:
                response_type = "Invalid JSON"

            results.append([
                site,
                name,
                url,
                status_code,
                response_time,
                response_type
            ])

        except Exception as e:
            results.append([
                site,
                name,
                url,
                "Error",
                "N/A",
                str(e)
            ])


# Create DataFrame report
df = pd.DataFrame(results, columns=[
    "Website",
    "Endpoint",
    "URL",
    "Status Code",
    "Response Time (s)",
    "Response Type"
])

# Save report
df.to_excel("multi_site_audit_report.xlsx", index=False)

print("Audit completed for all websites.")
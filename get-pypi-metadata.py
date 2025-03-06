import requests
from bs4 import BeautifulSoup
import json
import time
import re
import sys

def parse_requirements_file(file_path):
    packages = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                package_name = re.split(r'[=<>~!]', line)[0].strip()
                if package_name:
                    packages.append(package_name)
    return packages

def extract_score_value(score_text):
    if score_text and '/' in score_text:
        try:
            return int(score_text.split('/')[0].strip())
        except ValueError:
            pass
    return 0

def fetch_snyk_data(package_name):
    url = f"https://snyk.io/advisor/python/{package_name}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data for {package_name}: HTTP {response.status_code}")
            return None
        
        return response.text
    except Exception as e:
        print(f"Error fetching {package_name}: {str(e)}")
        return None

"""NOTE: I expect that these HTML elements are subject to change over time. If
the script does not generate correct results, you probably want to look here."""
def parse_snyk_data(html_content, package_name):
    if not html_content:
        return None
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = {"package": package_name}
        
        score_elem = soup.select_one('span[data-v-3f4fee08][data-v-77223d2e]')
        if not score_elem:
            score_elem = soup.select_one('div.number span')
        result["score"] = score_elem.text.strip() if score_elem else "N/A"
        
        scores = {}
        score_items = soup.select('ul.scores li')
        for li in score_items:
            category_elem = li.select_one('span')
            if not category_elem:
                continue
                
            category = category_elem.text.strip().lower()
            value_elem = li.select_one('.vue--pill .vue--pill__body')
            value = value_elem.text.strip() if value_elem else "N/A"
            scores[category] = value
        result.update(scores)
        
        stats = {"stars": "N/A", "forks": "N/A", "contributors": "N/A"}
        
        for div in soup.select('.stats-item'):
            label = div.select_one('dt span')
            if not label:
                continue
                
            label_text = label.text.strip()
            value = div.select_one('dd span')
            value_text = value.text.strip() if value else "N/A"
            
            if "GitHub Stars" in label_text:
                stats["stars"] = value_text
            elif "Forks" in label_text:
                stats["forks"] = value_text
            elif "Contributors" in label_text:
                stats["contributors"] = value_text
        
        result.update(stats)
        
        result["score_value"] = extract_score_value(result["score"])
        
        return result
    
    except Exception as e:
        print(f"Error parsing data for {package_name}: {str(e)}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py requirements.txt <snyk_meta.json>")
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = "snyk_meta.json"
    
    packages = parse_requirements_file(requirements_file)
    print(f"Found {len(packages)} packages in {requirements_file}")
    
    results = []
    for i, package in enumerate(packages):
        print(f"Processing {i+1}/{len(packages)}: {package}")
        html_content = fetch_snyk_data(package)
        metadata = parse_snyk_data(html_content, package)
        if metadata:
            results.append(metadata)
        # NOTE: hopefully this is enough to not get ratelimited, could consider jitter.
        time.sleep(0.5)
    
    sorted_results = sorted(results, key=lambda x: x.get("score_value", 0), reverse=True)
    
    for item in sorted_results:
        if "score_value" in item:
            del item["score_value"]
    
    with open(output_file, 'w') as f:
        json.dump(sorted_results, f, indent=2)
    
    print(f"Saved sorted metadata for {len(sorted_results)} packages to {output_file}")

if __name__ == "__main__":
    main()

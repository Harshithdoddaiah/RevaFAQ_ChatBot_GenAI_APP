import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.reva.edu.in/faq'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

faq_data = []

# Find all <a> tags with role="button" and href pointing to collapse IDs
faq_links = soup.find_all('a', {'role': 'button', 'data-toggle': 'collapse'})

for link in faq_links:
    question_tag = link.find('div', class_='dateDetails')
    if not question_tag:
        continue
    question = question_tag.get_text(strip=True)
    
    collapse_id = link.get('href', '').replace('#', '').strip()
    answer_div = soup.find('div', {'id': collapse_id})
    
    if answer_div:
        answer = answer_div.get_text(strip=True)
        faq_data.append({'Question': question, 'Answer': answer})

# Save to CSV
df = pd.DataFrame(faq_data)
df.to_csv('reva_faq_output.csv', index=False, encoding='utf-8')
print("Saved to reva_faq_output.csv")
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://www.reva.edu.in"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_internal_links(base_url):
    response = requests.get(base_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    domain = urlparse(base_url).netloc
    links = set()

    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"]).split("#")[0]
        if urlparse(full_url).netloc == domain:
            links.add(full_url)

    return list(links)


def scrape_faq_page(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    faq_data = []
    faq_links = soup.find_all("a", {"role": "button", "data-toggle": "collapse"})

    for link in faq_links:
        question_div = link.find("div", class_="dateDetails")
        if not question_div:
            continue

        question = question_div.get_text(strip=True)
        collapse_id = link.get("href", "").replace("#", "")
        answer_div = soup.find("div", id=collapse_id)

        if answer_div:
            answer = " ".join(answer_div.stripped_strings)
            faq_data.append({
                "Page_Type": "FAQ",
                "URL": url,
                "Title": question,
                "Content": answer
            })

    return faq_data


def scrape_generic_page(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""
    paragraphs = [
        p.get_text(strip=True)
        for p in soup.find_all("p")
        if p.get_text(strip=True)
    ]

    return {
        "Page_Type": "GENERAL",
        "URL": url,
        "Title": title,
        "Content": " ".join(paragraphs)
    }


def scrape_school_member_profile(profile_url):
    response = requests.get(profile_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else ""

    content = " ".join(
        p.get_text(strip=True)
        for p in soup.find_all("p")
        if p.get_text(strip=True)
    )

    return {
        "Page_Type": "SCHOOL_MEMBER",
        "URL": profile_url,
        "Title": name,
        "Content": content
    }


def scrape_school_members_list(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    members = []
    profile_links = set()

    for a in soup.find_all("a", href=True):
        if "/school-member/" in a["href"]:
            profile_links.add(urljoin(url, a["href"]))

    for profile_url in profile_links:
        try:
            members.append(scrape_school_member_profile(profile_url))
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed member page: {profile_url} | {e}")

    return members


def main():
    print("🔍 Collecting internal links...")
    links = get_internal_links(BASE_URL)
    print(f"✅ Found {len(links)} internal pages")

    all_data = []
    visited = set()

    for link in links:
        if link in visited:
            continue
        visited.add(link)

        print(f"Scraping → {link}")

        try:
            if "faq" in link.lower():
                all_data.extend(scrape_faq_page(link))

            elif "school-member" in link.lower():
                all_data.extend(scrape_school_members_list(link))

            else:
                all_data.append(scrape_generic_page(link))

            time.sleep(1)

        except Exception as e:
            print(f"❌ Failed: {link} | {e}")

    df = pd.DataFrame(all_data)
    df = pd.DataFrame(all_data)

    # Drop Page_Type and URL columns if they exist
    df = df.drop(columns=["Page_Type", "URL"], errors="ignore")
    df.insert(0, "ID", range(1, len(df) + 1))

    df.to_csv("reva_complete_website_data.csv", index=False, encoding="utf-8")

    print("🎉 Data saved to reva_complete_website_data.csv")


if __name__ == "__main__":
    main()
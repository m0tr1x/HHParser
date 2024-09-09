import fake_useragent
import requests
import time
from bs4 import BeautifulSoup

def get_links(text, max_pages=5):
    user_agent = fake_useragent.UserAgent()
    url = f"https://hh.ru/search/resume?text={text}&area=1&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&page=0"
    data = requests.get(url, headers={"user-agent": user_agent.random})

    if data.status_code != 200:
        print(f"Ошибка при получении страницы: {data.status_code}")
        return

    soup = BeautifulSoup(data.content, "lxml")

    try:
        pager = soup.find("div", class_="pager")
        page_count = int(pager.find_all("span", recursive=False)[-1].find("a").find("span").text)
        print(f"Найдено страниц: {page_count}")
    except AttributeError:
        print("Не удалось найти количество страниц")
        page_count = 1  # Default to 1 if page count is not found

    for page in range(min(page_count, max_pages)):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/resume?text={text}&area=1&isDefaultArea=true&exp_period=all_time&logic=normal&pos=full_text&page={page}",
                headers={"user-agent": user_agent.random}
            )
            if data.status_code != 200:
                print(f"Ошибка на странице {page}: {data.status_code}")
                continue

            soup = BeautifulSoup(data.content, "lxml")
            resumes = soup.find_all("a", attrs={"data-qa": "serp-item__title", "class": "bloko-link"})
            if resumes:
                for resume in resumes:
                    yield f"https://hh.ru{resume.attrs['href'].split('?')[0]}"
            else:
                print(f"Резюме на странице {page} не найдено")
        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
        time.sleep(1)  # Be considerate with rate limits

def get_resume(link):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={"user-agent": user_agent.random}
    )
    if data.status_code != 200:
        print(f"Ошибка при получении резюме: {data.status_code}")
        return None

    soup = BeautifulSoup(data.content, "lxml")

    try:
        name = soup.find(attrs={"data-qa": "resume-block-title-position"}).text.strip()
    except AttributeError:
        name = "Не удалось получить имя"

    try:
        compensation = soup.find(attrs={"data-qa": "resume-block-salary"}).text.replace("\u2009"," ").replace("\xa0", " ")

    except AttributeError:
        compensation = "Не удалось получить информацию о зарплате"

    resume = {
        "name": name,
        "salary": compensation,
    }
    return resume

if __name__ == '__main__':
    for a in get_links("python"):
        resume = get_resume(a)
        if resume:
            print(resume)
        time.sleep(1)

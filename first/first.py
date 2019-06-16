# -*- coding: utf-8 -*-

import requests
import csv
import time
from bs4 import BeautifulSoup as bs

headers = {"accept":"*/*",
          "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0"
          }

# https://omsk.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=python&area=1&from=cluster_area

# area 68 Омск 160 Алматы 1 Москва 113 Россия
# only_with_salary=true
# order_by=salary_desc
# 

url = {"site":"omsk.hh.ru",
       "profession":"django",
       "area":"113",
    }

def url_current(page=0,salary="false"):
    url_str = "https://" + url["site"] + \
    "/search/vacancy?text=" + url["profession"] + \
    "&area=" + url["area"] + \
    "&page=" + str(page) + \
    "&only_with_salary=" + salary + \
    "&order_by=relevance"
    return url_str

jobs = []

def find_jobs(jobs, soup):
    divs = soup.find_all("div", attrs={"data-qa":"vacancy-serp__vacancy"})
    for div in divs:
        title = div.find("a", attrs={"data-qa":"vacancy-serp__vacancy-title"}).text
        href = div.find("a", attrs={"data-qa":"vacancy-serp__vacancy-title"})["href"]
        employer = div.find("a", attrs={"data-qa":"vacancy-serp__vacancy-employer"}).text
        compensation = div.find("div", attrs={"data-qa":"vacancy-serp__vacancy-compensation"})
        compensation = compensation.text if compensation else "не указана"
        responsibility = div.find("div", attrs={"data-qa":"vacancy-serp__vacancy_snippet_responsibility"}).text
        requirement = div.find("div", attrs={"data-qa":"vacancy-serp__vacancy_snippet_requirement"}).text
        jobs.append({
            "title":title,
            "href":href,
            "employer":employer,
            "compensation":compensation,
            "responsibility":responsibility,
            "requirement":requirement
        })

def hh_parse(base_url, headers):
    jobs = []
    pages = 0
    session = requests.session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        soup = bs(request.content,"lxml")
        try:
            pagination = soup.find_all("a", attrs={"data-qa":"pager-page"})
            pages = int(pagination[-1].text)
        except:
            pass
        find_jobs(jobs, soup)
        if pages > 1:
            for page in range(1, pages):
                base_url = url_current(page=page,salary="true")
                request = session.get(base_url,headers=headers)
                if request.status_code == 200:
                    soup = bs(request.content,"lxml")
                    find_jobs(jobs, soup)
    return jobs


def pretty_print(jobs):
    print(len(jobs))
    for job in jobs:
        print("Вакансия: {}\nСсылка: {}\nКомпания: {}\nОплата: {}\nОписание: {}\nТребования: {}".format(
            job['title'], job['href'], job['employer'], job['compensation'], job['responsibility'], 
            job['requirement']))


def file_writer(jobs):
    with open("jobs.csv","a", encoding='utf8') as file:
        a_pen = csv.writer(file, delimiter=';')
        a_pen.writerow(('Вакансия','Ссылка','Компания','Оплата','Описание','Требования'))
        # a_pen.writerow(('Vac','Ref','Com','Sal','Def','Req'))
        for job in jobs:
            a_pen.writerow((job['title'], job['href'], job['employer'], job['compensation'],
                           job['responsibility'], job['requirement']))


print("Start find")
start = time.time()
base_url = url_current(salary="true")
jobs = hh_parse(base_url,headers)
finish = time.time()
print("Finish find")
print("Time find: {}".format(str(finish-start)))
# pretty_print(jobs)
file_writer(jobs)
finish = time.time()
print("Finish all")
print("Time all: {}".format(str(finish-start)))
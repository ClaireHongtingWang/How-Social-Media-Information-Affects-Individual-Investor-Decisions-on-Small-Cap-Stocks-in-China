import openpyxl as openpyxl
import pandas as pd
import requests
import random
from bs4 import BeautifulSoup
from future import *
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from requests.adapters import HTTPAdapter
from requests.packages import *
from time import sleep



def gather_data_2_years(
        url_prefix,
        log_element_example=False):
    """
    start_page and end_page are inclusive

    returns a list of (content, time, read, comment)
    """
    global all_comments_num

    ret = []
    current_year = 2021
    last_month = 12

    page_num = 0
    consec_errorcnt = 0
    while True and consec_errorcnt < 10:
        if current_year == 2019 or page_num == 10:
            return ret
        page_num += 1
        url = url_prefix + str(page_num) + '.html'
        print(url)
        # print(page_num)
        unreliable_page = False
        unsuccessful_get = True
        unsuccessful_get_cnt = 0
        while unsuccessful_get:
            if unsuccessful_get_cnt > 5:
                break
            try:
                # headers = {'user-agent': random.choice(agents)}
                headers = {'user-agent': 'Baiduspider'}
                page = requests.get(url, headers=headers, timeout=5)
                unsuccessful_get = False
            except requests.exceptions.Timeout as err:
                print("error occurred")
                unreliable_page = True
                unsuccessful_get_cnt += 1
            except requests.exceptions.ConnectionError as err2:
                print("error occurred")
                unreliable_page = True
                unsuccessful_get_cnt += 1
        # page = requests.get(url)
        if unsuccessful_get_cnt > 5:
            continue
        print(page.status_code)
        if page.status_code != 200:
            consec_errorcnt += 1
            continue
        consec_errorcnt = 0
        # print(page.text)
        soup = BeautifulSoup(page.text, "html.parser")
        # soup = BeautifulSoup(page.content.decode("utf-8"), 'lxml')
        # print(soup.text.decode("unicode-escape"))

        results = soup.find(id="blk_list_02")
        r1 = results.find_all("tr", class_="")
        # print(r1)
        r2 = results.find_all("tr", class_="tr2")
        temp_res1 = []
        temp_res2 = []
        for r1e in r1:
            sleep(0.15)
            all_content = r1e.find_all("td")
            if len(all_content) != 5:
                print('error, length of all_content should be 5')
                continue
            click = all_content[0].text
            reply = all_content[1].text
            title = all_content[2].find("a").text
            author = all_content[3].find("div").text
            date = all_content[4].text
            cur_month = int(date[0:2])
            if cur_month > last_month:
                current_year -= 1
            last_month = cur_month
            second_link_suffix = all_content[2].find("a").get('href')
            second_url = "http://guba.sina.com.cn/" + second_link_suffix
            headers = {'user-agent': 'Baiduspider'}
            sub_page = requests.get(second_url, headers=headers, timeout=5)
            print(sub_page.status_code)
            sub_soup = BeautifulSoup(sub_page.text, "html.parser")
            content = sub_soup.find('div', id='thread_content').text
            temp_res1.append((click, reply, title, author, str(current_year) + "年" + date[:-1], content))
            if current_year == 2019:
                break

        for r1e in r2:
            sleep(0.15)
            all_content = r1e.find_all("td")
            if len(all_content) != 5:
                print('error, length of all_content should be 5')
                continue
            click = all_content[0].text
            reply = all_content[1].text
            title = all_content[2].find("a").text
            author = all_content[3].find("div").text
            date = all_content[4].text
            cur_month = int(date[0:2])
            if cur_month > last_month:
                current_year -= 1
            last_month = cur_month
            second_link_suffix = all_content[2].find("a").get('href')
            second_url = "http://guba.sina.com.cn/" + second_link_suffix
            headers = {'user-agent': 'Baiduspider'}
            sub_page = requests.get(second_url, headers=headers, timeout=5)
            print(sub_page.status_code)
            sub_soup = BeautifulSoup(sub_page.text, "html.parser")
            content = sub_soup.find('div', id='thread_content').text
            temp_res2.append((click, reply, title, author, str(current_year) + "年" + date[:-1], content))
            if current_year == 2019:
                break

        # combine res1 with res2
        for i in range(max(len(temp_res1), len(temp_res2))):
            if i < len(temp_res1):
                ret.append(temp_res1[i])
            if i < len(temp_res2):
                ret.append(temp_res2[i])

    return ret


stockres = pd.read_excel('output.xlsx', index_col=0)
# print(stockres)

for i in range(81, 88, 1):
    stock_code = str(stockres.at[i, '证券代码'][0:6])
    stock_prefix = str(stockres.at[i, '证券代码'][7:9]).lower()
    print(stock_code)

    res = gather_data_2_years("http://guba.sina.com.cn/?s=bar&name=" + stock_prefix + str(stock_code) +"&type=0&page=")
    print("creating a pd...")
    df1 = pd.DataFrame([],
                       index=[i for i in range(len(res))],
                       columns=['click', 'reply', 'post', 'author', 'date', 'content'])
    results = list(set(res))
    print(results)
    print("writing to excel...")
    for idx in range(len(results)):
        df1.at[idx, 'click'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][0])
        # (r'',x)results[idx][0]
        df1.at[idx, 'reply'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][1])
        df1.at[idx, 'post'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][2])
        df1.at[idx, 'author'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][3])
        df1.at[idx, 'date'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][4])
        df1.at[idx, 'content'] = ILLEGAL_CHARACTERS_RE.sub(r'', results[idx][5])
    excel_name = str(stock_code) + ".xlsx"
    df1.to_excel(excel_name)
    print("finished writing")
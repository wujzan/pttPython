#吳倬安 508170624

import time
from bs4 import BeautifulSoup
from requests import Session
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
# 自訂義的model(解決標題不合法字元當檔案名)
import customModel.fixFileName

import os
# 中檢查目錄是否存在，若是不存在的情況下建立它
if not os.path.exists('authorAllPost'):
    os.makedirs('authorAllPost')

# 使用者輸入(menu)
while True:
    try:
        # example_ID: ptk9811107
        author_id = input('請輸入要搜尋的PTT id:')
        if len(author_id) == 0:
            raise ValueError

        userInputGrabPages = int(input('請輸入要抓取頁數 的整數:'))
        if userInputGrabPages < 1:
            raise ValueError

        break
    except ValueError as err:
        print('輸入錯誤,請重新輸入:')


session = Session()

def getAllPostLinks():
    page = 1
    endPage = userInputGrabPages
    while page <= endPage:
        check_haveNextpage = None
        pageURL = 'http://www.ucptt.com/author/' + author_id + '/' + str(page)
        response = session.get(pageURL)
        print('###############')
        print(f'目前已經爬到 第{page}頁')
        soup = BeautifulSoup(response.text, 'html.parser')  # root  features="lxml"

        links = []
        elements = soup.find_all('a', class_='list-group-item')
        for elem in elements:  # 單頁全部文章連結都加入名為links的list中
            URL_OK = "http://www.ucptt.com" + elem["href"]
            links.append(URL_OK)
        # print(links)

        print('開始抓取文章:')
        handle(links)

        ######檢查是否還有 下一頁#######
        check_haveNextpage = soup.find('li', class_='next')
        if check_haveNextpage == None:
            endPage = page-1
        else:
            page += 1
            time.sleep(1)  # 防止被鎖IP


boards=[]  # 存放有抓取文章的看板放入list中
def board_count():  # list中各看板類型統計
    dict={}
    for key in boards:
        dict[key] = dict.get(key, 0) + 1
    print(dict)
    drawGraph(dict)


posts = []
def handle(links):
    htmls = []
    for num, link in enumerate(links):
        print(f'正在抓取第 {num+1}篇文章')
        response = session.get(link)
        htmls.append(response.text)
        # time.sleep(1)  # 防止被鎖IP

    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        for br in soup.find_all("br"):
            br.replace_with('\n')

        title = soup.select('h3')[0].text
        created_time = soup.select('div.panel-heading > span')[0].text
        board = soup.select('ol > li:nth-of-type(2)> a')[0].text
        boards.append(board)
        content = soup.select('div.panel-body')[0].text

        ##############
        # 儲存成 "單一" .csv檔案
        post = {'看板': board, '文章標題': title, '作者': author_id, '發文時間': created_time, '文章內容': content}
        posts.append(post)
        df = pd.DataFrame(posts)
        # 參數mode='a' 不覆蓋到資料
        df.to_csv("./authorAllPost/" + author_id + "_authorAllPost.csv", encoding='utf_8_sig', index=False)
        ##############
        # 儲存成 "個別" .txt檔案
        # 由於抓取"文章標題"做 檔案名稱, 若遇到不合法字元, 取代掉它
        fixedTitle = customModel.fixFileName.replace(title)
        f = open("./authorAllPost/" + author_id + "." + fixedTitle + ".txt", "w", encoding='utf-8')

        f.write(title)
        f.write('\n看板: ')
        f.write(board)
        f.write('\n作者: ')
        f.write(author_id)
        f.write('\n發文時間: ')
        f.write(created_time)
        f.write('\n文章內容: \n')
        f.write(content)
        f.close()


# 資料視覺化 -->做圖
def drawGraph(dict):
    boardList = sorted(dict.items(), key=lambda item: item[1], reverse=True)
    # print(boardList)
    x, y = zip(*boardList)
    plt.xticks(rotation=90)  # 旋轉標籤文字90度
    plt.plot(x, y)
    # plt.show()


    df = pd.read_csv("./authorAllPost/" + author_id + "_authorAllPost.csv", encoding='utf_8_sig')
    postDates = df['發文時間']  # 讀取欄位 -->發文日期
    hourData=[]
    for postDate in postDates:
        date = datetime.strptime(postDate, '%Y-%m-%d %H:%M:%S')
        hourData.append(int(date.strftime('%H')))  # 字串轉為int 存入list
    # Post in 24hr(24小時發文時間)
    s = pd.DataFrame(hourData)  # value
    s.hist(bins=25, alpha=0.5, figsize=(9, 7))
    plt.title('Histogram')
    s.plot(kind='kde', secondary_y=False, figsize=(9, 7))
    plt.grid()
    plt.show()  # 顯示出圖形


def main():
    start_time = time.time()
    print('取得文章連結URL:')
    getAllPostLinks()
    end_time = time.time()

    print('###############')
    print('爬取結束')
    print("抓取共耗時: {:.2f}秒".format(end_time - start_time))

    print("各看板類型統計:")
    board_count()


# 執行
main()
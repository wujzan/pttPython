#吳倬安 508170624

import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
# 自訂義的model(解決標題不合法字元當檔案名)
import customModel.fixFileName
import customModel.selectBoard

import os
# 中檢查目錄是否存在，若是不存在的情況下建立它
if not os.path.exists('boardAllPost'):
    os.makedirs('boardAllPost')


# 使用者輸入(menu)
while True:
    try:
        userSelectBoard = int(input('請輸入要抓取的PTT看版 的整數: (0)movie (1)stock (2)C_Chat (3)Tech_Job :'))
        if userSelectBoard < 0 or userSelectBoard > 3:
            raise ValueError

        replyedCount = int(input('請輸入要抓取PTT看版 >=回復量 的整數:'))
        if replyedCount < 1:
            raise ValueError

        userInputGrabPages = int(input('請輸入要抓取頁數 的整數:'))
        if userInputGrabPages < 1:
            raise ValueError

        numbered = int(input('抓取下來的個別文章 檔名標題前面加上編號排序? (0)否 (1)是 :'))
        if not ((numbered == 0) or (numbered == 1)):
            raise ValueError

        isDrawGraph = int(input('抓取結束後是否進行資料視覺化分析做圖? (0)否 (1)是 :'))
        if not ((isDrawGraph == 0) or (isDrawGraph == 1)):
            raise ValueError

        break
    except ValueError as err:
        print('輸入錯誤,請重新輸入:')


# 用於爬取PTT
def grab():
    # PTT看版 網址URL
    pageURL = customModel.selectBoard.links(userSelectBoard)
    # print(pageURL)
    # 計數初始值為 第1頁
    start = 1
    # 要抓取的頁面數
    end = userInputGrabPages
    for currentCountLoop in range(start, end+1):
        print(f'目前已經爬到 第{str(currentCountLoop)}頁, 總共頁數: {str(end)}頁')
        returnURL = parsePage(pageURL)
        pageURL = returnURL
        time.sleep(1)  # 防止被鎖IP


titleTages=[]  # 存放有抓取文章的tage放入list中
def tage_count():  # list中各類型統計
    dict={}
    for key in titleTages:
        dict[key] = dict.get(key, 0) + 1
    # 字典排序(由大到小)
    sort = {key: value for key, value in sorted(dict.items(), key=lambda item: item[1], reverse=True)}
    print(sort)


def check_skip_tage(titleTage):
    # 略過 "贈票"-->電影廠商廣告
    # 略過 "公告"-->版主版規公告
    skip_tage_list = ["贈票", "公告"]
    for item in skip_tage_list:
        if titleTage == item:
            return False
    return True


# 把要抓取 >=回復量 & 爆文  -->存入list中
def parsePage(pageURL):
    response = requests.get(pageURL)
    root = BeautifulSoup(response.text, 'html.parser')
    articleList = root.find_all('div', class_='r-ent')
    href_list = list()

    for div in articleList:
        try:
            titleTage = ((div.find('div', class_='title').text.split('['))[1].split(']'))[0]

            if check_skip_tage(titleTage):
                targetReplyedCount = div.find('div', class_='nrec').text

                # 爆文: 推文 減 噓文 大於100時,就會變成「推爆」的狀況
                if targetReplyedCount == '爆':
                    print('回復量: 爆(超過100(含))')
                    flag = 100  # 超過100顯示'爆',以100來計
                    titleTages.append(titleTage)
                    content_list = list()
                    # split('\n')是以換行符號作為分割存入list, split('\n')[0]是獲取第1行
                    content_list.append(div.find('div', class_='title').text.split('\n')[1])
                    content_list.append(div.find('div', class_='title').a.get('href'))  # 標題網址的超連結
                    all = (content_list, flag)  # 用all這個list來存 當前"標題+網址", "推文減噓文數"
                    href_list.append(all)

                elif int(targetReplyedCount) >= replyedCount:
                    print('回復量:', targetReplyedCount)
                    flag = int(targetReplyedCount)
                    titleTages.append(titleTage)
                    content_list = list()
                    content_list.append(div.find('div', class_='title').text.split('\n')[1])
                    content_list.append(div.find('div', class_='title').a.get('href'))
                    all = (content_list, flag)
                    href_list.append(all)
        except:
            print("遇到title之中沒符合條件-->略過")  # 包含(本文已被刪除)

    for item in href_list:
        handleArticle(item)

    # 繼續前往 下一頁 -->抓取"上一頁"的連結
    nextLink = root.find("a", string="‹ 上頁")  # 找到內文是 ‹ 上頁 的 a 標籤
    nextURL = nextLink["href"]
    URL_OK = "https://www.ptt.cc" + nextURL
    return URL_OK


# 讀取網頁文章內容-->整理-->存入檔案
count = 0
posts = []
def handleArticle(dataAll):
    global count
    count += 1

    data = dataAll[0]  # 標題 -->data[0], 網址(./bbs/movie/xxxx.html) -->data[1]
    flag = dataAll[1]  # 推文減噓文數

    # 由於抓取"文章標題"做 檔案名稱, 若遇到不合法字元, 取代掉它
    fixedTitle = customModel.fixFileName.replace(data[0])
    URL = "https://www.ptt.cc" + data[1]
    response = requests.get(URL)
    root = BeautifulSoup(response.text, 'html.parser')

    main_content = root.find("div", id="main-content")
    article_header = main_content.find_all("span", class_="article-meta-value")

    # 去掉文章內文中 發信站後面內容 (IP+全部的推文回復)
    chose = 2  # 預設選第2種,無'--'底線資料整理後比較乾淨
    if chose == 1:
        # 根據 文章結束後的'※ 發信站' 作文章內容的分隔
        content = root.find('div', id='main-content').text.split('※ 發信站')[0]
    else:
        # 根據 文章結束後的'--' 作文章內容的分隔(若文章中結束前有提早出現'--',可能會造成bug抓取不全)
        content = root.find('div', id='main-content').text.split('--')[0]

    texts = content.split("\n")[1:]  # 以換行符號作為分割存入list,保留第2行以後的內容
    content_lite = "\n".join(texts)

    if len(article_header) != 0:
        author = article_header[0].text  # 發文作者
        title = article_header[2].text  # 文章標題
        time = article_header[3].text  # 發文時間
    else:  # 防止抓取出錯
        author = "無"
        title = "無"
        time = "無"

    ##############
    # 儲存成 "單一" allPost.csv檔案
    post = {'編號': count, '文章標題': title, '作者': author, '發文時間': time, '文章內容': content_lite,
            '推文減噓文數': flag, '文章網址URL': URL, '原始資料內容(未整理.備份)': content}
    posts.append(post)
    df1 = pd.DataFrame(posts)
    df1.to_csv('./boardAllPost/allPost.csv', encoding='utf_8_sig', index=False)
    ##############
    # 儲存成 "個別" .txt檔案
    if numbered == 0:  # 檔名文章標題前面 "不用"加上編號排序
        f = open("./boardAllPost/" + fixedTitle + ".txt", "w", encoding='utf-8')
    else:  # 檔名文章標題前面加上編號排序
        f = open("./boardAllPost/" + str(count) + "." + fixedTitle + ".txt", "w", encoding='utf-8')

    # f.write(content)  #(未整理)
    f.write(title)
    f.write('\n作者: ')
    f.write(author)
    f.write('\n發文時間: ')
    f.write(time)
    f.write('\n文章內容: \n')
    f.write(content_lite)
    f.close()


# 資料視覺化 -->做圖
def drawGraph():
    # 讀取剛剛抓下來儲存成 allPost.csv 的那個檔案
    df = pd.read_csv('./boardAllPost/allPost.csv', encoding='utf_8_sig')
    mydata = list(df.loc[:, '推文減噓文數'])  # 讀取欄位 數值資料, 存成list

    print('#################')
    print('資料視覺化:')

    mean = df['推文減噓文數'].mean()
    print('平均數: {:.3f}'.format(mean))  # 平均數

    median = df['推文減噓文數'].median()
    print('中位數: {:.3f}'.format(median))  # 中位數

    std = df['推文減噓文數'].std()
    print('標準差: {:.3f}'.format(std))  # 標準差

    data = [["ReplyedCount", mean, median, std]]
    df1 = pd.DataFrame(data, columns=["ReplyedCount", "mean", "median", "std"])
    df1.plot(x="ReplyedCount", y=["mean", "median", "std"], kind="barh", figsize=(12, 4))
    # plt.show()

    # 散布圖 & 直方圖
    s = pd.DataFrame(mydata, columns=[''])  # value
    fig = plt.figure(figsize=(9, 7))
    # 子圖1 -->散布圖
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.scatter(s.index, s.values)
    plt.title('Scatter diagram')
    plt.grid()  # 顯示網格
    # 子圖2 -->直方圖
    ax2 = fig.add_subplot(2, 1, 2)
    s.hist(bins=30, alpha=0.5, ax=ax2)
    s.plot(kind='kde', secondary_y=True, ax=ax2)
    plt.title('Histogram')
    plt.grid()
    plt.show()  # 顯示出圖形


def main():
    start_time = time.time()
    grab()
    end_time = time.time()
    print('#################')
    print('爬取結束')
    print("抓取共耗時: {:.2f}秒".format(end_time - start_time))

    print("各類型統計:")
    tage_count()

    if isDrawGraph == 1:  # 做圖
        drawGraph()

# 執行
main()

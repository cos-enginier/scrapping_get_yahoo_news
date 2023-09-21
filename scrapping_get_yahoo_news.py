import requests
from bs4 import BeautifulSoup
import re
import csv
import copy



def create_new_list(headline_link_list):
    news_list = []
    # ヤフーニュース見出のURLリストから記事URLを取得し、記事内容を取得する
    for headline_link in headline_link_list:

        # ヤフーニュース見出のURLから、　要約ページの内容を取得する
        summary = requests.get(headline_link)

        # 取得した要約ページをBeautifulSoupで解析できるようにする
        summary_soup = BeautifulSoup(summary.text, "html.parser")
        
        # aタグの中に「続きを読む」が含まれているテキストを抽出する
        # ヤフーのページ構成は[Top] -> [要約] -> [本文] となっており、
        # [要約]から[本文]に遷移するには「続きを読む」をクリックする必要がある。
        summary_soup_a = summary_soup.select("a:contains('記事全文を読む')")[0]

        # aタグの中の"href="から先のテキストを抽出する。
        # するとヤフーの記事本文のURLを取得できる
        news_body_link = summary_soup_a.attrs["href"]

        # 記事本文のURLから記事本文のページ内容を取得する
        news_body = requests.get(news_body_link)
        # 取得した記事本文のページをBeautifulSoupで解析できるようにする
        news_soup = BeautifulSoup(news_body.text, "html.parser")

        dict = {'title':"",'link':"",'text':""}

        # 記事本文のタイトルを表示する
        dict['title'] = news_soup.title.text

        # 記事本文のURLを表示する
        dict['link'] = news_body_link

        # class属性の中に「Direct」が含まれる行を抽出する
        detail_text = news_soup.find_all(class_=re.compile("Direct"))

        # 記事本文を出力する
        # hasattr:指定のオブジェクトが特定の属性を持っているかを確認する
        for i in range(len(detail_text)):
            if hasattr(detail_text[i], "text"):
                dict['text'] +=detail_text[i].text
            else:
                dict['text'] += ''
            
        #ニュース記事を追加する
        news_list.append(copy.deepcopy(dict))

    return news_list
    


def csv_out(new_list):
    #CSVにレビュー情報の書き出し
    with open('data/sample.csv','w',encoding=ENCODING, newline='\n') as f:
            
        writer = csv.writer(f, lineterminator='\n')
        #ヘッダを作成する
        header=[]
        header.append('No')
        header.append('タイトル')
        header.append('リンク')
        header.append('記事')
        writer.writerow(header)
        
        #ニュース記事をcsv出力する
        for i in range(len(news_list)):

            csvlist=[]
            dict = news_list[i]
            #データ作成
            csvlist.append('{}'.format(i+1))      
            csvlist.append(dict['title'])         
            csvlist.append(dict['link'])
            csvlist.append(dict['text'])
            # 出力    
            writer.writerow(csvlist)

        # ファイルクローズ
        f.close()

if __name__ == '__main__':  
    # ヤフーニュースのトップページ情報を取得する
    URL = "https://www.yahoo.co.jp/"
    res = requests.get(URL)
    ENCODING = 'utf_8_sig'
    news_list = []

    # BeautifulSoupにヤフーニュースのページ内容を読み込ませる
    soup = BeautifulSoup(res.text, "html.parser")

    # URLに news.yahoo.co.jp/pickup が含まれるものを抽出する。
    data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup"))

    #! ここから先を修正、追記 !#

    # ヤフーニュース見出のURL情報をループで取得し、リストで格納する。
    headline_link_list = [data.attrs["href"] for data in data_list]
    
    #ニュース情報作成
    news_list = create_new_list(headline_link_list)
    
    #ニュース情報をcsv出力
    csv_out(news_list)

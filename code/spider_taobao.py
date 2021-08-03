import json
import os
import re
import requests
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from retrying import retry

start = time.perf_counter()

# plist 为1-100页的URL的编号num
plist = []
for i in range(1, 101):  # [0, 44, 88, ..., 4356]
    j = 44 * (i - 1)
    plist.append(j)

plist_no = plist  # 初始化未爬取编号

key = '帽子'
GOODS_EXCEL_PATH = f'sales_data_{key}.xlsx'
taobao_search_url = f'https://s.taobao.com/search?q={key}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180207&ie=utf8&sort=sale-desc&style=list&fs=1&bcoffset=0&p4ppushleft=%2C44&s='
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
            AppleWebKit/537.36(KHTML, like Gecko)  \
            Chrome/55.0.2883.87 Safari/537.36'}

columns = ['raw_title', 'view_price', 'item_loc', 'view_sales', 'pic_url', 'nick', 'detail_url', 'comment_url',
           'comment_count']


# 解析抓取的json数据
def parse_json(json_data):
    g_json = json.loads(json_data)
    g_items = g_json['mods']['itemlist']['data']['auctions']
    g_list = []
    for item in g_items:
        goods = {
            'raw_title': item['raw_title'],
            'view_price': item['view_price'],
            'item_loc': item['item_loc'],
            'view_sales': item['view_sales'],
            'pic_url': item['pic_url'],
            'nick': item['nick'],
            'detail_url': item['detail_url'],
            'comment_url': item['comment_url'],
            'comment_count': item['comment_count'],
        }
        g_list.append(goods)
    return g_list


# 保存抓取的json数据
def save_excel(goods_list):
    # pandas没有对excel没有追加模式，只能先读后写
    if os.path.exists(GOODS_EXCEL_PATH):
        df = pd.read_excel(GOODS_EXCEL_PATH, engine='openpyxl')
        df = df.append(goods_list)
    else:
        df = pd.DataFrame(goods_list)

    print("excel len : ", len(df))
    writer = pd.ExcelWriter(GOODS_EXCEL_PATH)
    # columns参数用于指定生成的excel中列的顺序
    df.to_excel(excel_writer=writer,
                columns=columns, index=False,
                encoding='utf-8', sheet_name='Sheet')
    writer.save()
    writer.close()


while True:
    @retry(stop_max_attempt_number=10)  # 设置最大重试次数
    def network_programming(num):
        url = taobao_search_url + str(num)
        web = requests.get(url, headers=headers)
        web.encoding = 'utf-8'
        return web

    # 多线程
    def multithreading():
        number = plist_no  # 每次爬取未爬取成功的页
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for res in executor.map(network_programming,
                                    number, chunksize=10):
                results.append(res)
        return results

    p_num_success = []
    results = multithreading()
    for i in results:
        page_config_json = re.search('g_page_config =(.*?)}};', i.text)
        if page_config_json:
            json_str = page_config_json.group(1) + '}}'
            goods_list = parse_json(json_str)
            p_num = re.findall('"pageNum":(.*?),"p4pbottom_up"', i.text)[0]
            p_num_success.append(p_num)  # 记入每一次爬取成功的页码
            print(len(goods_list), 'page_num: ', p_num)
            print(goods_list[0])
            print(goods_list[-1])
            print("-------------------------")
            save_excel(goods_list)

    plist_success = []
    for a in p_num_success:
        b = 44 * (int(a) - 1)
        plist_success.append(b)  # 将爬取成功的页码转为url中的num值

    listn = plist_no
    plist_no = []  # 将本次爬取失败的页记入列表中 用于循环爬取
    for p in listn:
        if p not in plist_success:
            plist_no.append(p)

    if len(plist_no) == 0:  # 当未爬取页数为0时  终止循环！
        break

end = time.perf_counter()
print("爬取完成 用时：", end - start, 's')

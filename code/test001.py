import re
import time
import requests
import pandas as pd
from retrying import retry
from concurrent.futures import ThreadPoolExecutor
 
start = time.perf_counter()
 
#plist 为1-100页的URL的编号num 
plist = []           
for i in range(1,101):   
    j = 44*(i-1)
    plist.append(j)


listno = plist
datatmsp = pd.DataFrame(columns=[])
#
while True:
   @retry(stop_max_attempt_number = 2)     #设置最大重试次数
   def network_programming(num):
      url='https://s.taobao.com/search?q=%E6%B2%99%E5%8F%91&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20180207&ie=utf8&sort=sale-desc&style=list&fs=1&filter_tianmao=tmall&filter=reserve_price%5B500%2C%5D&bcoffset=0&p4ppushleft=%2C44&s='+str(num)

      web = requests.get(url, headers=headers)
      web.encoding = 'utf-8'
      return web

#   多线程
   def multithreading():
      number = listno        #每次爬取未爬取成功的页
      event = []

      with ThreadPoolExecutor(max_workers=10) as executor:
         for result in executor.map(network_programming,
                                    number, chunksize=10):
             event.append(result)
      return event

   headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) \
            AppleWebKit/537.36(KHTML, like Gecko)  \
            Chrome/55.0.2883.87 Safari/537.36'}

   listpg = []
   event = multithreading()

   for i in event:
      json = re.findall('"auctions":(.*?),"recommendAuctions"', i.text)
      if len(json):
         try:
            table = pd.read_json(json[0])
            datatmsp = pd.concat([datatmsp, table], axis=0, ignore_index=True)
            pg = re.findall('"pageNum":(.*?),"p4pbottom_up"', i.text)[0]
            listpg.append(pg)  # 记入每一次爬取成功的页码
         except ValueError:
            print("ValueError")
            # listpg.append(pg)  # 记入每一次爬取成功的页码
            continue

   lists = []
   for a in listpg:
       b = 44*(int(a)-1)
       lists.append(b)     #将爬取成功的页码转为url中的num值

   listn = listno

   listno = []       #将本次爬取失败的页记入列表中 用于循环爬取
   for p in listn:
       if p not in lists:
           listno.append(p)

   print("datatmsp len: ", len(datatmsp))
   if len(listno) == 0:     #当未爬取页数为0时 终止循环！
      break

# datatmsp.to_excel('datatmsp.xls', index=False)    #导出数据为Excel

end = time.perf_counter()    #计时-结束
print("爬取完成 用时：", end - start,'s')



# '''
# 二、数据清洗、处理： (此步骤也可以在Excel中完成 再读入数据)
# '''
# datatmsp = pd.read_excel('datatmsp.xls')     #读取爬取的数据 
# #datatmsp.shape   
 
# # 数据缺失值分析： 此模块仅供了解  #见下<图1>
# # 安装模块：pip install missingno
# import missingno as msno
# msno.bar(datatmsp.sample(len(datatmsp)),figsize=(10,4))   
 
# # 删除缺失值过半的列： 仅供了解 本例中可以不用
# half_count = len(datatmsp)/2
# datatmsp = datatmsp.dropna(thresh = half_count, axis=1)
 
# # 删除重复行：
# datatmsp = datatmsp.drop_duplicates()   
 
 
# '''
# 说明：根据需求，本案例中我只取了 item_loc, raw_title, view_price, view_sales 这4列数据，
# 主要对 标题、区域、价格、销量 进行分析，代码如下: 
# '''
# # 取出这4列数据：
# data = datatmsp[['item_loc','raw_title','view_price','view_sales']]   
# data.head()    #默认查看前5行数据
 
# # 对 item_loc 列的省份和城市 进行拆分 得出 province 和 city 两列:https://xpanx.com/2099.html
   
# # 生成province列：
# data['province'] = data.item_loc.apply(lambda x: x.split()[0])
 
# # 注：因直辖市的省份和城市相同 这里根据字符长度进行判断： 
# data['city'] = data.item_loc.apply(lambda x: x.split()[0]   \
#                                 if len(x) < 4 else x.split()[1])
 
# # 提取 view_sales 列中的数字，得到 sales 列：                                                  
# data['sales'] = data.view_sales.apply(lambda x: x.split('人')[0])  
 
# # 查看各列数据类型
# data.dtypes   
 
# # 将数据类型进行转换                                             
# data['sales'] = data.sales.astype('int')                                                     
 
# list_col = ['province','city']
# for i in  list_col:
#     data[i] = data[i].astype('category') 
 
# # 删除不用的列：
# data = data.drop(['item_loc','view_sales'], axis=1) 
 
 
 
 
# '''
# 三、数据挖掘与分析：
 
# 【1】. 对 raw_title 列标题进行文本分析：
#    使用结巴分词器，安装模块pip install jieba
# '''                  
# title = data.raw_title.values.tolist()    #转为list
 
# # 对每个标题进行分词：  使用lcut函数
# import jieba
# title_s = []
# for line in title:     
#    title_cut = jieba.lcut(line)    
#    title_s.append(title_cut)
 
 
# '''
# 对 title_s（list of list 格式）中的每个list的元素（str）进行过滤 剔除不需要的词语，
# 即 把停用词表stopwords中有的词语都剔除掉：
# '''
 
# # 导入停用词表：
# stopwords = pd.read_excel('stopwords.xlsx')        
# stopwords = stopwords.stopword.values.tolist()      
 
# # 剔除停用词：
# title_clean = []
# for line in title_s:
#    line_clean = []
#    for word in line:
#       if word not in stopwords:
#          line_clean.append(word)
#    title_clean.append(line_clean)
 
# '''
# 因为下面要统计每个词语的个数，所以 为了准确性 这里对过滤后的数据 title_clean 中的每个list的元素进行去重，
# 即 每个标题被分割后的词语唯一。 
# '''
# title_clean_dist = []  
# for line in title_clean:   
#    line_dist = []
#    for word in line:
#       if word not in line_dist:
#          line_dist.append(word)
#    title_clean_dist.append(line_dist)
 
   
# # 将 title_clean_dist 转化为一个list: allwords_clean_dist 
# allwords_clean_dist = []
# for line in title_clean_dist:
#    for word in line:
#       allwords_clean_dist.append(word)
 
 
# # 把列表 allwords_clean_dist 转为数据框： 
# df_allwords_clean_dist = pd.DataFrame({'allwords': allwords_clean_dist})
 
 
# # 对过滤_去重的词语 进行分类汇总：
# word_count = df_allwords_clean_dist.allwords.value_counts().reset_index()    
# word_count.columns = ['word','count']      #添加列名 
 
 
# '''
# 观察 word_count 表中的词语，发现jieba默认的词典 无法满足需求： 
# 有的词语（如 可拆洗、不可拆洗等）却被cut，这里根据需求对词典加入新词
# （也可以直接在词典dict.txt里面增删，然后载入修改过的dict.txt）
# '''
# add_words = pd.read_excel('add_words.xlsx')     #导入整理好的待添加词语
 
# # 添加词语： 
# for w in add_words.word:
#    jieba.add_word(w , freq=1000)  
  
   
# #=======================================================================
# # 注：再将上面的 分词_过滤_去重_汇总 等代码执行一遍，得到新的 word_count表 
# # https://xpanx.com/2099.html
# #=======================================================================
   
# #word_count.to_excel('word_count.xlsx', index=False)    #导出数据
 
 
# '''
# 词云可视化： 见下<图2>
# 安装模块 wordcloud  
# 方法1：pip install wordcloud  
# 方法2：:下载Packages安装：pip install 软件包名称
# 软件包下载地址：https://www.lfd.uci.edu/~gohlke/pythonlibs/#wordcloud
# 注意：要把下载的软件包放在Python安装路径下。
# '''
# from wordcloud import WordCloud
# import matplotlib.pyplot as plt
# from scipy.misc import imread    
# plt.figure(figsize=(20,10))   
 
# pic = imread("shafa.png")   #读取图片,自定义‘沙发’形状
# w_c = WordCloud(font_path="./data/simhei.ttf",background_color="white", 
#                 mask=pic, max_font_size=60, margin=1)
# wc = w_c.fit_words({x[0]:x[1] for x in word_count.head(100).values})    
 
# plt.imshow(wc, interpolation='bilinear') 
# plt.axis("off")
# plt.show()
 
# '''
# 以上注释：
# shafa.png 是透明背景图 将该图放在Python的项目路径下！
# "./data/simhei.ttf"   设置字体
# background_color   默认是黑色 这里设置成白色
# head(100)   取前100个词进行可视化！ 
# max_font_size　 字体最大字号 
# interpolation='bilinear'  图优化   
# "off"   去除边框
# '''
 
 
# '''
# 分析结论：
# 1. 组合、整装商品占比很高；
# 2. 从沙发材质看：布艺沙发占比很高，比皮艺沙发多；
# 3. 从沙发风格看：简约风格最多，北欧风次之，其他风格排名依次是美式、中式、日式、法式 等；
# 4. 从户型看：小户型占比最高、大小户型次之，大户型最少；
# '''
 
 
 
 
# '''
# 【2】. 不同关键词word对应的sales之和的统计分析： 
#   （说明：例如 词语 ‘简约’，则统计商品标题中含有‘简约’一词的商品的销量之和，即求出具有‘简约’风格的商品销量之和）
#    代码如下：
# '''
# import numpy as np   
 
# w_s_sum = []
# for w in word_count.word:
#    i = 0
#    s_list = []
#    for t in title_clean_dist:
#       if w in t:
#          s_list.append(data.sales[i])
#       i+=1
#    w_s_sum.append(sum(s_list))     #list求和
   
# df_w_s_sum = pd.DataFrame({'w_s_sum': w_s_sum})  
 
# # 把 word_count 与对应的 df_w_s_sum 合并为一个表：
# df_word_sum = pd.concat([word_count,df_w_s_sum], axis=1,ignore_index = True)
# df_word_sum.columns = ['word','count','w_s_sum']     #添加列名 
 
 
 
# '''
# 对表df_word_sum 中的 word 和 w_s_sum 两列数据进行可视化： 见下<图3>
# （本例中取销量排名前30的词语进行绘图）
# '''
# df_word_sum.sort_values('w_s_sum',inplace=True,ascending=True)  #升序 
# df_w_s = df_word_sum.tail(30)     #取最大的30行数据
 
# import matplotlib
# from matplotlib import pyplot as plt
 
# font = {'family' : 'SimHei'}    #设置字体
# matplotlib.rc('font', **font)
 
# index = np.arange(df_w_s.word.size)
# plt.figure(figsize=(6,12))
# plt.barh(index, df_w_s.w_s_sum, color='purple', align='center', alpha=0.8) 
# plt.yticks(index, df_w_s.word, fontsize=11)                             
 
# # 添加数据标签：
# for y,x in zip(index , df_w_s.w_s_sum):
#    plt.text(x, y, '%.0f' %x , ha='left', va= 'center', fontsize=11)    
# plt.show()
 
# # va参数 ('top', 'bottom', 'center', 'baseline')
# # ha参数('center'， 'right'， 'left')
 
# '''
# 由图表可知：
# 1. 组合商品销量最高 ；
# 2. 从品类看：布艺沙发销量很高，远超过皮艺沙发；
# 3. 从户型看：小户型沙发销量最高，大小户型次之，大户型销量最少；
# 4. 从风格看：简约风销量最高，北欧风次之，其他依次是中式、美式、日式等；
# 5. 可拆洗、转角类沙发销量可观，也是颇受消费者青睐的。
# '''
 
 
 
 
# '''
# 【3】. 商品的价格分布情况分析：  见下<图4>
#    分析发现，有一些值太大，为了使可视化效果更加直观，这里我们结合自身产品情况，选择价格小于20000的商品。
# '''
# data_p = data[data['view_price'] < 20000]    
 
# plt.figure(figsize=(7,5))
# plt.hist(data_p['view_price'] ,bins=15 ,color='purple')   #分为15组  
# plt.xlabel('价格',fontsize=12)
# plt.ylabel('商品数量',fontsize=12)         
# plt.title('不同价格对应的商品数量分布',fontsize=15)  
# plt.show()
 
# '''
# 由图表可知：
# 1. 商品数量随着价格总体呈现下降阶梯形势，价格越高，在售的商品越少；
# 2. 低价位商品居多，价格在500-1500之间的商品最多，1500-3000之间的次之，价格1万以上的商品较少；
# 3. 价格1万元以上的商品，在售商品数量差异不大。https://xpanx.com/2099.html
# '''
 
 
 
 
# '''
# 【4】. 商品的销量分布情况分析：  见下<图5>
#    同样，为了使可视化效果更加直观，这里我们选择销量大于100的商品。
# '''
# data_s = data[data['sales'] > 100]    
# print('销量100以上的商品占比: %.3f' %(len(data_s)/len(data)))
 
# plt.figure(figsize=(7,5))
# plt.hist(data_s['sales'] ,bins=20 , color='purple')    #分为20组  
# plt.xlabel('销量', fontsize=12)
# plt.ylabel('商品数量', fontsize=12)         
# plt.title('不同销量对应的商品数量分布', fontsize=15)
# plt.show()
 
# '''
# 由图表及数据可知：
# 1. 销量100以上的商品仅占3.4% ，其中销量100-200之间的商品最多，200-300之间的次之；
# 2. 销量100-500之间，商品的数量随着销量呈现下降趋势，且趋势陡峭，低销量商品居多；
# 3. 销量500以上的商品很少。
# '''
 
 
 
 
# '''
# 【5】. 不同价格区间的商品的平均销量分布： 见下<图6>
#    代码如下：
# '''
# data['price'] = data.view_price.astype('int')   #转为整型  
 
# # 用 qcut 将price列分为12组
# data['group'] = pd.qcut(data.price, 12)         
# df_group = data.group.value_counts().reset_index()   #生成数据框并重设索引 
 
# # 以group列进行分类求sales的均值：
# df_s_g = data[['sales','group']].groupby('group').mean().reset_index()  
 
# # 绘柱形图：
# index = np.arange(df_s_g.group.size)
# plt.figure(figsize=(8,4))
# plt.bar(index, df_s_g.sales, color='purple')     
# plt.xticks(index, df_s_g.group, fontsize=11, rotation=30) 
# plt.xlabel('Group')
# plt.ylabel('mean_sales')
# plt.title('不同价格区间的商品的平均销量')
# plt.show()
 
# '''
# 由图表可知：
# 1. 价格在1331-1680之间的商品平均销量最高，951-1331之间的次之，9684元以上的最低；
# 2. 总体呈现先增后减的趋势，但最高峰处于相对低价位阶段；
# 3. 说明广大消费者对购买沙发的需求更多处于低价位阶段，在1680元以上 价位越高 平均销量基本是越少。
# '''
 
 
 
 
# '''
# 【6】. 商品价格对销量的影响分析： 见下<图7>
#    同上，为了使可视化效果更加直观，这里我们结合自身产品情况，选择价格小于20000的商品。
#    代码如下：
# '''
# fig, ax = plt.subplots(figsize=(8,5))    
# ax.scatter(data_p['view_price'], data_p['sales'],color='purple')
# ax.set_xlabel('价格')
# ax.set_ylabel('销量')
# ax.set_title('商品价格对销量的影响',fontsize=14)
# plt.show()
 
# '''
# 由图表可知：
# 1. 总体趋势：随着商品价格增多 其销量减少，商品价格对其销量影响很大；
# 2. 价格500-2500之间的少数商品销量冲的很高，价格2500-5000之间的商品少数相对较高，多数销量偏低，
# 但价格5000以上的商品销量均很低 没有销量突出的商品。
# '''
 
 
 
# '''
# 【7】. 商品价格对销售额的影响分析： 见下<图8>
#    代码如下：
# '''
# data['GMV'] = data['price'] * data['sales']
 
# import seaborn as sns
# sns.regplot(x="price",y='GMV',data=data,color='purple')  
 
# '''
# 由图表可知：
# 1. 总体趋势：由线性回归拟合线可以看出，商品销售额随着价格增长呈现上升趋势；
# 2. 多数商品的价格偏低，销售额也偏低；https://xpanx.com/2099.html
# 3. 价格在0-20000的商品只有少数销售额较高，价格2万-6万的商品只有3个销售额较高，
#    价格6-10万的商品有1个销售额很高，而且是最大值。
# '''
 
 
 
 
# '''
# 【8】. 不同省份的商品数量分布： 见下<图9>
#    代码如下：
# '''  
# plt.figure(figsize=(8,4))
# data.province.value_counts().plot(kind='bar',color='purple')
# plt.xticks(rotation= 0)       
# plt.xlabel('省份')
# plt.ylabel('数量')
# plt.title('不同省份的商品数量分布')
# plt.show()
 
# '''
# 由图表可知：
# 1. 广东的最多，上海次之，江苏第三，尤其是广东的数量远超过江苏、浙江、上海等地，
#    说明在沙发这个子类目，广东的店铺占主导地位；
# 2. 江浙沪等地的数量差异不大，基本相当。
# '''
 
 
 
 
# '''
# 【9】. 不同省份的商品平均销量分布： 见<图10、11>
#    代码如下：
# ''' 
# pro_sales = data.pivot_table(index = 'province', values = 'sales', aggfunc=np.mean)    #分类求均值
# pro_sales.sort_values('sales', inplace = True, ascending = False)    #排序
# pro_sales = pro_sales.reset_index()     #重设索引
 
# index = np.arange(pro_sales.sales.size)
# plt.figure(figsize=(8,4))
# plt.bar(index, pro_sales.sales, color='purple') 
# plt.xticks(index, pro_sales.province, fontsize=11, rotation=0)
# plt.xlabel('province')
# plt.ylabel('mean_sales')
# plt.title('不同省份的商品平均销量分布')
# plt.show()
 
# pro_sales.to_excel('pro_sales.xlsx', index = False)   #导出数据 并绘制热力型地图
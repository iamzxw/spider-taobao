import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Map

key = '帽子'
GOODS_EXCEL_PATH = f'./data/sales_data_{key}.xlsx'
GOODS_STANDARD_EXCEL_PATH = f'./data/sales_data_{key}_standard.xlsx'

DF_STANDARD = pd.read_excel(GOODS_STANDARD_EXCEL_PATH)


def standard_data():
    df = pd.read_excel(GOODS_EXCEL_PATH)
    # 1、将价格转化为整数型
    raw_sales = df['view_sales'].values
    new_sales = []
    for sales in raw_sales:
        sales = sales[:-3]
        sales = sales.replace('+', '')
        if '万' in sales:
            sales = sales[:-1]
            if '.' in sales:
                sales = sales.replace('.', '') + '000'
            else:
                sales = sales + '0000'
        sales = int(sales)
        new_sales.append(sales)
    df['view_sales'] = new_sales
    print(df['view_sales'].values)

    # 2、将地区转化为只包含省
    raw_location = df['item_loc'].values
    new_location = []
    for location in raw_location:
        if ' ' in location:
            location = location[:location.find(' ')]
        new_location.append(location)
    # df.location与df[location]效果类似
    df['item_loc'] = new_location
    print(df['item_loc'].values)

    # 3、生成新的excel
    writer = pd.ExcelWriter(GOODS_STANDARD_EXCEL_PATH)
    # columns参数用于指定生成的excel中列的顺序
    columns = ['raw_title', 'view_price', 'item_loc', 'view_sales', 'pic_url', 'nick', 'detail_url', 'comment_url',
               'comment_count']
    df.to_excel(excel_writer=writer, columns=columns, index=False,
                encoding='utf-8', sheet_name='Sheet')
    writer.save()
    writer.close()


def analysis_price():
    """
    分析商品价格
    :return:
    """
    # 引入全局数据
    global DF_STANDARD

    # 设置切分区域
    price_list_bins = [0, 20, 40, 60, 80, 100, 120, 150, 200, 1000000]
    # 设置切分后对应标签
    price_list_labels = ['0-20', '21-40', '41-60', '61-80', '81-100', '101-120', '121-150', '151-200', '200以上']
    # 分区统计
    price_count = cut_and_sort_data(price_list_bins, price_list_labels, DF_STANDARD['view_price'])
    print(price_count)
    # 生成柱状图
    bar = (
        Bar()
            .add_xaxis(list(price_count.keys()))
            .add_yaxis("", list(price_count.values()))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{key}商品价格区间分布柱状体"),
            yaxis_opts=opts.AxisOpts(name="个商品"),
            xaxis_opts=opts.AxisOpts(name="商品售价：元")
        )
    )
    bar.render('price-bar.html')
    # 生成饼图
    age_count_list = [list(z) for z in zip(price_count.keys(), price_count.values())]
    pie = (
        Pie()
            .add("", age_count_list)
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{key}商品价格区间饼图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    pie.render('price-pie.html')


def analysis_sales():
    """
    销量情况分布
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    # 设置切分区域
    listBins = [0, 1000, 5000, 10000, 50000, 100000, 1000000]
    # 设置切分后对应标签
    listLabels = ['一千以内', '一千到五千', '五千到一万', '一万到五万', '五万到十万', '十万以上']
    # 分区统计
    sales_count = cut_and_sort_data(listBins, listLabels, DF_STANDARD['view_sales'])
    print(sales_count)
    # 生成柱状图
    bar = (
        Bar()
            .add_xaxis(list(sales_count.keys()))
            .add_yaxis("", list(sales_count.values()))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{key}商品销量区间分布柱状图"),
            yaxis_opts=opts.AxisOpts(name="个商品"),
            xaxis_opts=opts.AxisOpts(name="销售件数")
        )
    )
    bar.render('sales-bar.html')
    # 生成饼图
    age_count_list = [list(z) for z in zip(sales_count.keys(), sales_count.values())]
    pie = (
        Pie()
            .add("", age_count_list)
            .set_global_opts(title_opts=opts.TitleOpts(title=f"{key}商品销量区间饼图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    pie.render('sales-pie.html')


def analysis_price_sales():
    """
    商品价格与销量关系分析
    :return:
    """
    # 引入全局数据
    global DF_STANDARD
    df = DF_STANDARD.copy()
    df['group'] = pd.qcut(df['view_price'], 12)
    df.group.value_counts().reset_index()
    df_group_sales = df[['view_sales', 'group']].groupby('group').mean().reset_index()
    df_group_str = [str(i) for i in df_group_sales['group']]
    print(df_group_str)
    # 生成柱状图
    bar = (
        Bar()
            .add_xaxis(df_group_str)
            .add_yaxis("", list(df_group_sales['view_sales']), category_gap="50%")
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{key}商品价格分区与平均销量柱状图"),
            yaxis_opts=opts.AxisOpts(name="价格区间"),
            xaxis_opts=opts.AxisOpts(name="平均销量", axislabel_opts={"rotate": 30})
        )
    )
    bar.render('price-sales-bar.html')


def cut_and_sort_data(listBins, listLabels, data_list) -> dict:
    """
    统计list中的元素个数，返回元素和count
    :param listBins: 数据切分区域
    :param listLabels: 切分后对应标签
    :param data_list: 数据列表形式
    :return: key为元素value为count的dict
    """
    data_labels_list = pd.cut(data_list, bins=listBins, labels=listLabels, include_lowest=True)
    # 生成一个以listLabels为顺序的字典，这样就不需要后面重新排序
    data_count = {i: 0 for i in listLabels}
    # 统计结果
    for value in data_labels_list:
        # get(value, num)函数的作用是获取字典中value对应的键值, num=0指示初始值大小。
        data_count[value] = data_count.get(value) + 1
    return data_count


def analysis_province_sales():
    """
    省份与销量的分布
    :return:
    """
    # 引入全局数据
    global DF_STANDARD

    # 1、全国商家数量分布
    province_sales = DF_STANDARD['item_loc'].value_counts()
    province_sales_list = [list(item) for item in province_sales.items()]
    print(province_sales_list)
    # 1.1 生成热力图
    province_sales_map = (
        Map()
            .add(f"{key}商家数量全国分布图", province_sales_list, "china")
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(max_=647),
        )
    )
    province_sales_map.render('province-seller-map.html')
    # 1.2 生成柱状图
    province_sales_bar = (
        Bar()
            .add_xaxis(province_sales.index.tolist())
            .add_yaxis("", province_sales.values.tolist(), category_gap="50%")
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{key}商家数量地区柱状图"),
            yaxis_opts=opts.AxisOpts(name="商家数量"),
            xaxis_opts=opts.AxisOpts(name="地区", axislabel_opts={"rotate": 90})
        )
    )
    province_sales_bar.render('province-seller-bar.html')

    # 3、全国商家省份平均销量分布
    province_sales_mean = DF_STANDARD.pivot_table(index='item_loc', values='view_sales', aggfunc=np.mean)
    # 根据平均销量排序
    province_sales_mean.sort_values('view_sales', inplace=True, ascending=False)
    province_sales_mean_list = [list(item) for item in
                                zip(province_sales_mean.index, np.ravel(province_sales_mean.values))]

    print(province_sales_mean_list)
    # 3.1 生成热力图
    province_sales_mean_map = (
        Map()
            .add(f"{key}商家平均销量全国分布图", province_sales_mean_list, "china")
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(max_=1536),
        )
    )
    province_sales_mean_map.render('province-sales-mean-map.html')
    # 3.2 生成柱状图
    province_sales_mean_bar = (
        Bar()
            .add_xaxis(province_sales_mean.index.tolist())
            .add_yaxis("", list(map(int, np.ravel(province_sales_mean.values))), category_gap="50%")
            .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{key}各省商家平均销量地区柱状图"),
            yaxis_opts=opts.AxisOpts(name="平均销量"),
            xaxis_opts=opts.AxisOpts(name="地区", axislabel_opts={"rotate": 90})
        )
    )
    province_sales_mean_bar.render('province-sales-mean-bar.html')


if __name__ == '__main__':
    # 数据清洗
    standard_data()
    # 数据分析
    # analysis_price()
    # analysis_sales()
    # analysis_price_sales()
    # analysis_province_sales()
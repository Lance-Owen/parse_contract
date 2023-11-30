'''
pip install pipreqs
pipreqs . --encoding=utf8 --force
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
'''
import datetime
import hashlib
import os
import re
import shutil
from datetime import datetime
from threading import RLock

import cv2
import numpy as np
import pandas as pd
import pymysql
from dbutils.persistent_db import PersistentDB
from docx import Document
from paddleocr import PaddleOCR, PPStructure, save_structure_res
from pdf2image import convert_from_path

field_contrast = {"材料名称": "materialName",
                  "型号": "module",
                  "单位": "unit",
                  "数量": "number",
                  "含税价格": "taxPrice",
                  "不含税价格": "noTaxPrice",
                  "含增值税价格": "addTaxPrice",
                  "不含增值税价格": "noAddTaxPrice",
                  "签订时间": "signDate"}


def generate_md5(s):
    """
    字符串生成哈希值
    :param s:
    :return:
    """
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def pyMuPDF_fitz(pdfPath, imagePath):
    # images = convert_from_path(pdfPath, poppler_path="E:\\Release-23.11.0-0\\poppler-23.11.0\\Library\\bin")
    images = convert_from_path(pdfPath, poppler_path=r"poppler-23.11.0\\Library\\bin")

    # 保存图片到指定文件夹
    for i, image in enumerate(images):
        direng = f"{imagePath}"
        if not os.path.exists(direng):
            os.makedirs(direng)
        image.save(f'{imagePath}/output_{i}.png', 'PNG')

def clean_num(s):
    s = str(s)
    num = re.findall("\d*\.?\d{0,2}", s)
    num = [s for s in num if s]
    if num:
        return num[0]
    return 0

def gci(project_name, file):
    """
    传入项目名称和文件，根据文件后缀分流，进行处理
    :param project_name:
    :param file:
    :return:
    """
    # if file != r"合同\338 大英县旅游基础设施（一期）建设项目三标段\砂石运输\大英县旅游基础设施（一期）建设项目三标段砂石运输合同补充协议.pdf":
    #     return ''
    print('处理文件分割线'.center(100, '*'))
    print(file)
    file_path = file.replace("\\", "/")
    if len(mysql_select_df(f"select filePath from material where filePath='{file_path}'")) > 0:
        print(f'文件已处理完成：{file}')
        return ""
    # 解析到的材料数据存放路径
    output_path = os.path.join('output', project_name, os.path.split(file)[-1].split(".")[0])
    # 创建存放路径在output文件夹中，下级目录项目名称，下级目录文件名称
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 处理pdf文件
    if file.endswith(".pdf"):
        if os.path.exists(file.replace(".pdf", ".doc")) or os.path.exists(file.replace(".pdf", ".docx")):
            print("存在word文件，不进行pdf解析")
            return ""
        # image存放路径
        img_path = os.path.join('imgs', project_name, os.path.split(file)[-1].split(".")[0])
        # pdf生成图片
        pyMuPDF_fitz(file, img_path)
        # 清空临时输出文件
        if os.path.exists('test'):
            shutil.rmtree('test')
        # 解析pdf表格
        df = getTables(img_path, output_path)
    elif '.doc' in file:
        # return ''
        # doc文件和docx文件采用同一种处理方式
        df = gettable_doc(output_path, file)
    else:
        print(f"数据未处理：{file}")
        return ''

    """
    清洗数据入库
    """
    if len(df) != 0:
        # df = df.fillna('')
        df['projectName'] = project_name
        df['filePath'] = file_path
        df['createTime'] = datetime.now()
        df['updateTime'] = datetime.now()
        df = df.drop_duplicates()

        try:
            df['md5'] = df.apply(lambda row: generate_md5(project_name + row['materialName'] + row['module']), axis=1)
        except Exception as e:
            print(f"error:容差性错误,不存在规格字段{e}")
            df['md5'] = df.apply(lambda row: generate_md5(project_name + row['materialName']), axis=1)
        for col in df.columns:
            if col in ['number', 'taxPrice', 'noTaxPrice', 'addTaxPrice', 'noAddTaxPrice']:
                df[col] = df[col].apply(lambda cell: clean_num(cell))
        print(df)
        mysql_insert_data(df, 'material')


def clean_output():
    for file in os.listdir("test"):
        if ".xlsx" in file:
            file_name = os.path.join("test", file)
            df = pd.read_excel(file_name).fillna("")
            title = df.columns.tolist()
            for s in title:
                if re.findall("单价", re.sub(",|\s", "", str(s))):
                    table = [title] + df.values.tolist()
                    for i in range(len(table)):
                        if re.findall('合计', "".join([str(s) for s in table[i]])):
                            table = table[:i]
                            break
                    table = clean_data(table)
                    df = pd.DataFrame(data=table[1:], columns=table[0])
                    return df
    return pd.DataFrame()


def clean_data(table):
    """
    清洗价格表
    :param table:
    :return:
    """
    name_index = []
    title = []
    # 匹配指定名称的表头，获取索引，并重设表头
    for s in table[0]:
        # 在匹配表头数据之前，替换掉换行和空格字符
        deal_s = re.sub(",|\s", "", s)
        # 匹配对应字段的位置，生成字段和字段索引两个列表
        if re.findall('名称', deal_s) and '材料名称' not in title:
            name_index.append(table[0].index(s))
            title.append('材料名称')
        elif re.findall("规格|型号", deal_s) and '型号' not in title:
            name_index.append(table[0].index(s))
            title.append('型号')
        elif re.findall("单位", deal_s) and '单位' not in title:
            name_index.append(table[0].index(s))
            title.append('单位')
        elif re.findall("数量", deal_s) and '数量' not in title:
            name_index.append(table[0].index(s))
            title.append('数量')
        elif re.findall("单价",deal_s):
            if re.findall("不含增值税价格|不含增值税", deal_s) and '不含增值税价格' not in title:
                name_index.append(table[0].index(s))
                title.append('不含增值税价格')
            elif re.findall("含增值税价格|含增值税", deal_s) and '含增值税价格' not in title:
                name_index.append(table[0].index(s))
                title.append('含增值税价格')
            elif re.findall("不含税价格|不含税", deal_s) and '不含税价格' not in title:
                name_index.append(table[0].index(s))
                title.append('不含税价格')
            elif re.findall("含税价格|含税", deal_s) and '含税价格' not in title:
                name_index.append(table[0].index(s))
                title.append('含税价格')
    # 获取指定列数据
    result_table = []
    for row in table[1:]:
        try:
            # 判断合并表格，脏数据
            if len(set(row)) == 1:
                continue
            # 生成行，并添加对应位置数据
            result_table.append([])
            for idx in name_index:
                result_table[-1].append(row[idx])
        except Exception as e:
            print(f"error:{e}，{row}")
    # 返回清洗以后的表格数据
    return [title] + result_table


def d_date_clean(value):
    """
    一般日期处理
    """
    value = re.findall(r'\d+', value)
    if value:
        # 如果第一位不是年
        if len(value[0]) != 4:
            year = datetime.datetime.now().strftime('%Y')
            # 如果年是两位数
            if len(value[0]) == 2 and int(value[0]) > 12:
                value[0] = '20' + value[0]
            else:
                # 第一位是月份
                value.insert(0, year)
        if len(value) < 6:
            for i in range(6 - len(value)):
                value.append(0)
        # 全部转换成数字
        value = [int(i) for i in value]
        # 如果24点
        if value[3] == 24:
            value[3] = 23
            value[4] = 59
            value[5] = 59
        try:
            value = datetime(value[0], value[1], value[2], value[3], value[4], value[5])
            # 转换成标准时间格式
            # value = value.strftime('%Y-%m-%d %H:%M:%S')
        except:
            value = ''
        return value


def getTables(img_dir, output_path):
    result_time = datetime.strptime('1900-01-01', "%Y-%m-%d")
    df = pd.DataFrame()
    # 遍历图片
    for img in os.listdir(img_dir):
        img_path = os.path.join(img_dir, img)
        table_engine = PPStructure(show_log=False)
        # img = cv2.imread(img_path)
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
        result = table_engine(img)
        save_structure_res(result, "./", "test")
        if len(clean_output()) > 0:
            df = clean_output()
        # new_name = os.path.join(output_path, f'pdf.xlsx')

        # 文字识别
        ocr = PaddleOCR(use_angle_cls=False,
                        lang="ch")  # need to run only once to download and load model into memory
        result = ocr.ocr(img_path, cls=False)
        res = result[0]  # 因为只有一张图片，所以结果只有1个，直接取出
        # 解析时间
        if res:
            # 拼接文本
            page_text = "".join([r[-1][0] for r in res])
            # 根据规则找到可能匹配的文本
            time_strs = re.findall("[原签订合同合约日期时间：：]{5,}.{8,15}?[日号]", re.sub("\s", "", page_text))
            # 针对匹配到的时间进行清洗
            if time_strs:
                for time_str in time_strs:
                    # 去除了数字和时间之外的任何字符
                    time_str = re.sub("[^\d年月]", "", time_str)
                    # 清洗转换为事件类型
                    sign_date = d_date_clean(time_str)
                    # 找到最大的时间
                    if sign_date and sign_date > result_time:
                        result_time = sign_date
                        print(result_time)
        # 判断是否存在材料单价表
        if len(df) != 0:
            # 判断是否解析到时间
            if result_time != datetime.strptime('1900-01-01', "%Y-%m-%d"):
                print(result_time)
                # 添加时间字段
                df['签订时间'] = result_time
            # 字段重命名,替换为数据库对应字段
            df = df.rename(columns=field_contrast)
            # 存放到对应输出文件夹
            df.to_excel(os.path.join(output_path, f'pdf.xlsx'), index=False)
            return df
    return pd.DataFrame()


def gettable_doc(output_path, file):
    # 打开.doc文件
    doc = Document(file)
    # 拼接所有段落文本数据
    text = "".join([para.text for para in doc.paragraphs])
    time_strs = re.findall("[原签订合同合约日期时间：：]{5,}.{8,15}?[日号]", re.sub("\s", "", text))
    if time_strs:
        result_time = datetime.strptime('1900-01-01', "%Y-%m-%d")
        for time_str in time_strs:
            time_str = re.sub("[^\d年月]", "", time_str)
            sign_date = d_date_clean(time_str)
            if sign_date and sign_date > result_time:
                result_time = sign_date
        if result_time == datetime.strptime('1900-01-01', "%Y-%m-%d"):
            result_time = ''
        print(result_time)
    else:
        result_time = ''
    # 遍历文档的表格
    for table in doc.tables:
        table = [[cell.text for cell in row.cells if cell] for row in table.rows]
        for s in table[0]:
            if re.findall("单价", re.sub(",|\s", "", str(s))):
                for i in range(len(table)):
                    if [re.findall('合计', s) for s in table[i] if '合计' in table[i]]:
                        table = table[:i]
                        table = clean_data(table)
                        df = pd.DataFrame(data=table[1:], columns=table[0])
                        if result_time:
                            df['签订时间'] = result_time
                        df = df.rename(columns=field_contrast)
                        df.to_excel(os.path.join(output_path, f'doc.xlsx'), index=False)
                        return df
    return pd.DataFrame()


def match_file(file_name):
    if os.path.isdir(file_name):
        for file in os.listdir(file_name):
            if os.path.isdir(os.path.join(file_name, file)):
                match_file(os.path.join(file_name, file))
            else:
                print(file)


def mysql_connect(config='mysql'):
    """
    连接数据库
    """
    db = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='631314',
        db='sf_data',
        charset='utf8',
    )
    return db


db = mysql_connect()


def mysql_connect_pool(config='mysql'):
    pool = PersistentDB(
        pymysql,
        5,
        host='localhost',
        port=3306,
        user='root',
        passwd='631314',
        db='sf_data',
        charset='utf8',
        setsession=['SET AUTOCOMMIT = 1']
    )

    return pool


pool = mysql_connect_pool()

conn = pool.connection()

LOCK = RLock()


def mysql_insert_data(df, table):
    """
    使用df的表头和数据拼成批量更新的sql语句
    """
    sql = 'insert into {} ({}) values ({})'.format(table, ','.join(df.columns), ','.join(['%s'] * len(df.columns)))

    values = df.values.tolist()
    # 将NaT 替换成 ''
    for i in range(len(values)):
        for j in range(len(values[i])):
            if pd.isnull(values[i][j]):
                values[i][j] = None
    with LOCK:
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, values)
        except:
            for value in values:
                try:
                    cursor.execute(sql, value)
                except Exception as e:
                    error = {'error': e, 'value': value[0], 'table': table}
                    print(error)
        db.commit()
        cursor.close()


def mysql_select_df(sql):
    """
    执行sql，返回的数据转换成dataframe，并且表头是列名
    """
    import pandas as pd
    with LOCK:
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
    df = pd.DataFrame(data)
    try:
        df.columns = [i[0] for i in cursor.description]
    except:
        # 为空
        pass
    return df


if __name__ == '__main__':
    # 项目
    pass

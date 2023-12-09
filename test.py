# 文件归档处理
from parse_utils import *
import re
from mysql_utils import *

df1 = pd.read_excel(r"C:\Users\pc\Desktop\建筑工程文档归档.xlsx")
df1['工程类型'] = 1
df2 = pd.read_excel(r"C:\Users\pc\Desktop\道路工程文档归档.xlsx")
df2['工程类型'] = 2
df3 = pd.read_excel(r"C:\Users\pc\Desktop\桥梁工程文档归档.xlsx")
df3['工程类型'] = 3
df4 = pd.read_excel(r"C:\Users\pc\Desktop\地下管线工程文档归档.xlsx")
df4['工程类型'] = 4

field_contrast = {"一级分类": "first_heading",
                  "二级分类": "second_heading",
                  "建设单位": "construction_unit",
                  "设计单位": "design_unit",
                  "施工单位": "build_unit",
                  "监理单位": "supervision_unit",
                  "城建党建馆": "city_party_building",
                  "工程类型": "project_type"
                  }

def deal_data(df):
    data = df.values.tolist()
    for i in range(len(data)):
        if re.findall('[A-Za-z]', str(data[i][0])):
            text = data[i][1]
            continue
        data[i][0] = text

    data_df = pd.DataFrame(data=data, columns=df.columns.tolist())
    data_df['二级分类'] = data_df['二级分类'].fillna('')
    data_df = data_df.fillna(0)
    print(len(data_df))
    data_df = data_df[~data_df['一级分类'].astype(str).str.contains(regex=True, pat='[A-Z]+\d+')]
    print(len(data_df))
    data_df['id'] = data_df.apply(lambda row:generate_md5(row['一级分类']+row['二级分类']+str(row['工程类型'])),axis=1)
    data_df = data_df.rename(columns=field_contrast)
    mysql_insert_data(data_df,'file_archiving_rules')

deal_data(df1)
deal_data(df2)
deal_data(df3)
deal_data(df4)
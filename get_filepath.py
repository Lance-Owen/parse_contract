"""
统计所有合同文件的文件名

"""


from parse_utils import *
path = r'\\192.168.180.180\7.信合源-综合\03业绩资料'

path = list_files_in_directory_recursive(path)

df = pd.DataFrame({'filePath':path},columns=['filePath'])
df['id'] = df['filePath'].apply(generate_md5)
df['file'] = df['filePath'].apply(lambda s: s.split("\\")[-1])

mysql_insert_data(df,'file_path')
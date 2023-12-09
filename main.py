# -*- coding: utf-8 -*-
"""
python版本
python 3.9.4

打包纯净依赖
pip install pipreqs
pipreqs . --encoding=utf8 --force
安装依赖
pip install -r .\requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


"""

from parse_contract_process import *
from multiprocessing import Pool
import os




def list_files_in_directory_recursive(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list

if __name__ == "__main__":
    # path = input("请输入合同文件夹: ")
    # 获取所有图像文件的路径
    path = r'\\192.168.180.180\13.平台-财务\平台公司共享'
    file_list = list_files_in_directory_recursive(path)
    process_file_list = []
    process_project_list = []
    for file in file_list:
        if '\\合同扫描件\\' in file and file.endswith('.pdf'):
            project_name = file.split("\\合同扫描件\\")[-1].split("\\")[1]
            project_name = re.findall("\d*\s*(.*)", project_name)[0]
            if '终止' in os.path.split(file)[-1] or '解除' in os.path.split(file)[-1]:
                # print(f'不处理文件：{file}')
                pass
            elif '合同' in os.path.split(file)[-1]:
                process_file_list.append(file)
                process_project_list.append(project_name)
                # print(f"处理文件：{file}")
                pass
            elif '补充' in os.path.split(file)[-1]:
                process_file_list.append(file)
                process_project_list.append(project_name)
                # print(f"处理文件：{file}")
                # pass
            elif '采购' in os.path.split(file)[-1] and not any(s in os.path.split(file)[-1] for s in ['审批表','出库','入库']):
                process_file_list.append(file)
                process_project_list.append(project_name)
                # print(f"处理文件：{file}")
                pass
            else:
                # print(f"判断文件：{file}")
                pass
    # for project_name,file in zip(process_project_list,process_file_list):
    #     gci(project_name,file)
    # # 10m
    # 使用进程池加速处理
    with Pool() as pool:
        # 提交任务，每个图像一个任务，传递两个参数
        pool.starmap(gci, list(zip(process_project_list, process_file_list)))



    # # # 创建线程
    # threads = []
    # for project_name,file in list(zip(process_project_list[:10],process_file_list[:10])):
    #     thread = threading.Thread(target=gci, args=(project_name, file))
    #     threads.append(thread)
    #     thread.start()
    #
    # # 等待所有线程完成
    # for thread in threads:
    #     thread.join()
    # 15m
        # 使用多进程池加速处理
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     # 提交任务，每个图像一个任务，传递两个参数
    #     executor.map(gci, project_list, file_list)
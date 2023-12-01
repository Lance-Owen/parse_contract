"""
python版本
python 3.9.4

打包纯净依赖
pip install pipreqs
pipreqs . --encoding=utf8 --force
安装依赖
pip install -r .\requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


"""




import concurrent.futures
from parse_contract_process import *
from multiprocessing import Pool
import threading


if __name__ == "__main__":
    path = input("请输入合同文件夹: ")
    # 获取所有图像文件的路径

    file_list = []
    project_list = []
    for file1 in os.listdir(path):
        path1 = os.path.join(path, file1)
        project_name = re.findall("[^\d\s].*", file1)[0]
        print(project_name)
        # 合同类别
        for file2 in os.listdir(path1):
            path2 = os.path.join(path1, file2)
            if os.path.isdir(path2):
                # 合同文件
                for file3 in os.listdir(path2):
                    path3 = os.path.join(path2, file3)
                    if not re.findall("分包|施工|检测|机械", path3) and '合同' in path3 and (
                            path3.endswith(".pdf") or path3.endswith(".docx")):
                        file_list.append(path3)
                        project_list.append(project_name)
                        # gci(project_name, path3)

            elif (not re.findall("分包|施工|检测|机械", path2)) and '合同' in path2 and (
                    path2.endswith(".pdf") or path2.endswith(".docx")):
                file_list.append(path2)
                project_list.append(project_name)
                # gci(project_name, path2)

    # 10m
    # 使用进程池加速处理
    with Pool() as pool:
        # 提交任务，每个图像一个任务，传递两个参数
        pool.starmap(gci, list(zip(project_list, file_list)))


    # # 创建线程
    # threads = []
    # for project_name,file in list(zip(project_list,file_list)):
    #     thread = threading.Thread(target=gci, args=(project_name, file))
    #     threads.append(thread)
    #     thread.start()
    # # 等待所有线程完成
    # for thread in threads:
    #     thread.join()
    # 15m
        # 使用多进程池加速处理
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     # 提交任务，每个图像一个任务，传递两个参数
    #     executor.map(gci, project_list, file_list)
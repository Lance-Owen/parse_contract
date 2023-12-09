
from parse_utils import *
import shutil
import os


path = r'\\192.168.180.180\7.信合源-综合\03业绩资料\5、信合源业绩扫描件\1、信合源\3、四川新诚电子新材料有限公司中高压电极箔项目'

file_list = list_files_in_directory_recursive(path)
# process_file_list = []
for file in file_list:
    if file.endswith('.pdf'):
        continue
        print('处理文件分割线'.center(100, '*'))
        print(file)
        file_name = os.path.split(file)
        if '施工合同' in file:
            print("该文件是施工合同！")
            continue
        elif '竣工报告' in file or '竣工验收报告' in file:
            print("该文件是：建设单位工程竣工报告")
        elif '项目建议书' in file:
            print("该文件是：项目建议书批复文件及项目建议书")
        elif '可行性研究报告' in file:
            print("该文件是：可行性研究报告批复文件及可行性研究报告")
        elif '' in file:
            print('该文件是：')
        elif '' in file:
            print('该文件是：')
        elif '' in file:
            print('该文件是：')
        elif '' in file:
            print('该文件是：')
        elif '' in file:
            print('该文件是：')
        process_file_list.append(file)
        imgs_file = os.path.join('imgs',os.path.split(file)[-1][:-4])
        if not os.path.exists(imgs_file):
            os.makedirs(imgs_file)

        pyMuPDF_fitz(file,imgs_file)
        for img in os.listdir(imgs_file):
            img_text = img_ocr(os.path.join(imgs_file,img))
            print('\n'.join(img_text))
        shutil.rmtree(imgs_file)

    elif file.endswith('.docx') and '~$' not in file:
        continue

        print('处理文件分割线'.center(100, '*'))
        print(file)
        print(parse_docx(file))
    elif file.endswith('.doc') and '~$' not in file:
        continue

        print('处理文件分割线'.center(100, '*'))
        print(file)
        text = parse_doc(file)
        print(text)

    elif file.endswith('.png') or file.endswith('.jpg'):
        continue
        print('处理文件分割线'.center(100, '*'))
        # 判断当前文件是否只有图片

        print(file)
        folder_path = os.path.split(file)[0]
        if folder_contains_only_images(folder_path):
            print(f"只有图片")

        else:
            print(f"包含非图片文件")
            print(img_ocr(file))
        pass

# print(os.listdir(r"\\192.168.180.180\7.信合源-综合\03业绩资料\5、信合源业绩扫描件\1、信合源\3、四川新诚电子新材料有限公司中高压电极箔项目\中高压电极箔业绩\竣工验收报告"))
a = dict()
a.items()



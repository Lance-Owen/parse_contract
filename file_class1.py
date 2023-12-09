
from parse_utils import *
import shutil
import os


path = r'\\192.168.180.180\7.信合源-综合\03业绩资料\5、信合源业绩扫描件\1、信合源\1、盐边县簸箕鲊一期居住小区Ⅰ、Ⅱ标段'

file_list = list_files_in_directory_recursive(path)
process_file_list = []


def parse_text(text):
    party_A = ""
    party_B = ""
    for s in text:
        if re.findall("[甲需方发包人]+.{0,5}[：:]([^,.，。，？！/\\ |]*)", s) and party_A == "":
            party_A = re.findall("[甲需方发包人]+.{0,5}[：:]([^,.，。，？！/\\ |]*)", s)[0]
            print(party_A)

        elif re.findall("[乙供方]*[承包人]*.{0,5}[：:]([^,.，。，？！/\\ |]*)", s) and party_B == "":
            party_B = re.findall("[乙供方承包人]+.{0,5}[：:]([^,.，。，？！/\\ |]*)", s)[0]
            print(party_B)



for file in file_list:
    if file != r"\\192.168.180.180\7.信合源-综合\03业绩资料\5、信合源业绩扫描件\1、信合源\1、盐边县簸箕鲊一期居住小区Ⅰ、Ⅱ标段\协议书（700000元）.pdf":
        continue
    if file.endswith('.pdf'):
        print('处理文件分割线'.center(100, '*'))
        print(file)
        file_name = os.path.split(file)

        imgs_file = os.path.join('imgs', os.path.split(file)[-1][:-4])
        if not os.path.exists(imgs_file):
            os.makedirs(imgs_file)

        pyMuPDF_fitz(file, imgs_file)
        text = []
        for img in os.listdir(imgs_file):
            img_text = img_ocr(os.path.join(imgs_file, img))
            text += img_text
        parse_text(text)

        shutil.rmtree(imgs_file)


    elif file.endswith('.docx') and '~$' not in file:
        print('处理文件分割线'.center(100, '*'))
        print(file)
        print(parse_docx(file))

    elif file.endswith('.doc') and '~$' not in file:
        print('处理文件分割线'.center(100, '*'))
        print(file)
        text = parse_doc(file)

    elif file.endswith('.png') or file.endswith('.jpg'):
        print('处理文件分割线'.center(100, '*'))
        # 判断当前文件是否只有图片
        print(file)
        text = img_ocr(file)


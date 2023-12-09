
import datetime
import hashlib
import re

import cpca
import fitz
from PIL import Image
from docx import Document
from paddleocr import PaddleOCR
from reportlab.pdfgen import canvas

from mysql_utils import *
import win32com.client


def list_files_in_directory_recursive(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != 'Thumbs.db' and '~$' not in file:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    return file_list


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
    """
    将pdf文件按页切分为图片
    """
    # images = convert_from_path(pdfPath, poppler_path="E:\\Release-23.11.0-0\\poppler-23.11.0\\Library\\bin")
    # images = convert_from_path(pdfPath, poppler_path=r"poppler-23.11.0\\Library\\bin")

    with fitz.open(pdfPath) as pdf:
        for pg in range(0, len(pdf)):
            page = pdf[pg]
            mat = fitz.Matrix(2, 2)
            pm = page.get_pixmap(matrix=mat, alpha=False)
            if pm.width > 2000 or pm.height > 2000:
                pm = page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
                os.makedirs(imagePath)  # 若图片文件夹不存在就创建

            pm.save(imagePath + '/' + '%s.jpg' % pg)  # 将图片写入指定的文件夹内


def clean_num(s):
    s = str(s)
    num = re.findall("\d*\.?\d{0,2}", s)
    num = [s for s in num if s]
    if num:
        return num[0]
    return 0


def d_date_clean(value):
    """
    一般日期处理
    """
    value = re.findall(r'\d+', value)
    if value:
        # 如果第一位不是年
        if len(value[0]) != 4:
            year = datetime.now().strftime('%Y')
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
        except:
            value = ''
        return value


def img_ocr(img_path):
    ocr = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, use_gpu=True)
    result = ocr.ocr(img_path, cls=False)
    res = result[0]  # 因为只有一张图片，所以结果只有1个，直接取出
    # 解析时间
    if res:
        img_text = [r[-1][0] for r in res]
    else:
        img_text = []
    return img_text


def parse_docx(file_path):
    doc = Document(file_path)
    # 拼接所有段落文本数据
    text = "".join([para.text for para in doc.paragraphs])
    return text


def parse_doc(file_path):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(file_path)
    content = doc.Content.Text
    doc.Close()
    word.Quit()
    content = content.encode('utf-8').decode('utf-8')
    return re.sub(r'\\[xX]\d*|\\r', '', repr(content))


def parse_address(address):
    address_info = cpca.transform([address])
    if len(address_info) > 0:
        province, city, county = address_info.values.tolist()[0][:3]
    return province, city, county


def combine2Pdf(folderPath, pdfFilePath):
    files = os.listdir(folderPath)
    pngFiles = []
    sources = []
    for file in files:
        if 'png' in file:
            pngFiles.append(folderPath + file)
    pngFiles.sort()
    output = Image.open(pngFiles[0])
    pngFiles.pop(0)
    for file in pngFiles:
        pngFile = Image.open(file)
        if pngFile.mode == "RGB":
            pngFile = pngFile.convert("RGB")
        sources.append(pngFile)
    output.save(pdfFilePath, "pdf", save_all=True, append_images=sources)


def merge_images_to_pdf(input_folder, output_pdf):
    # 获取输入文件夹中的所有文件和子文件夹
    files_and_folders = os.listdir(input_folder)
    # 创建一个PDF文件
    pdf = canvas.Canvas(output_pdf)
    for item in files_and_folders:
        item_path = os.path.join(input_folder, item)
        if os.path.isfile(item_path) and item.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 如果是图片文件，将其添加到PDF中
            image = Image.open(item_path)
            # 获取图片的宽度和高度
            img_width, img_height = image.size
            # 获取PDF页面的宽度和高度
            pdf_width, pdf_height = pdf._pagesize
            # 计算缩放比例
            scale_factor = min(pdf_width / img_width, pdf_height / img_height)
            # 计算图片在PDF中的位置
            x_offset = (pdf_width - img_width * scale_factor) / 2
            y_offset = (pdf_height - img_height * scale_factor) / 2
            # 缩放并添加图片到PDF
            pdf.drawInlineImage(image, x_offset, y_offset, width=img_width * scale_factor,
                                height=img_height * scale_factor)
            pdf.showPage()
        elif os.path.isdir(item_path):
            # 如果是子文件夹，递归处理
            merge_images_to_pdf(item_path, output_pdf)
    # 保存PDF文件
    pdf.save()


def is_image_file(file_path):
    """
    判断文件夹内是否只包含图片文件
    """
    try:
        with Image.open(file_path):
            return True
    except:
        return False

def folder_contains_only_images(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename != 'Thumbs.db' and not is_image_file(file_path):
            return False
    return True


if __name__ == '__main__':
    pass

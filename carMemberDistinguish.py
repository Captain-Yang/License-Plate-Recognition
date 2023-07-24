from PIL import Image
import pytesseract
def get_bin_table(threshold = 200):
    # 获取灰度转二值的映射table
    table = []
    for i in range(256):
        if i < threshold:
            table.append(1)
        else:
            table.append(0)
    return table

# image = Image.open("split_img/1.jpg")
image = Image.open("color.jpg")
imgry = image.convert('L')  # 转化为灰度图
table = get_bin_table()
out = imgry.point(table, '1')
out.save("test_color.jpg")

text = pytesseract.image_to_string(out)#lang='chi_sim'
# text = pytesseract.image_to_string(out, config='digits')
#text = pytesseract.im
# # 去除数字以外的其他字符
# fil = filter(str.isdigit, text)
# new_text = ''
# for i in fil:
#     new_text += i
# print(new_text)
print(text)
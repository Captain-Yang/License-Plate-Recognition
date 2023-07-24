#!/usr/bin/env python
# -*- coding:utf-8 -*-
import cv2
import numpy as np
from skimage import io

MAX_WIDTH = 1000  # 原始图片最大宽度
MAX_HIGH = 1000  # 原始图片最大宽度


def point_limit(point):
    if point[0] < 0:
        point[0] = 0
    if point[1] < 0:
        point[1] = 0


def accurate_place(card_img_hsv, limit1, limit2, color):
    row_num, col_num = card_img_hsv.shape[:2]
    xl = col_num
    xr = 0
    yh = 0
    yl = row_num
    # col_num_limit = self.cfg["col_num_limit"]
    row_num_limit = 10
    col_num_limit = col_num * 0.8 if color != "green" else col_num * 0.5  # 绿色有渐变
    for i in range(row_num):
        count = 0
        for j in range(col_num):
            H = card_img_hsv.item(i, j, 0)
            S = card_img_hsv.item(i, j, 1)
            V = card_img_hsv.item(i, j, 2)
            if limit1 < H <= limit2 and 34 < S and 46 < V:
                count += 1
        if count > col_num_limit:
            if yl > i:
                yl = i
            if yh < i:
                yh = i
    for j in range(col_num):
        count = 0
        for i in range(row_num):
            H = card_img_hsv.item(i, j, 0)
            S = card_img_hsv.item(i, j, 1)
            V = card_img_hsv.item(i, j, 2)
            if limit1 < H <= limit2 and 34 < S and 46 < V:
                count += 1
        if count > row_num - row_num_limit:
            if xl > j:
                xl = j
            if xr < j:
                xr = j
    return xl, xr, yh, yl


def find_end(start, arg, black, white, width, black_max, white_max):
    end = start + 1
    for m in range(start + 1, width - 1):
        if (black[m] if arg else white[m]) > (0.95 * black_max if arg else 0.95 * white_max):
            end = m
            break
    return end


def predict(src,destination):
    # 读取图片
    rawImage = cv2.imread(src)

    pic_hight, pic_width = rawImage.shape[:2]  # 获取图片大小
    if pic_width > MAX_WIDTH:  # 限制大小
        resize_rate = MAX_WIDTH / pic_width
        rawImage = cv2.resize(rawImage, (MAX_WIDTH, int(pic_hight * resize_rate)),
                              interpolation=cv2.INTER_AREA)  # 局部重采样

    if pic_hight > MAX_HIGH:  # 限制大小
        resize_rate = MAX_HIGH / pic_hight
        cv2.resize(rawImage, (int(pic_width * resize_rate), MAX_HIGH), interpolation=cv2.INTER_AREA)  # 局部重采样
    image = rawImage.copy()
    # 高斯模糊，将图片平滑化，去掉干扰的噪声
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # 图片灰度化
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Sobel算子（X方向）
    Sobel_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
    # Sobel_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)
    absX = cv2.convertScaleAbs(Sobel_x)  # 转回uint8
    # absY = cv2.convertScaleAbs(Sobel_y)
    # dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
    image = absX
    # 二值化：图像的二值化，就是将图像上的像素点的灰度值设置为0或255,图像呈现出明显的只有黑和白
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)

    # 闭操作：闭操作可以将目标区域连成一个整体，便于后续轮廓的提取。
    kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernelX)

    # 膨胀腐蚀(形态学处理)
    kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))
    kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9))
    image = cv2.dilate(image, kernelX)
    # image = cv2.erode(image, kernelX)
    # image = cv2.erode(image, kernelY)
    image = cv2.dilate(image, kernelY)
    # 平滑处理，中值滤波
    image = cv2.medianBlur(image, 15)
    # 查找轮廓
    contours, w1 = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 一一排除不是车牌的矩形区域
    car_contours = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 2000:
            continue
        rect = cv2.minAreaRect(cnt)
        area_width, area_height = rect[1]

        if area_width < area_height:
            area_width, area_height = area_height, area_width
        wh_ratio = area_width / area_height
        # print(wh_ratio)
        # 要求矩形区域长宽比在2到5.5之间，2到5.5是车牌的长宽比，其余的矩形排除
        if 2 < wh_ratio < 5.5:
            car_contours.append(rect)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            rawImage = cv2.drawContours(rawImage, [box], 0, (0, 0, 255), 2)
            # cv2.imshow("rawImage", rawImage)

    # print("矫正矩形")
    card_imgs = []
    # 矩形区域可能是倾斜的矩形，需要矫正，以便使用颜色定位
    for rect in car_contours:
        if -1 < rect[2] < 1:  # 创造角度，使得左、高、右、低拿到正确的值
            angle = 1
        else:
            angle = rect[2]
        rect = (rect[0], (rect[1][0] - 8, rect[1][1] - 8), angle)  # 扩大范围，避免车牌边缘被排除
        box = cv2.boxPoints(rect)
        heigth_point = right_point = [0, 0]
        left_point = low_point = [pic_width, pic_hight]
        for point in box:
            if left_point[0] > point[0]:
                left_point = point
            if low_point[1] > point[1]:
                low_point = point
            if heigth_point[1] < point[1]:
                heigth_point = point
            if right_point[0] < point[0]:
                right_point = point

        if left_point[1] <= right_point[1]:  # 正角度
            new_right_point = [right_point[0], heigth_point[1]]
            pts2 = np.float32([left_point, heigth_point, new_right_point])  # 字符只是高度需要改变
            pts1 = np.float32([left_point, heigth_point, right_point])
            M = cv2.getAffineTransform(pts1, pts2)
            dst = cv2.warpAffine(rawImage, M, (pic_width, pic_hight))
            point_limit(new_right_point)
            point_limit(heigth_point)
            point_limit(left_point)
            card_img = dst[int(left_point[1]):int(heigth_point[1]), int(left_point[0]):int(new_right_point[0])]
            card_imgs.append(card_img)
            # cv2.imshow("card", card_img)
            # cv2.waitKey(0)
        elif left_point[1] > right_point[1]:  # 负角度
            new_left_point = [left_point[0], heigth_point[1]]
            pts2 = np.float32([new_left_point, heigth_point, right_point])  # 字符只是高度需要改变
            pts1 = np.float32([left_point, heigth_point, right_point])
            M = cv2.getAffineTransform(pts1, pts2)
            dst = cv2.warpAffine(rawImage, M, (pic_width, pic_hight))
            point_limit(right_point)
            point_limit(heigth_point)
            point_limit(new_left_point)
            card_img = dst[int(right_point[1]):int(heigth_point[1]), int(new_left_point[0]):int(right_point[0])]
            card_imgs.append(card_img)
            # cv2.imshow("card", card_img)
            # cv2.waitKey(0)

    # print("颜色定位")
    # 开始使用颜色定位，排除不是车牌的矩形，目前只识别蓝、绿、黄车牌
    colors = []
    Maxgreen = Maxyellow = Maxblue = 0
    for card_index, card_img in enumerate(card_imgs):
        green = yellow = blue = black = white = 0
        card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)  # 转hsv格式
        # 有转换失败的可能，原因来自于上面矫正矩形出错
        if card_img_hsv is None:
            continue
        row_num, col_num = card_img_hsv.shape[:2]  # 获取行列值
        card_img_count = row_num * col_num

        #  根据hsv范围统计card_imgs 里面的矩阵颜色
        for i in range(row_num):
            for j in range(col_num):
                H = card_img_hsv.item(i, j, 0)
                S = card_img_hsv.item(i, j, 1)
                V = card_img_hsv.item(i, j, 2)
                if 26 < H <= 34 and S > 43:  # 图片分辨率调整
                    yellow += 1
                elif 35 < H <= 99 and S > 43:  # 图片分辨率调整
                    green += 1
                elif 99 < H <= 124 and S > 43:  # 图片分辨率调整
                    blue += 1
                if 0 < H < 180 and 0 < S < 255 and 0 < V < 46:
                    black += 1
                elif 0 < H < 180 and 0 < S < 43 and 221 < V < 225:
                    white += 1
        color = "no"
        if green > Maxgreen:
            Maxgreen = green
        if blue > Maxblue:
            Maxblue = blue
        if yellow > Maxyellow:
            Maxyellow = yellow

        limit1 = limit2 = 0
        # 确认颜色所对应的hsv范围值
        if yellow * 2 >= card_img_count:
            if yellow < Maxyellow:
                color = 'no'
            else:
                color = "yellow"
            limit1 = 11
            limit2 = 34  # 有的图片有色偏偏绿
        elif green * 2 >= card_img_count:
            if green < Maxgreen:
                color = 'no'
            else:
                color = "green"
            limit1 = 35
            limit2 = 99
        elif blue * 2 >= card_img_count:
            if blue < Maxblue:
                color = 'no'
            else:
                color = "blue"
            limit1 = 100
            limit2 = 124  # 有的图片有色偏偏紫
        elif black + white >= card_img_count * 0.7:  # TODO
            color = "bw"
        # print(color)
        colors.append(color)
        # print(blue, green, yellow, black, white, card_img_count)
        # if color != 'no':
        #     cv2.imshow("color", card_img)
        #     cv2.waitKey(0)
        if limit1 == 0:
            continue

        # 以上为确定车牌颜色
        # 以下为根据车牌颜色再定位，缩小边缘非车牌边界
        xl, xr, yh, yl = accurate_place(card_img_hsv, limit1, limit2, color)
        if yl == yh and xl == xr:
            continue
        need_accurate = False
        if yl >= yh:
            yl = 0
            yh = row_num
            need_accurate = True
        if xl >= xr:
            xl = 0
            xr = col_num
            need_accurate = True
        card_imgs[card_index] = card_img[yl:yh, xl:xr] if color != "green" or yl < (yh - yl) // 4 else card_img[
                                                                                                       yl - (
                                                                                                               yh - yl) // 4:yh,
                                                                                                       xl:xr]
        if need_accurate:  # 可能x或y方向未缩小，需要再试一次
            card_img = card_imgs[card_index]
            card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
            xl, xr, yh, yl = accurate_place(card_img_hsv, limit1, limit2, color)
            if yl == yh and xl == xr:
                continue
            if yl >= yh:
                yl = 0
                yh = row_num
            if xl >= xr:
                xl = 0
                xr = col_num
        card_imgs[card_index] = card_img[yl:yh, xl:xr] if color != "green" or yl < (yh - yl) // 4 else card_img[
                                                                                                       yl - (
                                                                                                               yh - yl) // 4:yh,

                                                                                                       xl:xr]

    # 以上为车牌定位
    # 以下为识别车牌中的字符
    predict_result = []
    roi = None
    card_color = None
    for i, color in enumerate(colors):
        if color in ("blue", "yellow", "green"):
            card_img = card_imgs[i]
            gray_img = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite("number_plate/card_img.jpg",card_img)
            # cv2.imshow("card_img", card_img)
            # cv2.waitKey(0)
            # 黄、绿车牌字符比背景暗、与蓝车牌刚好相反，所以黄、绿车牌需要反向
            if color == "green" or color == "yellow":
                gray_img = cv2.bitwise_not(gray_img)

            ret, gray_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)#cv2.THRESH_BINARY_INV cv2.THRESH_BINARY
            if color == "green":
                print("绿牌！")
            elif color == "blue":
                print("蓝牌！")
            elif color == "yellow":
                print("黄牌！")
            cv2.imwrite(destination,gray_img)
            print("成功定位！")
            # cv2.imshow("gray_img", gray_img)
            # cv2.waitKey(0)
            # 分割字符
            white = []  # 记录每一列的白色像素总和
            black = []  # ..........黑色.......
            height = gray_img.shape[0]
            width = gray_img.shape[1]
            white_max = 0
            black_max = 0
            # 计算每一列的黑白色像素总和
            for k in range(width):
                s = 0  # 这一列白色总数
                t = 0  # 这一列黑色总数
                for j in range(height):
                    if gray_img[j][k] == 255:
                        s += 1
                    if gray_img[j][k] == 0:
                        t += 1
                white_max = max(white_max, s)
                black_max = max(black_max, t)
                white.append(s)
                black.append(t)
                # print(s)
                # print(t)

            arg = False  # False表示白底黑字；True表示黑底白字
            if black_max > white_max:
                arg = True
                # print('arg = ', arg)

            count = 0 #count计数器
            n = 1
            start = 1
            end = 2
            s_width = 28
            s_height = 28
            cjs = []
            while n < width - 2:
                n += 1
                # 判断是白底黑字还是黑底白字  0.05参数对应上面的0.95 可作调整
                if (white[n] if arg else black[n]) > (0.05 * white_max if arg else 0.05 * black_max):
                    start = n
                    end = find_end(start, arg, black, white, width, black_max, white_max)
                    n = end
                    # print('start = ', start)
                    # print('end = ', end)
                    if end - start > 5:
                        cj = gray_img[1:height, start:end]
                        cjs.append(cj)
                        # new_image = cj.resize((s_width,s_height),Image.BILINEAR)
                        # cj=cj.reshape(28, 28)
                        # print("split_img/%s.jpg" % (count))
                        # 保存分割的图片 by cayden
                        # cj.save("result/%s.jpg" % (n))
                        infile = "split_img/%s.jpg" % (count)
                        io.imsave(infile, cj)
                        count+=1 #count计数器

                        # im = Image.open(infile)
                        # out=im.resize((s_width,s_height),Image.BILINEAR)
                        # out.save(infile)

                        # cv2.imshow('cutlicense', cj)
                        # cv2.waitKey(0)

src = "origin_img/1.jpg"
destination = "number_plate/gray.jpg"
predict(src,destination)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

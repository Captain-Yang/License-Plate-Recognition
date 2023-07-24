import cv2
import numpy as np

'''水平投影'''
def getHProjection(img):
    hProjection = np.zeros(img.shape,np.uint8)
    #图像高与宽
    (h,w)=img.shape
    print(hProjection)
    print(img.shape)
    #长度与图像高度一致的数组
    h_ = [0]*h
    #循环统计每一行白色像素的个数
    for y in range(h):
        for x in range(w):
            if img[y,x] == 255:
                h_[y]+=1
    #绘制水平投影图像
    for y in range(h):
        for x in range(h_[y]):
            hProjection[y,x] = 255
    cv2.imshow('hProjection',hProjection)
    cv2.waitKey(0)
    return h_

def getVProjection(img):
    vProjection = np.zeros(img.shape,np.uint8);
    #图像高与宽
    (h,w) = img.shape
    #长度与图像宽度一致的数组
    w_ = [0]*w
    #循环统计每一列白色像素的个数
    for x in range(w):
        for y in range(h):
            if img[y,x] == 255:
                w_[x]+=1
    #绘制垂直平投影图像
    for x in range(w):
        for y in range(h-w_[x],h):
            vProjection[y,x] = 255
    cv2.imshow('vProjection',vProjection)
    cv2.waitKey(0)
    return w_

if __name__ == "__main__":
    #读入原始图像
    origineImage = cv2.imread("number_plate/card_img.jpg")
    # 图像灰度化
    gray = cv2.cvtColor(origineImage,cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray',gray)
    cv2.waitKey(0)
    # 将图片二值化
    ret, img = cv2.threshold(gray,190,255,cv2.THRESH_BINARY) #cv2.THRESH_BINARY  cv2.THRESH_BINARY_INV
    cv2.imshow('binary',img)
    cv2.waitKey(0)
    #图像高与宽
    (h,w)=img.shape
    Position = []
    #水平投影
    H = getHProjection(img)
    start = 0
    H_Start = []
    H_End = []
    #根据水平投影获取垂直分割位置
    print("len(H)={}".format(len(H)))
    print("w={}".format(w))
    #根据水平投影获取垂直分割位置
    for i in range(len(H)):
        if H[i] > w/4 and start ==0:
            H_Start.append(i)
            start = 1
        if H[i] <= 0 and start == 1:
            H_End.append(i)
            start = 0
    #分割行，分割之后再进行列分割并保存分割位置
    for i in range(len(H_Start)):
        #获取行图像
        cropImg = img[H_Start[i]:H_End[i], 0:w]
        cv2.imshow('cropImg',cropImg)
        cv2.waitKey(0)
        #对行图像进行垂直投影
        W = getVProjection(cropImg)
        Wstart = 0
        Wend = 0
        W_Start = 0
        W_End = 0
        for j in range(len(W)):
            if W[j] > 0 and Wstart ==0:
                W_Start =j
                Wstart = 1
                Wend=0
            if W[j] <= 0 and Wstart == 1:
                W_End =j
                Wstart = 0
                Wend=1
            if Wend == 1:
                Position.append([W_Start,H_Start[i],W_End,H_End[i]])
                Wend =0
    print(len(Position))
    #根据确定的位置分割字符
    # for m in range(len(Position)):
    #     cv2.rectangle(origineImage, (Position[m][0],Position[m][1]), (Position[m][2],Position[m][3]), (247 ,166 ,4), 1)
    #     cv2.imshow('origineImage',origineImage)
    #     cv2.waitKey(0)
    #     final_img = origineImage[Position[m][1]:Position[m][3],Position[m][0]:Position[m][2],:]
    #     path = "split_img/" + str(m) + ".jpg"
    #     if(m>0 and m!=2 and m<8):
    #         cv2.imwrite(path,final_img)
    cv2.rectangle(origineImage, (Position[0][0],Position[0][1]), (Position[0][2],Position[0][3]),(0 ,0 ,255) , 1)#(247 ,166 ,4)
    cv2.imshow('origineImage',origineImage)
    cv2.waitKey(0)
    final_img = origineImage[Position[1][1]:Position[6][3],Position[1][0]:Position[6][2],:]
    path = "split_img/" + "test" + ".jpg"
    cv2.imwrite(path,final_img)


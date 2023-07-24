from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from new_locantion_divide import *
from new_tesseract import *


class CameraWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__()
        # 判断是否使用一个参数的构造函数
        if parent is not None:
            self.setParent(parent)
        self.setFixedSize(800, 360)
        self.setWindowTitle("摄像头-截图识别")
        self.setup_ui()

        # 初始化显示的np图像数组和摄像头、Qt图像
        # 设置摄像头参数
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # 从上到下一次为宽、高、帧率
        self.cap.set(3, 640)
        self.cap.set(4, 360)
        self.cap.set(5, 60)
        self.image = None
        self.q_image = None
        # 将摄像头标签设为全局变量，方便更新
        self.capture = self.findChild(QLabel, "capture")
        # 创建定时器，间隔发信号，更新图片
        self.timer = QTimer(self)

        self.start_webcam()

    def setup_ui(self):
        # 左侧区域
        left = QWidget(self)
        left.setObjectName("left")
        left.setFixedSize(640, 360)

        # 摄像头区域
        capture = QLabel(self)
        capture.setAlignment(Qt.AlignCenter)
        capture.setObjectName("capture")
        capture.setFixedSize(640, 360)

        # 左侧布局
        leftLayout = QHBoxLayout()
        leftLayout.addWidget(capture)
        leftLayout.setContentsMargins(0, 0, 0, 0)
        left.setLayout(leftLayout)

        # 右侧区域
        right = QWidget(self)
        right.setObjectName("right")
        right.setFixedSize(160, 360)

        # 捕获按钮
        screenshot = QPushButton(self)
        screenshot.setText("截图")
        screenshot.setFixedWidth(120)

        screenshot.clicked.connect(self.screenshotSlot)
        # 重置按钮
        reset = QPushButton(self)
        reset.setText("重置")
        reset.setFixedWidth(120)
        reset.clicked.connect(self.resetSlot)
        # 确定按钮
        confirm = QPushButton(self)
        confirm.setText("确认")
        confirm.setFixedWidth(120)
        confirm.clicked.connect(self.confirmSlot)
        confirm.setObjectName("confirm")

        # 右侧布局
        rightLayout = QVBoxLayout()
        rightLayout.addStretch(3)
        # 第二个参数为stretch
        rightLayout.addWidget(screenshot, 0, Qt.AlignCenter)
        rightLayout.addWidget(reset, 0, Qt.AlignCenter)
        rightLayout.addWidget(confirm, 0, Qt.AlignCenter)
        rightLayout.addStretch(20)
        rightLayout.setContentsMargins(0, 0, 0, 0)
        right.setLayout(rightLayout)

        # 主窗口布局
        layout = QHBoxLayout()
        layout.addWidget(left)
        layout.addWidget(right)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    # 设置摄像头参数，设定计时器
    def start_webcam(self):
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(17)

    # 更新摄像头标签的图像
    def update_frame(self):
        ret, self.image = self.cap.read()
        self.q_image = QImage(self.image.data, self.image.shape[1], self.image.shape[0],
                              self.image.shape[1]*3, QImage.Format_BGR888)
        pix = QPixmap().fromImage(self.q_image)
        self.capture.setPixmap(pix)

    # 捕获按钮的槽函数
    def screenshotSlot(self):
        if self.timer.isActive():
            self.timer.stop()

    # 重置按钮的槽函数
    def resetSlot(self):
        if not self.timer.isActive():
            self.timer.start(17)

    # 确定按钮的槽函数，关闭此窗口，close函数发生一个事件
    def confirmSlot(self):
        # 释放摄像头
        self.timer.stop()
        self.cap.release()
        self.close()

    # 重写关闭事件，先停止计时器发送信号，再释放摄像头，最后再关闭
    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        self.close()


class Window(QWidget):

    def __init__(self):
        # 主窗口
        super().__init__()
        # 初始化预处理窗口，来自摄像头窗口，保存结果的列表
        self.pre_window = QWidget(self)
        self.camera = None
        # 返回的列表包含状态码、原车牌、车牌颜色、灰度化后的车牌、预处理的图像
        self.res = []
        self.setFixedSize(1280, 720)
        self.setWindowTitle("车牌识别")
        self.setup_ui()

    def setup_ui(self):
        # 左侧区域
        left = QWidget(self)
        left.setObjectName("left")
        # left.resize(960, 720)
        left.setFixedSize(960, 720)

        # 左侧图片文本标签
        imgLabel = QLabel(self)
        imgLabel.setFixedHeight(20)
        imgLabel.setText("原图：")
        # imgLabel.setMargin(0)
        # 显示图片标签img
        img = QLabel(left)
        img.setObjectName("img")
        img.setPixmap(QPixmap("./label.jpg").scaled(900, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation))


        # 左侧区域布局
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(imgLabel)
        leftLayout.addWidget(img)
        leftLayout.setMargin(0)
        # leftLayout.setContentsMargins(0, 0, 0, 0)
        left.setLayout(leftLayout)

        # 右侧区域
        right = QWidget(self)
        right.setObjectName("right")
        right.setFixedSize(320, 700)

        # 形状定位车牌位置文本标签
        shapeLabel = QLabel(right)
        shapeLabel.setText("颜色形状定位车牌位置:")
        # shapeLabel.setFixedHeight(20)
        # 形状定位车牌位置图片标签
        shape = QLabel(right)
        shape.setFixedSize(300, 120)
        shape.setObjectName("shape")
        # 形状定位识别结果文本标签
        shapeResLabel = QLabel(right)
        shapeResLabel.setText("颜色形状定位识别结果:")
        # 形状定位识别结果标签
        shapeRes = QLabel(right)
        shapeRes.setObjectName("shapeRes")
        # 形状定位识别车牌颜色结果标签
        shapeColorRes = QLabel(right)
        shapeColorRes.setObjectName("shapeColorRes")

        # 颜色定位车牌位置文本标签
        # colorLabel = QLabel(right)
        # colorLabel.setText("颜色定位车牌位置:")
        # 颜色定位车牌位置图片标签
        # color = QLabel(right)

        # 颜色定位车牌识别结果文本标签
        # colorResLabel = QLabel(right)
        # colorResLabel.setText("颜色定位车牌识别结果:")
        # 颜色定位车牌识别结果标签
        # colorRes = QLabel(right)
        # 颜色定位车牌颜色识别结果标签
        # colorColorRes = QLabel(right)

        # 来自摄像头按钮
        camera = QPushButton(right)
        camera.setText("来自摄像头")
        # camera.setFixedSize()
        camera.clicked.connect(self.cameraSlot)
        # 来自图片按钮
        picture = QPushButton(right)
        picture.setText("来自图片")
        picture.clicked.connect(self.pictureSlot)
        # 查看形状处理图像按钮
        pretreatment = QPushButton(right)
        pretreatment.setText("查看预处理图像")
        pretreatment.clicked.connect(self.preSlot)

        # 右侧区域布局
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(shapeLabel)
        rightLayout.addWidget(shape)
        rightLayout.addWidget(shapeResLabel)
        rightLayout.addWidget(shapeRes)
        rightLayout.addWidget(shapeColorRes)
        # rightLayout.addWidget(colorLabel)
        # rightLayout.addWidget(color)
        # rightLayout.addWidget(colorResLabel)
        # rightLayout.addWidget(colorRes)
        # rightLayout.addWidget(colorColorRes)
        rightLayout.addWidget(camera)
        rightLayout.addWidget(picture)
        rightLayout.addWidget(pretreatment)
        # rightLayout.setContentsMargins(0, 0, 0, 0)
        right.setLayout(rightLayout)

        # 主窗口布局
        windowLayout = QHBoxLayout()
        windowLayout.addWidget(left)
        windowLayout.addWidget(right)
        self.setLayout(windowLayout)

    # 来自图片按钮链接的槽函数
    def pictureSlot(self):
        # 获取图片的绝对路径
        url = QFileDialog.getOpenFileName(self, "打开图片", ".", "Images (*.jpg *.png)")[0]
        # 做出判断，以防url为空
        if url == '':
            return

        # 获取左窗口的图片标签控件并改变图片
        left = self.findChild(QWidget, "left")
        img = left.findChild(QLabel, "img")
        img.setPixmap(QPixmap(url).scaled(900, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 处理图片识别车牌获取结果
        # 结果是一个列表，依次包括状态码，结果array
        # imread中不能有中文路径，改用imdecode
        # with open(url, 'rb') as f:
        #     license_plate = cv2.imdecode(np.array(bytearray(f.read()), dtype=np.uint8), cv2.IMREAD_COLOR)

        # 返回的列表包含状态码、原车牌、车牌颜色、灰度化后的车牌、预处理的图像
        self.res = predict(url)

        # print(color_position(license_plate))
        # 获取右窗口的形状识别图片标签控件和显示结果的控件
        right = self.findChild(QWidget, "right")
        shape = right.findChild(QLabel, "shape")
        shapeRes = right.findChild(QLabel, "shapeRes")
        if self.res[0] == 0:
            shapeRes.setText("无法识别")
            return

        # 将结果图片numpy数组转为QImage, 再转为QPixmap输出
        h = self.res[1].shape[0]
        w = self.res[1].shape[1]
        # 返回的np数组存储地址不是连续，需要再做转换才能使用QImage
        plate_img = np.array(self.res[1], dtype=np.uint8)
        pix = QPixmap.fromImage(QImage(plate_img.data, w, h, w*3, QImage.Format_BGR888))
        shape.setPixmap(pix.scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 识别结果图片文字并显示结果
        # shapeRes.setText(str(self.ocr.ocr_for_single_line(self.res[2])))
        dis = distinguish_tesseract(self.res[3])
        shapeRes.setStyleSheet("font-size:50px;")
        if not dis:
            shapeRes.setText("无法识别")
        else:
            shapeRes.setText(dis)

        # 显示车牌颜色结果
        shapeColorRes = right.findChild(QLabel, "shapeColorRes")
        # shapeColorRes.setStyleSheet("font-size:50px;")
        if self.res[2] == 'blue':
            shapeColorRes.setText("蓝牌")
            shapeColorRes.setStyleSheet("font-size:25px;color:blue;")
        elif self.res[2] == 'green':
            shapeColorRes.setText("绿牌")
            shapeColorRes.setStyleSheet("font-size:25px;color:green;")
        elif self.res[2] == 'yellow':
            shapeColorRes.setText("黄牌")
            shapeColorRes.setStyleSheet("font-size:25px;color:yellow;")
        else:
            shapeColorRes.setText("车牌颜色无法识别")

    # 形状预处理图像按钮的槽函数
    def preSlot(self):
        if self.res[4] is None:
            return
        # 设置模态窗口显示预处理图片
        # 该模态窗口不能使局部变量
        self.pre_window.setFixedSize(850, 650)
        self.pre_window.setWindowFlags(Qt.Dialog)
        self.pre_window.setWindowTitle("车牌识别-预处理图像")

        # 创建图片标签
        pre_label = QLabel(self.pre_window)
        # 获取图片的宽高
        h = self.res[4].shape[0]
        w = self.res[4].shape[1]
        pix = QPixmap.fromImage(QImage(self.res[4].data, w, h, w*3, QImage.Format_BGR888))
        pre_label.setPixmap(pix.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 添加布局同时设置图片标签的对齐方式，使图片标签居中
        layout = QHBoxLayout()
        layout.addWidget(pre_label)
        pre_label.setAlignment(Qt.AlignCenter)
        self.pre_window.setLayout(layout)

        self.pre_window.setWindowModality(Qt.WindowModal)
        self.pre_window.show()

    def cameraSlot(self):
        # 初始化设置模态化窗口
        self.camera = CameraWindow(self)
        # 解除原有确定按钮的槽函数
        # 先找到原有的confirm按钮，两个槽函数都叫confirmSlot，注意别混淆，处于不同的类
        confirm = self.camera.findChild(QPushButton, "confirm")
        confirm.clicked.disconnect(self.camera.confirmSlot)
        confirm.clicked.connect(self.confirmSlot)
        self.camera.setWindowFlags(Qt.Dialog)
        self.camera.setWindowModality(Qt.WindowModal)
        self.camera.show()

    # 摄像头窗口 确定按钮的槽函数函数，写在主窗口方便传值
    # 关闭此窗口，close函数发生一个事件
    def confirmSlot(self):
        # 释放摄像头
        self.camera.cap.release()

        # 做有无图片检查
        if self.camera.image is None:
            return

        # 获取左窗口的图片标签控件并改变图片
        left = self.findChild(QWidget, "left")
        img = left.findChild(QLabel, "img")
        img.setPixmap(QPixmap().fromImage(self.camera.q_image).scaled(900, 650, Qt.KeepAspectRatio,
                                                                      Qt.SmoothTransformation))

        # 图片识别处理，原图为BGR
        self.res = predict(self.camera.image)
        # 返回的列表包含状态码、原车牌、车牌颜色、灰度化后的车牌、预处理的图像
        if self.res[0] == 0:
            self.camera.close()
            return

        # 获取左窗口的形状识别图片标签控件和显示结果的控件
        right = self.findChild(QWidget, "right")
        shape = right.findChild(QLabel, "shape")
        shapeRes = right.findChild(QLabel, "shapeRes")

        # 将结果图片numpy数组转为QImage, 再转为QPixmap输出
        h = self.res[1].shape[0]
        w = self.res[1].shape[1]
        # 返回的np数组存储地址不是连续，需要再做转换才能使用QImage
        plate_img = np.array(self.res[1], dtype=np.uint8)
        pix = QPixmap.fromImage(QImage(plate_img.data, w, h, w * 3, QImage.Format_BGR888))
        shape.setPixmap(pix.scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 关闭摄像头窗口
        self.camera.close()


# 判断是否在本模块运行，若是，则执行这段代码
if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    window.show()
    app.exec_()

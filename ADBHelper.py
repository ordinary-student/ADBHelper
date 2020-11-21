# encoding:utf-8
import os
import sys
import json
import time as _time
from threading import Thread
from ADBTool import ADBTool
from PySide2.QtGui import QBrush, QPalette, QPixmap, QTextCursor, QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QStyleFactory, QApplication, QMessageBox, QFileDialog


'''
date:2020-11-20
author:ordinary-student
'''


# ADB助手
class ADBHelper(object):
    # 构造函数
    def __init__(self):
        # 加载UI文件
        self.ui = QUiLoader().load('adbwindow.ui')
        # 设置窗口背景
        palette = QPalette()
        pix = QPixmap('bg.jpg')
        #pix = pix.scaled(self.ui.width(), self.ui.height())
        palette.setBrush(self.ui.backgroundRole(), QBrush(pix))
        self.ui.setAutoFillBackground(True)
        self.ui.setPalette(palette)

        self.ui.setWindowIcon(QIcon('adb.png'))
        # self.ui.setWindowFlags(qcore.Qt.WindowStaysOnTopHint)

        # 绑定保存参数菜单项点击事件
        self.ui.save_action.triggered.connect(self.save_params)
        # 绑定加载参数菜单项点击事件
        self.ui.load_action.triggered.connect(self.load_params)
        # 绑定退出菜单项点击事件
        self.ui.exit_action.triggered.connect(self.exit)
        # 绑定断开连接菜单项点击事件
        self.ui.disconnect_action.triggered.connect(self.disconnect)
        # 绑定清空输出信息菜单项点击事件
        self.ui.clear_action.triggered.connect(self.clear)
        # 绑定坐标工具菜单项点击事件
        self.ui.tool_action.triggered.connect(self.tool)
        # 绑定关于菜单项点击事件
        self.ui.about_action.triggered.connect(self.about)

        # 绑定启动ADB按钮点击事件
        self.ui.openadb_pushButton.clicked.connect(self.open_adb)
        # 绑定连接按钮点击事件
        self.ui.connect_pushButton.clicked.connect(self.connect)
        # 绑定显示设备列表按钮点击事件
        self.ui.show_devices_pushButton.clicked.connect(self.show_devices)
        # 绑定开始点击按钮点击事件
        self.ui.tap_pushButton.clicked.connect(self.tap)
        # 绑定开始滑屏按钮点击事件
        self.ui.swipe_pushButton.clicked.connect(self.swipe)
        # 绑定停止按钮点击事件
        self.ui.stop_pushButton.clicked.connect(self.stop)
        # 绑定坐标工具按钮点击事件
        self.ui.tool_pushButton.clicked.connect(self.tool)

        # 限制数值范围
        self.ui.swipe_x1_min_spinBox.valueChanged.connect(self.x1_min)
        self.ui.swipe_x1_max_spinBox.valueChanged.connect(self.x1_max)
        self.ui.swipe_y1_min_spinBox.valueChanged.connect(self.y1_min)
        self.ui.swipe_y1_max_spinBox.valueChanged.connect(self.y1_max)
        self.ui.swipe_x2_min_spinBox.valueChanged.connect(self.x2_min)
        self.ui.swipe_x2_max_spinBox.valueChanged.connect(self.x2_max)
        self.ui.swipe_y2_min_spinBox.valueChanged.connect(self.y2_min)
        self.ui.swipe_y2_max_spinBox.valueChanged.connect(self.y2_max)

        # ADB工具
        self.adbtool = None
        # 连接标志
        self.connected = False
        # 坐标工具窗口
        self.tool_dialog = None
        # 截图文件
        self.screen_cap_file = None

    # 当前时间
    def nowtime(self):
        return str(_time.strftime(
            '%Y-%m-%d %H:%M:%S', _time.localtime(_time.time())))

    # 输出信息
    def output_message(self, message):
        mess = "<font color='orange'>[</font><font color='blue'>"+self.nowtime() + \
            "</font><font color='orange'>]</font><font color='green'>"+message+"</font>"
        self.ui.output_textEdit.append(mess)
        # 移动光标到最底
        self.ui.output_textEdit.moveCursor(QTextCursor.End)

    # 输出结果和错误信息
    def output_result_error(self, result, error):
        # 输出信息
        self.output_message(result)
        # 判断错误信息是否为空
        if len(error.strip()) != 0:
            self.output_message(error)

    # 保存参数
    def save_params(self):
        # 弹出文件选择器
        filepath, filetype = QFileDialog.getSaveFileName(
            self.ui, "保存参数", os.getcwd(), "Json File (*.json)")

        # 判断
        if filepath != "":
            # IP地址
            ip = self.ui.ip_lineEdit.text()
            # 端口号
            port = self.ui.port_spinBox.value()
            # 模拟点击
            tap_x = self.ui.tap_x_spinBox.value()
            tap_y = self.ui.tap_y_spinBox.value()
            tap_times = self.ui.tap_times_spinBox.value()
            tap_interval = round(self.ui.tap_interval_doubleSpinBox.value(), 1)
            tap_random_interval = self.ui.tap_random_interval_checkBox.isChecked()
            # 模拟滑屏
            swipe_x1_min = self.ui.swipe_x1_min_spinBox.value()
            swipe_x1_max = self.ui.swipe_x1_max_spinBox.value()
            swipe_y1_min = self.ui.swipe_y1_min_spinBox.value()
            swipe_y1_max = self.ui.swipe_y1_max_spinBox.value()
            swipe_x2_min = self.ui.swipe_x2_min_spinBox.value()
            swipe_x2_max = self.ui.swipe_x2_max_spinBox.value()
            swipe_y2_min = self.ui.swipe_y2_min_spinBox.value()
            swipe_y2_max = self.ui.swipe_y2_max_spinBox.value()
            swipe_times = self.ui.swipe_times_spinBox.value()
            # 浮点数取整
            swipe_interval = round(
                self.ui.swipe_interval_doubleSpinBox.value(), 1)
            swipe_random_interval = self.ui.swipe_random_interval_checkBox.isChecked()
            swipe_60 = self.ui.swipe_60_checkBox.isChecked()
            # 组成字典
            params = {'ip': ip, 'port': port, 'tap_x': tap_x,
                      'tap_y': tap_y, 'tap_times': tap_times,
                      'tap_interval': tap_interval,
                      'tap_random_interval': tap_random_interval,
                      'swipe_x1_min': swipe_x1_min, 'swipe_x1_max': swipe_x1_max,
                      'swipe_y1_min': swipe_y1_min, 'swipe_y1_max': swipe_y1_max,
                      'swipe_x2_min': swipe_x2_min, 'swipe_x2_max': swipe_x2_max,
                      'swipe_y2_min': swipe_y2_min, 'swipe_y2_max': swipe_y2_max,
                      'swipe_times': swipe_times, 'swipe_interval': swipe_interval,
                      'swipe_random_interval': swipe_random_interval,
                      'swipe_60': swipe_60}
            # 写入文件
            if not filepath.endswith('.json'):
                filepath = filepath+'.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(params, f)
            # 输出信息
            self.output_message('保存参数完成！文件路径：'+os.path.abspath(filepath))

    # 加载参数
    def load_params(self):
        # 弹出文件选择器
        filepath, filetype = QFileDialog.getOpenFileName(
            self.ui, "请选择文件", os.getcwd(), "Json File (*.json)")
        # 判断
        if filepath != "":
            # 读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                params = json.load(f)
                # IP和端口
                self.ui.ip_lineEdit.setText(params['ip'])
                self.ui.port_spinBox.setValue(params['port'])
                # 模拟点击
                self.ui.tap_x_spinBox.setValue(params['tap_x'])
                self.ui.tap_y_spinBox.setValue(params['tap_y'])
                self.ui.tap_times_spinBox.setValue(params['tap_times'])
                self.ui.tap_interval_doubleSpinBox.setValue(
                    params['tap_interval'])
                self.ui.tap_random_interval_checkBox.setChecked(
                    params['tap_random_interval'])
                # 模拟滑屏
                self.ui.swipe_x1_max_spinBox.setValue(params['swipe_x1_max'])
                self.ui.swipe_x1_min_spinBox.setValue(params['swipe_x1_min'])
                self.ui.swipe_y1_max_spinBox.setValue(params['swipe_y1_max'])
                self.ui.swipe_y1_min_spinBox.setValue(params['swipe_y1_min'])
                self.ui.swipe_x2_max_spinBox.setValue(params['swipe_x2_max'])
                self.ui.swipe_x2_min_spinBox.setValue(params['swipe_x2_min'])
                self.ui.swipe_y2_max_spinBox.setValue(params['swipe_y2_max'])
                self.ui.swipe_y2_min_spinBox.setValue(params['swipe_y2_min'])
                self.ui.swipe_times_spinBox.setValue(params['swipe_times'])
                self.ui.swipe_interval_doubleSpinBox.setValue(
                    params['swipe_interval'])
                self.ui.swipe_random_interval_checkBox.setChecked(
                    params['swipe_random_interval'])
                self.ui.swipe_60_checkBox.setChecked(params['swipe_60'])
            # 输出信息
            self.output_message('加载参数完成！文件路径：'+os.path.abspath(filepath))

    # 退出
    def exit(self):
        # 保存日志
        # 断开连接
        self.disconnect()
        # 退出
        self.ui.close()

    # 断开连接
    def disconnect(self):
        # 停止
        self.stop()
        # 断开连接
        result, error = ADBTool().disconnect()
        # 输出信息
        self.output_result_error(result, error)
        self.connected = False
        self.output_message('已经断开连接')
        # 按钮可点
        self.ui.tap_pushButton.setEnabled(True)
        self.ui.swipe_pushButton.setEnabled(True)

    # 清空输出信息
    def clear(self):
        self.ui.output_textEdit.setText('')

    # 关于
    def about(self):
        # 显示弹窗
        QMessageBox.about(
            self.ui, '关于', 'ADB助手\n© Copyright 2020\n作者：ordinary-student\n版本：v1.0.0')

    # 打开ADB
    def open_adb(self):
        # 获取IP地址
        ip = self.ui.ip_lineEdit.text()
        # IP校验
        if len(ip.strip()) == 0:
            self.ui.ip_lineEdit.setText('')
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', '请填写IP地址！')
            return
        # 获取端口号
        port = self.ui.port_spinBox.value()
        # 创建ADB工具
        adbtool = ADBTool(ip, port)
        # 启动ADB
        result, error = adbtool.open()
        # 输出信息
        self.output_result_error(result, error)
        # 判断是否已经启动
        if ('restarting' in result) and ('error' not in error):
            self.adbtool = adbtool
            self.output_message('ADB已经启动')

    # 连接设备
    def connect(self):
        # 判断
        if self.adbtool == None:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', 'ADB尚未启动！')
            return
        # 连接
        try:
            result, error = self.adbtool.connect()
            # 输出信息
            self.output_result_error(result, error)
            # 判断是否已经启动
            if ('connected' in result) and ('error' not in error):
                self.connected = True
                self.output_message('已经连接设备')
                self.adbtool.tap(700, 1860)
        except:
            self.output_message('设备连接失败')
            # 显示弹窗
            QMessageBox.information(
                self.ui, '提示', '设备连接失败！\n请检查设备和电脑是否处于同一局域网，\n检查设备的USB调试模式是否已经打开。\n若还是不行，请重启软件再尝试。')
            return

    # 显示设备列表
    def show_devices(self):
        # 显示设备列表
        result, error = ADBTool().show_devices()
        # 输出信息
        self.output_result_error(result, error)

    # 开始点击
    def tap(self):
        # 判断ADB是否启动
        if self.adbtool == None:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', 'ADB尚未启动！')
            return
        # 判断是否连接
        if self.connected:
            tap_thread = Thread(target=self.tap2)
            tap_thread.start()
        else:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', '尚未连接设备！')
            return

    # 开始点击
    def tap2(self):
        # 按钮不可点
        self.ui.tap_pushButton.setEnabled(False)
        # 获取参数
        tap_x = self.ui.tap_x_spinBox.value()
        tap_y = self.ui.tap_y_spinBox.value()
        tap_times = self.ui.tap_times_spinBox.value()
        tap_interval = round(self.ui.tap_interval_doubleSpinBox.value(), 1)
        tap_random_interval = self.ui.tap_random_interval_checkBox.isChecked()
        if tap_random_interval:
            message = '点击坐标（{}，{}）处，{}次，时间间隔随机'.format(
                tap_x, tap_y, tap_times)
        else:
            message = '点击坐标（{}，{}）处，{}次，时间间隔{}秒'.format(
                tap_x, tap_y, tap_times, tap_interval)
        self.output_message(message)
        # 模拟点击
        if self.adbtool.continuous_tap(tap_x, tap_y, tap_times, tap_interval, tap_random_interval):
            self.output_message('模拟点击已完成')
        else:
            self.output_message('模拟点击已停止')
        # 按钮可点
        self.ui.tap_pushButton.setEnabled(True)

    # 开始滑屏
    def swipe(self):
        # 判断ADB是否启动
        if self.adbtool == None:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', 'ADB尚未启动！')
            return
        # 判断是否连接
        if self.connected:
            swipe_thread = Thread(target=self.swipe2)
            swipe_thread.start()
        else:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', '尚未连接设备！')
            return

    # 开始滑屏
    def swipe2(self):
        # 按钮不可点
        self.ui.swipe_pushButton.setEnabled(False)
        # 获取参数
        swipe_x1_min = self.ui.swipe_x1_min_spinBox.value()
        swipe_x1_max = self.ui.swipe_x1_max_spinBox.value()
        swipe_y1_min = self.ui.swipe_y1_min_spinBox.value()
        swipe_y1_max = self.ui.swipe_y1_max_spinBox.value()
        swipe_x2_min = self.ui.swipe_x2_min_spinBox.value()
        swipe_x2_max = self.ui.swipe_x2_max_spinBox.value()
        swipe_y2_min = self.ui.swipe_y2_min_spinBox.value()
        swipe_y2_max = self.ui.swipe_y2_max_spinBox.value()
        swipe_times = self.ui.swipe_times_spinBox.value()
        swipe_interval = round(self.ui.swipe_interval_doubleSpinBox.value(), 1)
        swipe_random_interval = self.ui.swipe_random_interval_checkBox.isChecked()
        swipe_60 = self.ui.swipe_60_checkBox.isChecked()
        # 定时60秒
        if swipe_60:
            message = '从坐标（{}~{}，{}~{}）滑到（{}~{}，{}~{}）处，连续滑屏60秒，时间间隔{}秒'.format(
                swipe_x1_min, swipe_x1_max, swipe_y1_min, swipe_y1_max, swipe_x2_min, swipe_x2_max, swipe_y2_min, swipe_y2_max, swipe_interval)
            self.output_message(message)
            # 模拟连续滑屏60秒
            if self.adbtool.timing_swipe((
                    swipe_x1_min, swipe_x1_max), (swipe_y1_min, swipe_y1_max), (swipe_x2_min, swipe_x2_max), (swipe_y2_min, swipe_y2_max), swipe_interval, swipe_random_interval):
                self.output_message('模拟滑屏已完成')
            else:
                self.output_message('模拟滑屏已停止')
        else:
            if swipe_random_interval:
                message = '从坐标（{}~{}，{}~{}）滑到（{}~{}，{}~{}）处，{}次，时间间隔随机'.format(
                    swipe_x1_min, swipe_x1_max, swipe_y1_min, swipe_y1_max, swipe_x2_min, swipe_x2_max, swipe_y2_min, swipe_y2_max, swipe_times)
            else:
                message = '从坐标（{}~{}，{}~{}）滑到（{}~{}，{}~{}）处，{}次，时间间隔{}秒'.format(
                    swipe_x1_min, swipe_x1_max, swipe_y1_min, swipe_y1_max, swipe_x2_min, swipe_x2_max, swipe_y2_min, swipe_y2_max, swipe_times, swipe_interval)
            self.output_message(message)
            # 模拟滑屏
            if self.adbtool.random_swipe((
                    swipe_x1_min, swipe_x1_max), (swipe_y1_min, swipe_y1_max), (swipe_x2_min, swipe_x2_max), (swipe_y2_min, swipe_y2_max), swipe_times, swipe_interval, swipe_random_interval):
                self.output_message('模拟滑屏已完成')
            else:
                self.output_message('模拟滑屏已停止')
        # 按钮可点
        self.ui.swipe_pushButton.setEnabled(True)

    # 停止
    def stop(self):
        if self.adbtool != None:
            self.adbtool.stop()
            # 按钮可点
            self.ui.tap_pushButton.setEnabled(True)
            self.ui.swipe_pushButton.setEnabled(True)

    # 截图
    def screen_cap(self):
        if self.adbtool != None:
            # 截图
            photo_path = self.adbtool.screen_cap()
            # 获取图片到本地
            result, error = self.adbtool.pull_file(photo_path)
            self.output_result_error(result, error)
            # 判断
            if ('png' in result) and ('error' not in error):
                path = photo_path[(photo_path.rindex('/')+1):]
                self.output_message('截图成功！图片路径：'+os.path.abspath(path))
                return os.path.abspath(path)
            else:
                self.output_message('截图失败！')
                return None
        else:
            return None

    # 坐标工具
    def tool(self):
        # 判断ADB是否启动
        if self.adbtool == None:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', 'ADB尚未启动！')
            return
        # 判断是否连接
        if self.connected:
            self.axis_tool()
        else:
            # 显示弹窗
            QMessageBox.information(self.ui, '提示', '尚未连接设备！')
            return

    # 坐标工具
    def axis_tool(self):
        w = 300
        h = 600
        # 判断
        if self.tool_dialog == None:
            # 创建坐标工具窗
            self.tool_dialog = QDialog(self.ui)
            self.tool_dialog.setWindowTitle('坐标工具')
            self.tool_dialog.resize(w, h)
        # 截图
        photo_path = self.screen_cap()
        if photo_path != None:
            if self.screen_cap_file != None:
                os.remove(self.screen_cap_file)
            self.screen_cap_file = photo_path
            pix = QPixmap(photo_path)
            w = pix.width()
            h = pix.height()
            # 设置面板大小
            self.tool_dialog.setFixedSize(w/4, h/4)
            # 调色板
            palette = QPalette()
            # 缩小图片
            pix = pix.scaled(w/4, h/4)
            palette.setBrush(self.tool_dialog.backgroundRole(), QBrush(pix))
            self.tool_dialog.setAutoFillBackground(True)
            self.tool_dialog.setPalette(palette)
            self.tool_dialog.setMouseTracking(True)
            # 绑定鼠标移动事件
            self.tool_dialog.mouseMoveEvent = self.mouse_move
        # 显示窗口
        self.tool_dialog.show()
        # 十字光标
        self.tool_dialog.setCursor(Qt.CrossCursor)

    # 鼠标移动
    def mouse_move(self, event):
        x = event.pos().x()
        y = event.pos().y()
        #print(x, y)
        self.tool_dialog.setWindowTitle('X：{}，Y：{}'.format(x*4, y*4))

    # 限制数值范围
    def x1_min(self):
        if self.ui.swipe_x1_min_spinBox.value() >= self.ui.swipe_x1_max_spinBox.value():
            self.ui.swipe_x1_min_spinBox.setValue(
                self.ui.swipe_x1_max_spinBox.value())

    #
    def x1_max(self):
        if self.ui.swipe_x1_max_spinBox.value() <= self.ui.swipe_x1_min_spinBox.value():
            self.ui.swipe_x1_max_spinBox.setValue(
                self.ui.swipe_x1_min_spinBox.value())

    #
    def y1_min(self):
        if self.ui.swipe_y1_min_spinBox.value() >= self.ui.swipe_y1_max_spinBox.value():
            self.ui.swipe_y1_min_spinBox.setValue(
                self.ui.swipe_y1_max_spinBox.value())

    #
    def y1_max(self):
        if self.ui.swipe_y1_max_spinBox.value() <= self.ui.swipe_y1_min_spinBox.value():
            self.ui.swipe_y1_max_spinBox.setValue(
                self.ui.swipe_y1_min_spinBox.value())

    #
    def x2_min(self):
        if self.ui.swipe_x2_min_spinBox.value() >= self.ui.swipe_x2_max_spinBox.value():
            self.ui.swipe_x2_min_spinBox.setValue(
                self.ui.swipe_x2_max_spinBox.value())

    #
    def x2_max(self):
        if self.ui.swipe_x2_max_spinBox.value() <= self.ui.swipe_x2_min_spinBox.value():
            self.ui.swipe_x2_max_spinBox.setValue(
                self.ui.swipe_x2_min_spinBox.value())

    #
    def y2_min(self):
        if self.ui.swipe_y2_min_spinBox.value() >= self.ui.swipe_y2_max_spinBox.value():
            self.ui.swipe_y2_min_spinBox.setValue(
                self.ui.swipe_y2_max_spinBox.value())

    #
    def y2_max(self):
        if self.ui.swipe_y2_max_spinBox.value() <= self.ui.swipe_y2_min_spinBox.value():
            self.ui.swipe_y2_max_spinBox.setValue(
                self.ui.swipe_y2_min_spinBox.value())


if __name__ == "__main__":
    # 创建QTAPP对象应用
    app = QApplication([])
    # 设置界面风格
    app.setStyle(QStyleFactory.create('Fusion'))
    # 创建窗体
    adbhelper = ADBHelper()
    # 显示窗体
    adbhelper.ui.show()
    # 主线程循环
    sys.exit(app.exec_())

import os
import random
import time as _time
import subprocess

'''
date:2020-11-20
author:ordinary-student
'''


# ADB工具类
class ADBTool(object):
    # 构造函数
    def __init__(self, ip='', port=5555):
        # IP地址
        self.ip = ip
        # 端口号
        self.port = port
        # 停止标志
        self.stop_flag = False

    # 打开ADB
    def open(self):
        # os.system('adb tcpip {}'.format(self.port))
        result, error = self.popen('adb tcpip {}'.format(self.port))
        print(result, error)
        return result, error

    # 连接
    def connect(self):
        # os.system('adb connect {}'.format(self.ip))
        result, error = self.popen(
            'adb connect {}:{}'.format(self.ip, self.port))
        print(result, error)
        return result, error

    # 断开连接
    def disconnect(self):
        # os.system('adb disconnect')
        result, error = self.popen('adb disconnect')
        print(result, error)
        return result, error

    # 显示设备列表
    def show_devices(self):
        # os.system('adb devices')
        result, error = self.popen('adb devices')
        print(result, error)
        return result, error

    # 点击屏幕
    def tap(self, x, y):
        try:
            self.popen(
                'adb -s {}:{} shell input tap {} {}'.format(self.ip, self.port, x, y))
            return True
        except:
            return False

    # 连续点击屏幕
    def continuous_tap(self, x, y, times=1, interval=1.0, use_random_interval=False):
        # 坐标，次数，时间间隔，是否使用随机时间间隔
        self.stop_flag = False
        # 循环
        for i in range(times):
            # 停顿时间
            t = interval
            # 判断是否使用随机时间
            if use_random_interval:
                t = random.uniform(0.1, 1)
            # 点击屏幕
            if self.tap(x, y) == False:
                return False
            # 停顿
            _time.sleep(t)
            # 判断是否停止
            if self.stop_flag:
                return False
        # 返回
        return True

    # 滑动屏幕
    def swipe(self, x1, y1, x2, y2):
        try:
            # 会弹出黑窗
            # os.system('adb -s {}:{} shell input swipe {} {} {} {}'.format(self.ip, self.port, x1, y1, x2, y2))
            # 改用POPEN
            self.popen(
                'adb -s {}:{} shell input swipe {} {} {} {}'.format(self.ip, self.port, x1, y1, x2, y2))
            return True
        except:
            return False

    # 连续随机滑动屏幕
    def random_swipe(self, x1_range, y1_range, x2_range, y2_range, times=1, interval=1.0, use_random_interval=False):
        # x1_range=(x1_min,x1_max)即坐标值范围的最小值，最大值
        # times次数，interval时间间隔，use_random_interval是否使用随机时间间隔
        self.stop_flag = False
        # 循环
        for i in range(times):
            # 随机坐标
            x1 = random.randint(x1_range[0], x1_range[1])
            y1 = random.randint(y1_range[0], y1_range[1])
            x2 = random.randint(x2_range[0], x2_range[1])
            y2 = random.randint(y2_range[0], y2_range[1])
            # 停顿时间
            t = interval
            # 判断是否使用随机时间
            if use_random_interval:
                t = random.uniform(0.1, 1)
            # 滑屏
            if self.swipe(x1, y1, x2, y2) == False:
                return False
            # 停顿
            _time.sleep(t)
            # 判断是否停止
            if self.stop_flag:
                return False
        # 返回
        return True

    # 定时随机滑动屏幕
    def timing_swipe(self, x1_range, y1_range, x2_range, y2_range, interval=0.5, use_random_interval=False, timing=60):
        # x1_range=(x1_min,x1_max)即坐标值范围的最小值，最大值
        # interval时间间隔，use_random_interval是否使用随机时间间隔
        # timing定时时间

        # 记录开始时间
        start_time = int(_time.time())
        end_time = int(_time.time())

        # 循环判断
        while(end_time-start_time) < timing:
            # 滑屏
            if self.random_swipe(x1_range, y1_range, x2_range,
                                 y2_range, 1, interval, use_random_interval) == False:
                return False
            # 记录结束时间
            end_time = int(_time.time())
            # print(end_time-start_time)
        # 返回
        return True

    # 输入文本
    def text(self, text):
        self.popen(
            'adb -s {}:{} shell input text "{}"'.format(self.ip, self.port, text))

    # 截图
    def screen_cap(self):
        # 图片文件名
        name = _time.strftime('%Y%m%d%H%M%S',
                              _time.localtime(_time.time()))
        path = '/sdcard/{}.png'.format(name)
        self.popen(
            'adb -s {}:{} shell screencap {}'.format(self.ip, self.port, path))
        # 返回文件路径
        return path

    # 录屏
    def screen_record(self, time):
        # 视频文件名
        name = _time.strftime('%Y%m%d%H%M%S',
                              _time.localtime(_time.time()))
        path = '/sdcard/{}.mp4'.format(name)
        self.popen(
            'adb -s {}:{} shell screenrecord --time -limit {} {}'.format(self.ip, self.port, time, path))
        # 返回文件路径
        return path

    # 提取文件
    def pull_file(self, srcpath, destpath=''):
        result, error = self.popen(
            'adb -s {}:{} pull {} {}'.format(self.ip, self.port, srcpath, destpath))
        print(result, error)
        return result, error

    # 传送文件
    def push_file(self, srcpath, destpath=''):
        result, error = self.popen(
            'adb -s {}:{} push {} {}'.format(self.ip, self.port, srcpath, destpath))
        print(result, error)
        return result, error

    # 停止
    def stop(self):
        self.stop_flag = True

    # 执行系统命令
    def popen(self, order):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # 执行命令
        process = subprocess.Popen(order, stdin=subprocess.PIPE, shell=True, startupinfo=startupinfo,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        result = process.stdout.read()
        process.stdout.close()
        error = process.stderr.read()
        process.stderr.close()

        # 输出运行结果
        # print(result)
        # 若程序没有异常，则只输出空行
        # print(error)

        # 返回运行结果
        return result, error

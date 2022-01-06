import logging
import os
import sys
from json import JSONDecodeError
from threading import Thread
from typing import Optional, Callable

import wx

from config_file import ConfigFile
from renamer import Renamer
from scaner import Scaner
from scraper import Locale, CachedScraper
from my_frame import MyFrame
from wx_log_handler import EVT_WX_LOG_EVENT, WxLogHandler

VERSION = '0.1.0'


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        """
        当接收到用户拖拽的文件时，运行 renamer
        """
        dirname_list = [filename for filename in filenames if os.path.isdir(filename)]
        self.window.thread_it(self.window.run_renamer, dirname_list)
        return True


class AppFrame(MyFrame):
    def __init__(self, parent):
        MyFrame.__init__(self, parent)

        # 使文件能被拖拽到 wx.TextCtrl 组件
        drop_target = MyFileDropTarget(self)
        self.text_ctrl.SetDropTarget(drop_target)

        # 配置文件
        config_file_path = os.path.join('config.json')
        self.__config_file = ConfigFile(config_file_path)

        # 工作线程。耗时长的任务应放在工作线程执行，避免阻塞 GUI 线程
        self.__worker_thread: Optional[Thread] = None

        # 为 logger 添加 wxLogHandler
        self.text_ctrl.Bind(EVT_WX_LOG_EVENT, self.on_log_event)
        wx_log_handler = WxLogHandler(self.text_ctrl)
        wx_log_handler.setLevel(logging.INFO)
        wx_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        Renamer.logger.addHandler(wx_log_handler)

    def thread_it(self, func: Callable, *args):
        """
        将函数打包进线程执行
        """
        if self.__worker_thread and self.__worker_thread.is_alive():
            return
        self.__worker_thread = Thread(target=func, args=args)
        self.__worker_thread.start()

    def on_log_event(self, event):
        """
        转发日志到 wx.TextCtrl 组件
        """
        if event.levelno <= logging.INFO:
            text_color = wx.BLACK
        elif event.levelno <= logging.WARNING:
            text_color = wx.BLUE
        else:
            text_color = wx.RED
        self.text_ctrl.SetDefaultStyle(wx.TextAttr(text_color))
        msg = event.message.strip("\r") + "\n"
        self.text_ctrl.AppendText(msg)
        event.Skip()

    def on_dir_changed_event(self, event):
        """
        当 wx.DirPickerCtrl 组件接收到用户选择的文件夹时，运行 renamer
        """
        root_path = self.dir_picker.GetPath()
        self.thread_it(self.run_renamer, [root_path])

    def __print_info(self, message: str):
        self.text_ctrl.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.text_ctrl.AppendText(message + '\n')

    def __print_warning(self, message: str):
        self.text_ctrl.SetDefaultStyle(wx.TextAttr(wx.BLUE))
        self.text_ctrl.AppendText(message + '\n')

    def __print_error(self, message: str):
        self.text_ctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
        self.text_ctrl.AppendText(message + '\n')

    def __before_worker_thread_start(self):
        thread_id = self.__worker_thread.native_id  # 线程 ID
        self.__print_info(f'******************************运行开始({thread_id})******************************')
        self.dir_picker.Disable()  # 禁用【浏览】按钮
        self.text_ctrl.SetDropTarget(None)  # 禁用文件拖拽

    def __before_worker_thread_end(self):
        self.dir_picker.Enable()  # 恢复【浏览】按钮
        self.text_ctrl.SetDropTarget(MyFileDropTarget(self))  # 恢复文件拖拽
        thread_id = self.__worker_thread.native_id  # 线程 ID
        self.__print_info(f'******************************运行结束({thread_id})******************************\n\n')

    def run_renamer(self, root_path_list: list[str]):
        self.__before_worker_thread_start()

        try:
            config = self.__config_file.load_config()  # 从配置文件中读取配置
        except JSONDecodeError as err:
            self.__print_error(f'配置文件解析失败："{os.path.normpath(self.__config_file.file_path)}"')
            self.__print_error(f'JSONDecodeError: {str(err)}')
            self.__before_worker_thread_end()
            return
        except FileNotFoundError as err:
            self.__print_error(f'配置文件加载失败："{os.path.normpath(self.__config_file.file_path)}"')
            self.__print_error(f'FileNotFoundError: {err.strerror}')
            self.__before_worker_thread_end()
            return

        # 检查配置是否合法
        strerror_list = ConfigFile.verify_config(config)
        if len(strerror_list) > 0:
            self.__print_error(f'配置文件验证失败："{os.path.normpath(self.__config_file.file_path)}"')
            for strerror in strerror_list:
                self.__print_error(strerror)
            self.__before_worker_thread_end()
            return

        # 配置 scaner
        scaner_max_depth = config['scaner_max_depth']
        scaner = Scaner(max_depth=scaner_max_depth)

        # 配置 scraper
        scraper_locale = config['scraper_locale']
        scraper_http_proxy = config['scraper_http_proxy']
        if scraper_http_proxy:
            proxies = {
                'http': scraper_http_proxy,
                'https': scraper_http_proxy
            }
        else:
            proxies = None
        scraper_connect_timeout = config['scraper_connect_timeout']
        scraper_read_timeout = config['scraper_read_timeout']
        scraper_sleep_interval = config['scraper_sleep_interval']
        cached_scraper = CachedScraper(
            locale=Locale[scraper_locale],
            connect_timeout=scraper_connect_timeout,
            read_timeout=scraper_read_timeout,
            sleep_interval=scraper_sleep_interval,
            proxies=proxies)

        # 配置 renamer
        renamer = Renamer(
            scaner=scaner,
            scraper=cached_scraper,
            template=config['renamer_template'],
            exclude_square_brackets_in_work_name_flag=config['renamer_exclude_square_brackets_in_work_name_flag'])

        # 执行重命名
        for root_path in root_path_list:
            renamer.rename(root_path)

        self.__before_worker_thread_end()


def get_application_path():
    """
    https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#run-time-information
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # running in a PyInstaller bundle
        application_path = sys._MEIPASS
    else:
        # running in a normal Python process
        application_path = os.path.dirname(__file__)
    return application_path


if __name__ == '__main__':
    app_path = get_application_path()
    icon_path = os.path.join(app_path, 'Letter_R_blue.ico')

    app = wx.App(False)
    frame = AppFrame(None)
    frame.SetIcon(wx.Icon(icon_path))
    frame.SetTitle(f'DLSite 同人作品重命名工具 v{VERSION}')
    frame.Show(True)
    # start the applications
    app.MainLoop()

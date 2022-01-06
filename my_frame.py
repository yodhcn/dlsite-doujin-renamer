# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc


###########################################################################
## Class MyFrame
###########################################################################

class MyFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.static_text = wx.StaticText(self, wx.ID_ANY, u"Tip：手动选择文件夹或拖拽文件夹到软件窗口", wx.DefaultPosition, wx.DefaultSize,
                                         0)
        self.static_text.Wrap(-1)
        box_sizer.Add(self.static_text, 0, wx.ALL | wx.EXPAND, 5)

        self.text_ctrl = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                     wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_RICH2 | wx.HSCROLL | wx.TE_AUTO_URL)
        box_sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        self.dir_picker = wx.DirPickerCtrl(self, wx.ID_ANY, '',
                                           u"Select a folder", wx.DefaultPosition, wx.DefaultSize,
                                           wx.DIRP_DIR_MUST_EXIST)
        box_sizer.Add(self.dir_picker, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(box_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.dir_picker.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_dir_changed_event)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def on_dir_changed_event(self, event):
        event.Skip()

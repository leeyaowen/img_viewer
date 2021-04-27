import wx
import numpy as np
import os
import ctypes
from PIL import Image


class SegWindow(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='Seg', size=(850, 650),
                          style=wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION)
        self.Center()
        panel = SegPanel(self)


class SegPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour((240, 240, 240))

        self.dirdlgBtn = wx.Button(self, label='Select Image', pos=(10, 20), size=(150, 30))
        self.PhotoMaxSize = 500
        self.NewW = self.PhotoMaxSize
        self.NewH = self.PhotoMaxSize

        img = wx.Image(self.PhotoMaxSize, self.PhotoMaxSize)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY,
                                         wx.Bitmap(img),
                                         pos=(10, 70))
        self.dirdlgBtn.Bind(wx.EVT_BUTTON, self.ondir)
        self.imageCtrl.Bind(wx.EVT_MOUSE_EVENTS, self.movemouseXY)

        self.setdpiAwarenessBtn = wx.Button(self, label='Set DPI Awareness', pos=(180, 20), size=(150, 30))
        self.setdpiAwarenessBtn.Bind(wx.EVT_BUTTON, self.setdpiAwareness)

        self.labelX = wx.StaticText(self, label='', pos=(10, 580), size=(50, -1), style=wx.ALIGN_CENTRE)
        self.labelY = wx.StaticText(self, label='', pos=(65, 580), size=(50, -1), style=wx.ALIGN_CENTRE)
        self.labelX.SetBackgroundColour('white')
        self.labelY.SetBackgroundColour('white')
        self.photosize = wx.StaticText(self, label='', pos=(125, 580), size=(200, -1), style=wx.ALIGN_CENTRE)
        self.photosize.SetBackgroundColour('white')

        self.seglist = wx.TextCtrl(self, pos=(520, 70), size=(250, 500), style=wx.TE_MULTILINE)
        self.imageCtrl.Bind(wx.EVT_MOUSE_EVENTS, self.onclick)
        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.onclick)

        self.photoexist = False

    def ondir(self, event):
        self.dlg = wx.FileDialog(self, 'Choose a file:',
                                 wildcard='pictures (*.png)|*.png',
                                 style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if self.dlg.ShowModal() == wx.ID_OK:
            self.filepath = self.dlg.GetPath()
            self.filename = os.path.basename(self.filepath)
            print('You chose %s' % os.path.splitext(self.filename)[0])
            self.npyfile = np.load(file='%s/%s_raw_prob.npy' % (self.filepath[:-len(self.filename)],
                                                                os.path.splitext(self.filename)[0][:-5]))
        self.dlg.Destroy()

        try:
            self.onview()
        except Exception as e:
            print('no file!')

        try:
            self.labelList = list()
            for i in range(0, 20):
                self.npimg = self.npyfile[-1, :self.H, :self.W, i]
                self.labelList.append(np.array(Image.fromarray(self.npimg).resize((int(self.NewW),
                                                                                   int(self.NewH)),
                                                                                   Image.BICUBIC)))
            print('W x H = %s x %s' % (self.NewW, self.NewH))
            print('img.shape=%s' % str(self.labelList[0].shape))
            print(self.labelList[1][211, 436])
        except Exception as e:
            print('img error!: %s' % e)

    def onview(self):
        filepath = self.filepath
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        self.W = img.GetWidth()
        self.H = img.GetHeight()
        if self.W < self.PhotoMaxSize & self.H < self.PhotoMaxSize:
            self.NewW = self.W
            self.NewH = self.H
        else:
            if self.W > self.H:
                self.NewW = self.PhotoMaxSize
                self.NewH = self.PhotoMaxSize * self.H / self.W
            else:
                self.NewH = self.PhotoMaxSize
                self.NewW = self.PhotoMaxSize * self.W / self.H
        img = img.Scale(self.NewW, self.NewH)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()
        self.photosize.SetLabel('photo size = %s x %s' % (str(int(self.NewW)), str(int(self.NewH))))
        self.photoexist = True

    def onclick(self, event):
        if self.photoexist:
            try:
                X = int(self.labelX.GetLabel())
                Y = int(self.labelY.GetLabel())
                if X >= 0 & X <= int(self.NewH) & Y <= int(self.NewW) & Y >= 0:
                    self.seglist.SetValue('(%s, %s)\n'
                                          'background: %s\n'
                                          'bicycle: %s\n'
                                          'bus: %s\n'
                                          'car: %s\n'
                                          'truck: %s\n'
                                          'cat: %s\n'
                                          'dog: %s\n'
                                          'motorcycle: %s\n'
                                          'person: %s\n'
                                          'pottedplant: %s\n'
                                          'train: %s\n'
                                          'sky: %s\n'
                                          'tree: %s\n'
                                          'grass: %s\n'
                                          'building: %s\n'
                                          'trafficlight: %s\n'
                                          'firehydrant: %s\n'
                                          'stopsign: %s\n'
                                          'parkingmeter: %s\n'
                                          'ignore: %s'
                                          % (self.labelX.GetLabel(),
                                             self.labelY.GetLabel(),
                                             str(round(self.labelList[0][Y, X], 2)),
                                             str(round(self.labelList[1][Y, X], 2)),
                                             str(round(self.labelList[2][Y, X], 2)),
                                             str(round(self.labelList[3][Y, X], 2)),
                                             str(round(self.labelList[4][Y, X], 2)),
                                             str(round(self.labelList[5][Y, X], 2)),
                                             str(round(self.labelList[6][Y, X], 2)),
                                             str(round(self.labelList[7][Y, X], 2)),
                                             str(round(self.labelList[8][Y, X], 2)),
                                             str(round(self.labelList[9][Y, X], 2)),
                                             str(round(self.labelList[10][Y, X], 2)),
                                             str(round(self.labelList[11][Y, X], 2)),
                                             str(round(self.labelList[12][Y, X], 2)),
                                             str(round(self.labelList[13][Y, X], 2)),
                                             str(round(self.labelList[14][Y, X], 2)),
                                             str(round(self.labelList[15][Y, X], 2)),
                                             str(round(self.labelList[16][Y, X], 2)),
                                             str(round(self.labelList[17][Y, X], 2)),
                                             str(round(self.labelList[18][Y, X], 2)),
                                             str(round(self.labelList[19][Y, X], 2)),))
            except Exception as e:
                print('img error!: %s' % e)
        event.Skip()

    def setdpiAwareness(self, event):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

    def movemouseXY(self, event):
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.labelX.SetLabel(str(x-10))
        self.labelY.SetLabel(str(y-70))
        if x-10 < 0:
            self.labelX.SetLabel(str(0))
        elif x-10 > self.NewW:
            self.labelX.SetLabel(str(int(self.NewW)))
        if y-70 < 0:
            self.labelY.SetLabel(str(0))
        elif y-70 > self.NewH:
            self.labelY.SetLabel(str(int(self.NewH)))
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    frame = SegWindow(None)
    frame.Show(True)
    app.MainLoop()

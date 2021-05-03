import wx
import numpy as np
import os
import ctypes
from PIL import Image
import glob


labelname = ['background',
             'bicycle',
             'bus',
             'car',
             'truck',
             'cat',
             'dog',
             'motorcycle',
             'person',
             'pottedplant',
             'train',
             'sky',
             'tree',
             'grass',
             'building',
             'trafficlight',
             'firehydrant',
             'stopsign',
             'parkingmeter',
             'ignore']


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

        self.PhotoMaxSize = 500
        self.NewW = self.PhotoMaxSize
        self.NewH = self.PhotoMaxSize
        self.picPaths = list()
        self.currentPicture = 0
        self.totalPictures = 0

        self.dirdlgBtn = wx.Button(self, label='Select Image', pos=(10, 20), size=(150, 30))

        img = wx.Image(self.PhotoMaxSize, self.PhotoMaxSize)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY,
                                         wx.Bitmap(img),
                                         pos=(10, 70))

        self.setdpiAwarenessBtn = wx.Button(self, label='Set DPI Awareness', pos=(180, 20), size=(150, 30))
        self.preBtn = wx.Button(self, label='上一張', pos=(350, 20), size=(150, 30))
        self.nextBtn = wx.Button(self, label='下一張', pos=(520, 20), size=(150, 30))

        self.labelX = wx.StaticText(self, label='', pos=(10, 580), size=(50, -1), style=wx.ALIGN_CENTRE)
        self.labelY = wx.StaticText(self, label='', pos=(65, 580), size=(50, -1), style=wx.ALIGN_CENTRE)
        self.photosize = wx.StaticText(self, label='', pos=(125, 580), size=(200, -1), style=wx.ALIGN_CENTRE)
        self.namebox = wx.StaticText(self, label='', pos=(350, 580), size=(300, -1), style=wx.ALIGN_CENTRE)
        self.labelX.SetBackgroundColour('white')
        self.labelY.SetBackgroundColour('white')
        self.photosize.SetBackgroundColour('white')
        self.namebox.SetBackgroundColour('white')

        self.seglist = wx.TextCtrl(self, pos=(520, 70), size=(250, 500), style=wx.TE_MULTILINE)

        self.dirdlgBtn.Bind(wx.EVT_BUTTON, self.ondir)
        self.preBtn.Bind(wx.EVT_BUTTON, self.onPrevious)
        self.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)
        self.imageCtrl.Bind(wx.EVT_MOUSE_EVENTS, self.onclick)
        self.setdpiAwarenessBtn.Bind(wx.EVT_BUTTON, self.setdpiAwareness)

        self.photoexist = False
        self.npyexist = False

    def ondir(self, event):
        self.dlg = wx.FileDialog(self, 'Choose a file:',
                                 wildcard='pictures (*.png)|*.png',
                                 style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if self.dlg.ShowModal() == wx.ID_OK:
            self.filepath = self.dlg.GetPath()
            self.filename = os.path.basename(self.filepath)
            # print('You chose %s' % (os.path.splitext(self.filename)[0]))
        self.dlg.Destroy()
        self.dirname = self.filepath[:-len(self.filename)]
        self.picPaths = glob.glob('%s*.png' % self.dirname)
        self.totalPictures = len(self.picPaths)

        try:
            self.loadimg(self.filepath)
            self.addnpyarr(self.filepath, self.filename)
            self.showfilename(self.filepath)
        except Exception as e:
            print('no file!')

    def addnpyarr(self, filepath, filename):
        try:
            self.npyfile = np.load(file='%s/%s_raw_prob.npy' % (filepath[:-len(filename)],
                                                                os.path.splitext(filename)[0][:-5]))
            self.labelList = list()
            for i in range(0, 20):
                self.npimg = self.npyfile[-1, :self.H, :self.W, i]
                self.labelList.append(np.array(Image.fromarray(self.npimg).resize((int(self.NewW),
                                                                                   int(self.NewH)),
                                                                                   Image.BICUBIC)))
            self.npyexist = True
            # print('W x H = %s x %s' % (self.NewW, self.NewH))
            # print('img.shape=%s' % str(self.labelList[0].shape))
        except Exception as e:
            print('img error!: %s' % e)

    def loadimg(self, filepath):
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
        img = img.Scale(int(self.NewW), int(self.NewH))
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()
        self.photosize.SetLabel('photo size = %s x %s' % (str(int(self.NewW)), str(int(self.NewH))))
        self.photoexist = True
        self.npyexist = False

    def showfilename(self, filepath):
        self.namebox.SetLabel(os.path.basename(filepath))

    def onclick(self, event):
        x, y = self.ScreenToClient(wx.GetMousePosition())
        self.labelX.SetLabel(str(x - 10))
        self.labelY.SetLabel(str(y - 70))
        if x - 10 < 0:
            self.labelX.SetLabel(str(0))
        elif x - 10 > self.NewW:
            self.labelX.SetLabel(str(int(self.NewW)))
        if y - 70 < 0:
            self.labelY.SetLabel(str(0))
        elif y - 70 > self.NewH:
            self.labelY.SetLabel(str(int(self.NewH)))

        if self.photoexist & self.npyexist:
            try:
                X = int(self.labelX.GetLabel())
                Y = int(self.labelY.GetLabel())
                self.seglist.SetValue('(%s, %s)\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      '%s: %s\n'
                                      % (self.labelX.GetLabel(), self.labelY.GetLabel(),
                                         labelname[0], str(round(self.labelList[0][Y, X], 2)),
                                         labelname[1], str(round(self.labelList[1][Y, X], 2)),
                                         labelname[2], str(round(self.labelList[2][Y, X], 2)),
                                         labelname[3], str(round(self.labelList[3][Y, X], 2)),
                                         labelname[4], str(round(self.labelList[4][Y, X], 2)),
                                         labelname[5], str(round(self.labelList[5][Y, X], 2)),
                                         labelname[6], str(round(self.labelList[6][Y, X], 2)),
                                         labelname[7], str(round(self.labelList[7][Y, X], 2)),
                                         labelname[8], str(round(self.labelList[8][Y, X], 2)),
                                         labelname[9], str(round(self.labelList[9][Y, X], 2)),
                                         labelname[10], str(round(self.labelList[10][Y, X], 2)),
                                         labelname[11], str(round(self.labelList[11][Y, X], 2)),
                                         labelname[12], str(round(self.labelList[12][Y, X], 2)),
                                         labelname[13], str(round(self.labelList[13][Y, X], 2)),
                                         labelname[14], str(round(self.labelList[14][Y, X], 2)),
                                         labelname[15], str(round(self.labelList[15][Y, X], 2)),
                                         labelname[16], str(round(self.labelList[16][Y, X], 2)),
                                         labelname[17], str(round(self.labelList[17][Y, X], 2)),
                                         labelname[18], str(round(self.labelList[18][Y, X], 2)),
                                         labelname[19], str(round(self.labelList[19][Y, X], 2)),))
            except Exception as e:
                print('img error!: %s' % e)

    def nextPicture(self):
        if self.currentPicture == self.totalPictures - 1:
            self.currentPicture = 0
        else:
            self.currentPicture += 1
        self.loadimg(self.picPaths[self.currentPicture])
        self.addnpyarr(self.picPaths[self.currentPicture], os.path.basename(self.picPaths[self.currentPicture]))
        if not self.npyexist:
            self.seglist.SetValue('No data!!!')
        else:
            self.seglist.SetValue('')
        self.showfilename(self.picPaths[self.currentPicture])

    def onNext(self, event):
        if self.photoexist:
            self.nextPicture()

    def previousPicture(self):
        if self.currentPicture == 0:
            self.currentPicture = self.totalPictures - 1
        else:
            self.currentPicture -= 1
        self.loadimg(self.picPaths[self.currentPicture])
        self.addnpyarr(self.picPaths[self.currentPicture], os.path.basename(self.picPaths[self.currentPicture]))
        if not self.npyexist:
            self.seglist.SetValue('No data!!!')
        else:
            self.seglist.SetValue('')
        self.showfilename(self.picPaths[self.currentPicture])

    def onPrevious(self, event):
        if self.photoexist:
            self.previousPicture()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_PAGEUP:
            if self.photoexist:
                self.nextPicture()
        elif keycode == wx.WXK_PAGEDOWN:
            if self.photoexist:
                self.previousPicture()
        self.imageCtrl.SetFocus()
        event.Skip()

    def setdpiAwareness(self, event):
        ctypes.windll.shcore.SetProcessDpiAwareness(2)


if __name__ == '__main__':
    app = wx.App()
    frame = SegWindow(None)
    frame.Show(True)
    app.MainLoop()

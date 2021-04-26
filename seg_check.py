import wx
import os


class SegWindow(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title='Seg', size=(950, 650),
                          style=wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION)
        self.Center()
        panel = SegPanel(self)


class SegPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour((240, 240, 240))
        self.currentDirectory = os.getcwd()

        dirdlgBtn = wx.Button(self, label="Select Image", pos=(10, 20), size=(150, 30))
        dirdlgBtn.Bind(wx.EVT_BUTTON, self.ondir)
        self.PhotoMaxSize = 500

        img = wx.Image(500, 500)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY,
                                         wx.Bitmap(img),
                                         pos=(10, 70))

    def ondir(self, event):
        self.dlg = wx.FileDialog(self, 'Choose a file:',
                            wildcard='pictures (*.jpg,*.png)|*.jpg;*.png',
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if self.dlg.ShowModal() == wx.ID_OK:
            print('You chose %s' % self.dlg.GetPath())
            self.filepath = self.dlg.GetPath()

        self.dlg.Destroy()
        try:
            self.onview()
        except Exception as e:
            print('no file!')

    def onview(self):
        filepath = self.filepath
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()


if __name__ == '__main__':
    app = wx.App()
    frame = SegWindow(None)
    frame.Show(True)
    app.MainLoop()

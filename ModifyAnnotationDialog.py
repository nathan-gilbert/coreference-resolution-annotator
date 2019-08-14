'''
Created on Oct 17, 2011

@author: ngilbert
'''
import wx

class ModifyAnnotationDialog(wx.Dialog):
    '''
    classdocs
    '''
    def __init__(self, parent, title, annotID, annots):
        '''
        Constructor
        '''
        self.annots = annots
        self.index = annotID
        self.annot = annots.getList()[annotID]

        super(ModifyAnnotationDialog, self).__init__(parent=parent, title=title, size=(250, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.textLabel = wx.StaticText(self, label="Text: " + self.annot.getText()) 
        self.id_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.idLabel = wx.StaticText(self, label="ID: ")
        self.idBox = wx.TextCtrl(self, -1, size=(100, -1))
        self.idBox.SetValue(str(self.annot.getID()))
        self.id_sizer.Add(self.idLabel)
        self.id_sizer.Add(self.idBox)
        self.ref_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.refLabel = wx.StaticText(self, label="Ref: ")
        self.refBox = wx.TextCtrl(self, -1, size=(100, -1))
        self.refBox.SetValue(self.annot.getATTR("REF"))
        self.ref_sizer.Add(self.refLabel)
        self.ref_sizer.Add(self.refBox)
        #semantics 
        #self.SEMANTIC = ["ORG", "PER", "LOC", "GPE", "DATE", "Other"]
        #self.SemRadioBox = wx.RadioBox(self,
        #    label="SEMANTIC:",
        #    choices=self.SEMANTIC,
        #    majorDimension=6,
        #    style=wx.RA_SPECIFY_COLS)
        #self.SemRadioBox.SetSelection(self.SEMANTIC.index(self.annot.getATTR("Semantic")))

        #self.TYPE = ["NAM", "NOM", "PRO"]
        #self.TypeRadioBox = wx.RadioBox(self,
                                        #label="TYPE:",
                                        #choices=self.TYPE,
                                        #majorDimension=3,
                                        #style=wx.RA_SPECIFY_COLS)
        #self.TypeRadioBox.SetSelection(self.TYPE.index(self.annot.getATTR("Type")))

        #button sizers 
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        saveButton = wx.Button(self, label='Save')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(saveButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(self.textLabel)
        vbox.Add(self.id_sizer)
        vbox.Add(self.ref_sizer)
        #vbox.Add(self.SemRadioBox)
        #vbox.Add(self.TypeRadioBox)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        saveButton.Bind(wx.EVT_BUTTON, self.OnSave)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnSave(self, e):
        self.annot.setProp("ID", self.idBox.GetValue().strip())

        ref = self.refBox.GetValue().strip()
        if ref == "":
            self.annot.setProp("REF", self.refBox.GetValue().strip())
            self.annot.setProp("CorefID", self.idBox.GetValue().strip())
        else:
            self.annot.setProp("REF", self.refBox.GetValue().strip())
            for a in self.annots:
                if str(a.getID) == ref:
                    self.annot.setProp("CorefID", a.getATTR("CorefID"))

        #self.annot.setProp("Semantic", self.SEMANTIC[self.SemRadioBox.GetSelection()])
        #self.annot.setProp("Type", self.TYPE[self.TypeRadioBox.GetSelection()])
        self.annots.getList()[self.index] = self.annot
        self.OnClose(e)

    def OnClose(self, e):
        self.Destroy()

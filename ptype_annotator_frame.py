#!/usr/bin/python
# File Name : ptype_annotator_frame.py
# Purpose : 
# Creation Date : 6-05-2012
# Last Modified : Wed 06 Jun 2012 10:02:04 AM MDT
# Created By : Nathan Alan Gilbert
import wx
import os
import re
import string

from pyconcile import annotation
from pyconcile import annotation_set

class AnnotatorFrame(wx.Frame):
    '''
    classdocs
    '''

    def __init__(self, parent, title):
        '''
        Constructor
        '''
        # --- initialize file settings
        self.fileList = []
        self.dirName = ""
        self.fileName = ""
        self.fullText = ""
        self.min = ""
        self.head_start = -1
        self.head_end = -1
        self.annots = annotation_set.AnnotationSet("annots")
        self.annotFileName = ""
        self.curr_id = 0
        self.curr_ref = -1
        self.COLS = ["Number", "ID", "Span", "Type", "Full Text"]
        self.CLASS = ["Team", "Player", "Game", "Coach", "Inanimate"]

        wx.Frame.__init__(self, parent, title=title, size=(600, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        #self.text_box_left = wx.TextCtrl(self, size=wx.Size(300, 400),
        #                      style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.list_box_left = wx.ListCtrl(self, size=wx.Size(300, 400),
                                         style=wx.LC_HRULES | wx.LC_REPORT)

        self.setUpListCtrl()
        #for header in self.COLS:
        #    self.list_box_left.InsertColumn(self.COLS.index(header), header)

        self.text_box_right = wx.TextCtrl(self, size=wx.Size(300, 400),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_box_sizer.Add(self.text_box_right, 1, wx.GROW)
        self.text_box_sizer.Add(self.list_box_left, 2, wx.GROW)

        #forms
        self.form_sizer = wx.BoxSizer(wx.VERTICAL)

        self.idLabel = wx.StaticText(self, label="Current ID: " + str(self.curr_id))
        self.SemRadioBox = wx.RadioBox(self,
            label="Profile Type:",
            choices=self.CLASS,
            majorDimension=6,
            style=wx.RA_SPECIFY_COLS)

        self.saveButton = wx.Button(self, label="Add Annotation")
        self.delButton = wx.Button(self, label="Delete Annotation")
        self.showAllButton = wx.Button(self, label="Show All Annotations")
        self.showNoButton = wx.Button(self, label="Show No Annotations")

        self.form_sizer_p = wx.BoxSizer(wx.HORIZONTAL)
        self.form_sizer_p.Add(self.saveButton)
        self.form_sizer_p.Add(self.delButton)
        self.form_sizer_p.Add(self.showAllButton)
        self.form_sizer_p.Add(self.showNoButton)

        #self.form_sizer.Add(self.form_sizer_p)
        self.form_sizer.Add(self.idLabel)
        self.form_sizer.Add(self.SemRadioBox)
        self.form_sizer.Add(self.form_sizer_p)

        self.main_sizer.Add(self.text_box_sizer, 1, wx.GROW)
        self.main_sizer.Add(self.form_sizer)
        self.SetSizerAndFit(self.main_sizer)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuFile = filemenu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Opens an existing file")
        filemenu.AppendSeparator()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        self.Bind(wx.EVT_MENU, self.OnFileOpen, menuFile)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_BUTTON, self.OnAddAnnotButton, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self.OnDelButton, self.delButton)
        self.Bind(wx.EVT_BUTTON, self.OnShowAllButton, self.showAllButton)
        self.Bind(wx.EVT_BUTTON, self.OnShowNoButton, self.showNoButton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListClick)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def OnShowAllButton(self, e):
        for a in self.annots:
            self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("red", "white"))
        self.text_box_right.Update()

    def OnShowNoButton(self, e):
        for a in self.annots:
            self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("black", "white"))
        self.text_box_right.Update()

    def OnListClick(self, e):
        index = self.list_box_left.GetFirstSelected()
        ptype = self.annots.getList()[index].getATTR("TYPE")

        for a in self.annots:
            if a.getATTR("TYPE") == ptype:
                self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("blue", "white"))
            else:
                self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("black", "white"))
        self.text_box_right.Update()

    def setFileList(self, fl):
        inFile = open(fl, 'r')
        self.fileList = [x for x in map(string.strip, inFile.readlines()) if x.startswith("#")]

    def writeAnnotations(self):
        try:
            outFile = open(self.dirName + "/" + self.annotFileName, 'w')
            id = 0
            for annot in self.annots:
                line = "%d\t%d,%d\tstring\tCOREF\t%s\tText=\"%s\"\n" % (id, annot.getStart(), annot.getEnd(), annot.getProps2String(), annot.getText())
                id += 1
                outFile.write(line)
            outFile.close()
        except IOError:
            print("Error, unable to write annotations file.")

    def OnDelButton(self, e):
        index = self.list_box_left.GetFirstSelected()
        id = self.annots.getList()[index].getID()
        ref = self.annots.getList()[index].getATTR("REF")
        self.annots.remove(index)
        self.updateListCtrl()
        self.writeAnnotations()

    def OnAddAnnotButton(self, e):
        span = list(map(int, self.text_box_right.GetSelection()))
        #print span
        new_text = self.fullText[span[0]:span[1]].replace("\n", " ")
        semantic = self.CLASS[self.SemRadioBox.GetSelection()]
        attr = {"ID" : self.curr_id, "TYPE" : semantic}
        new_annot = annotation.Annotation(span[0], span[1], attr.get("ID"), attr, new_text)
        self.annots.add(new_annot)
        self.updateListCtrl()
        self.curr_id += 1
        self.idLabel.SetLabel("Current ID:" + str(self.curr_id))
        self.idLabel.Update()
        #write the annotations out to file
        self.writeAnnotations()

    def setUpListCtrl(self):
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)
        self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        #self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
        #self.list_box_left.SetColumnWidth(6, wx.LIST_AUTOSIZE_USEHEADER)
        #self.list_box_left.SetColumnWidth(7, wx.LIST_AUTOSIZE_USEHEADER)

    def updateListCtrl(self):
        self.list_box_left.ClearAll()
        self.setUpListCtrl()
        index = 0
        for annot in self.annots:
            self.list_box_left.InsertStringItem(index, str(index))
            self.list_box_left.SetStringItem(index, 1, str(annot.getID()))
            self.list_box_left.SetStringItem(index, 2, "%d,%d" % (annot.getStart(), annot.getEnd()))
            self.list_box_left.SetStringItem(index, 3, annot.getATTR("TYPE"))
            self.list_box_left.SetStringItem(index, 4, annot.getText())
            index += 1

        if len(self.annots) > 0:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            #self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE)
            #self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE)
        else:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            #self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
            #self.list_box_left.SetColumnWidth(6, wx.LIST_AUTOSIZE_USEHEADER)

    def readInAnnots(self, lines):
        #self.annots = annotation_set.AnnotationSet("annots")
        SPAN = re.compile('(\d+),(\d+)')
        ID = re.compile('ID="([^"]*)\"')
        TEXT = re.compile('.*Text="([^"]*)\".*')
        COREF = re.compile('.*CorefID="([^"]*)\".*')
        CAT = re.compile('.*Category="([^"]*)\".*')
        REF = re.compile('.*Ref="([^"]*)\".*')
        REF2 = re.compile('.*REF="([^"]*)\".*')
        SEM = re.compile('.*TYPE="([^"]*)\".*')
        SEM2 = re.compile('.*Type="([^"]*)\".*')
        MOD = re.compile('.*Mod="([^"]*)\".*')
        MOD2 = re.compile('.*Modifier="([^"]*)\".*')
        MIN = re.compile('.*Min="([^"]*)\".*')
        #NP_TYPE = re.compile('.*Type="([^"]*)\".*')
        HEAD_START = re.compile('.*HEAD_START="([^"]*)\".*')
        HEAD_END = re.compile('.*HEAD_END="([^"]*)\".*')

        for line in lines:
            if line.startswith("#"):
                continue

            attr = {}
            match = SPAN.search(line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))

            match = ID.search(line)
            if match:
                annot_id = int(match.group(1))
                attr["ID"] = match.group(1)

            match = TEXT.search(line)
            if match:
                text = match.group(1)

            match = COREF.search(line)
            if match:
                attr["CorefID"] = match.group(1)

            match = CAT.search(line)
            if match:
                category = match.group(1)
                attr["category"] = category

            match = MIN.search(line)
            if match:
                attr["Min"] = match.group(1)

            #match = NP_TYPE.search(line)
            #if match:
            #    attr["Type"] = match.group(1)

            match = REF.search(line)
            if match:
                ref = match.group(1)
                attr["REF"] = ref

            match = REF2.search(line)
            if match:
                ref = match.group(1)
                attr["REF"] = ref

            match = HEAD_END.search(line)
            if match:
                attr["HEAD_END"] = match.group(1)

            match = HEAD_START.search(line)
            if match:
                attr["HEAD_START"] = match.group(1)

            match = SEM.search(line)
            if match:
                semantic = match.group(1)
                attr["TYPE"] = semantic
            else:
                match = SEM2.search(line)
                if match:
                    semantic = match.group(1)
                    attr["TYPE"] = semantic

            match = MOD.search(line)
            if match:
                modifier = match.group(1)
                attr["Modifier"] = modifier
            else:
                match = MOD2.search(line)
                if match:
                    modifier = match.group(1)
                    attr["Modifier"] = modifier
            annot = annotation.Annotation(start, end, annot_id, attr, text)
            self.annots.add(annot)
        self.curr_id = len(self.annots)
        self.idLabel.SetLabel("Current ID:" + str(self.curr_id))

    def _readInLines(self):
        #read in text file
        try:
            f = file(os.path.join(self.dirName, self.fileName), 'r')
            self.fullText = ''.join(f.readlines())
            self.text_box_right.SetValue(self.fullText)
            #self.SetTitle("The Annotator" + " - [" + self.fileName + "]")
            #self.SetStatusText("Opened file: " + str(self.text_box_right.GetLastPosition()) + 
            #                   " characters.", SB_INFO)
            #self.ShowPos()
            f.close()
        except:
            print("text file not found")
            #self.PushStatusText("Error in opening file.", wx.SB_INFO)

        annotDirName = "annotations"
        annotFileName = "type_annots"
        self.annotFileName = annotDirName + "/" + annotFileName
        annotLines = []

        try:
            f = file(os.path.join(self.dirName, self.annotFileName), 'r')
            annotLines = f.readlines()
            f.close()
        except:
            #dir or file not found.
            if not os.path.isdir(self.dirName + "/" + annotDirName):
                os.mkdir(self.dirName + "/" + annotDirName)
                annotsFile = open(self.dirName + "/" + annotDirName + "/" + annotFileName, 'w')
                annotsFile.close()
            else:
                if not os.path.isfile(annotDirName + "/" + annotFileName):
                    annotsFile = open(self.dirName + "/" + annotDirName + "/" + annotFileName, 'w')
                    annotsFile.close()
        return annotLines

    def LoadFile(self, filename, dirname):
        self.fileName = filename
        self.dirName = dirname
        self.readInAnnots(self._readInLines())
        self.updateListCtrl()

    def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Text Files (*.txt)|*.txt|All Files|*.*", wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            self.readInAnnots(self._readInLines())
            self.updateListCtrl()
        dlg.Destroy()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small annotator for the Reconcile system.", "About Teh Annotator", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, e):
        self.writeAnnotations()
        self.Close(True)  # Close the frame.

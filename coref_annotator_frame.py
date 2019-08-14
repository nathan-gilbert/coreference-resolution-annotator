#!/usr/bin/python
# File Name : coref_annotator_frame.py
# Purpose : Coreference annotation software for use with Reconcile
# Creation Date : 7-27-2011
# Last Modified : Mon 03 Jun 2013 02:07:35 PM MDT
# Created By : Nathan Alan Gilbert
import wx
import os
import re
import string

from ModifyAnnotationDialog import ModifyAnnotationDialog

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
        #self.dirName = "/home/ngilbert/xspace/data/profile"
        self.dirName = "."
        self.fileName = ""
        self.fullText = ""
        self.min = ""
        self.head_start = -1
        self.head_end = -1
        self.annots = annotation_set.AnnotationSet("annots")
        self.annotFileName = ""
        self.curr_id = 0
        self.used_ids = []
        self.curr_ref = -1
        self.COLS = ["Number", "ID", "Span", "REF", "Min", "Full Text"]

        wx.Frame.__init__(self, parent, title=title, size=(600, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        self.list_box_left = wx.ListCtrl(self, size=wx.Size(300, 400),
                                         style=wx.LC_HRULES | wx.LC_REPORT)

        self.setUpListCtrl()
        #for header in self.COLS:
        #    self.list_box_left.InsertColumn(self.COLS.index(header), header)

        self.text_box_right = wx.TextCtrl(self, size=wx.Size(300, 400),
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.text_box_sizer.Add(self.text_box_left, 2, wx.GROW)
        self.text_box_sizer.Add(self.text_box_right, 1, wx.GROW)
        self.text_box_sizer.Add(self.list_box_left, 2, wx.GROW)

        #forms
        self.form_sizer = wx.BoxSizer(wx.VERTICAL)

        #self.propLabel = wx.StaticText(self, label="Property: ")
        #self.propTextCtrl = wx.TextCtrl(self, value="")
        self.idLabel = wx.StaticText(self, label="Current ID: " + str(self.curr_id))


        self.refLabel = wx.StaticText(self, label="Ref ID: ")
        self.ref_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.refBox = wx.TextCtrl(self, -1, size=(100, -1))
        self.clearRefButton = wx.Button(self, label="Clear")
        self.ref_sizer.Add(self.refBox)
        self.ref_sizer.Add(self.clearRefButton)

        self.minLabel = wx.StaticText(self, label="Min: None")
        self.minButton = wx.Button(self, label="Add Minimum")

        #self.SEMANTIC = ["ORG", "PER", "LOC", "GPE", "DATE", "Other"]
        #self.SemRadioBox = wx.RadioBox(self,
        #    label="SEMANTIC:",
        #    choices=self.SEMANTIC,
        #    majorDimension=6,
        #    style=wx.RA_SPECIFY_COLS)
        #self.TYPE = ["NAM", "NOM", "PRO"]
        #self.TypeRadioBox = wx.RadioBox(self,
        #                                label="Type:",
        #                                choices=self.TYPE,
        #                                majorDimension=3,
        #                                style=wx.RA_SPECIFY_COLS)
        self.saveButton = wx.Button(self, label="Add Annotation")
        self.modifyAnnotButton = wx.Button(self, label="Modify Annotation")
        self.delButton = wx.Button(self, label="Delete Annotation")
        self.showAllButton = wx.Button(self, label="Show All Annotations")
        self.showNoButton = wx.Button(self, label="Show No Annotations")

        self.form_sizer_p = wx.BoxSizer(wx.HORIZONTAL)
        self.form_sizer_p.Add(self.saveButton)
        self.form_sizer_p.Add(self.modifyAnnotButton)
        self.form_sizer_p.Add(self.delButton)
        self.form_sizer_p.Add(self.showAllButton)
        self.form_sizer_p.Add(self.showNoButton)

        #self.form_sizer.Add(self.form_sizer_p)
        self.form_sizer.Add(self.idLabel)
        self.form_sizer.Add(self.refLabel)
        self.form_sizer.Add(self.ref_sizer)
        # self.form_sizer.Add(self.refBox)
        self.form_sizer.Add(self.minLabel)
        self.form_sizer.Add(self.minButton)
        #self.form_sizer.Add(self.SemRadioBox)
        #self.form_sizer.Add(self.TypeRadioBox)
        self.form_sizer.Add(self.form_sizer_p)

        #self.form_sizer.Add(self.saveButton)

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
        self.Bind(wx.EVT_BUTTON, self.OnMinButton, self.minButton)
        self.Bind(wx.EVT_BUTTON, self.OnDelButton, self.delButton)
        self.Bind(wx.EVT_BUTTON, self.OnShowAllButton, self.showAllButton)
        self.Bind(wx.EVT_BUTTON, self.OnShowNoButton, self.showNoButton)
        self.Bind(wx.EVT_BUTTON, self.OnRefClear, self.clearRefButton)
        self.Bind(wx.EVT_BUTTON, self.OnModifyAnnotationButton, self.modifyAnnotButton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnListClick)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def OnRefClear(self, e):
        self.refBox.SetValue("")
        self.refLabel.Update()

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
        coref_id = self.annots.getList()[index].getATTR("CorefID")

        for a in self.annots:
            if a.getATTR("CorefID") == coref_id:
                #update the text
                self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("blue", "white"))
            else:
                self.text_box_right.SetStyle(a.getStart(), a.getEnd(), wx.TextAttr("black", "white"))
        self.text_box_right.Update()

    def setFileList(self, fl):
        inFile = open(fl, 'r')
        self.fileList = filter(lambda x : x.startswith("#"), map(string.strip, inFile.readlines()))

    def writeAnnotations(self):
        outFile = open(self.dirName + "/" + self.annotFileName, 'w')
        id = 0
        for annot in self.annots:
            line = "%d\t%d,%d\tstring\tCOREF\t%s\tText=\"%s\"\n" % (id, annot.getStart(), annot.getEnd(), annot.getProps2String(), annot.getText())
            id += 1
            outFile.write(line)
        outFile.close()

    def OnModifyAnnotationButton(self, e):
        index = self.list_box_left.GetFirstSelected()

        #make the changes
        modDialog = ModifyAnnotationDialog(None, "Modify Annotation", index, self.annots)
        modDialog.ShowModal()
        modDialog.Destroy()
        self.updateListCtrl()
        self.writeAnnotations()

    def OnMinButton(self, e):
        span = map(int, self.text_box_right.GetSelection())
        self.min = self.fullText[span[0]:span[1]].replace("\n", " ")
        self.head_start = span[0]
        self.head_end = span[1]
        self.minLabel.SetLabel("Min: %s" % self.min)
        self.minLabel.Update()

    def OnDelButton(self, e):
        index = self.list_box_left.GetFirstSelected()
        id = self.annots.getList()[index].getID()
        ref = self.annots.getList()[index].getATTR("REF")
        self.annots.remove(index)

        first = True
        prevID = -1

        self.min = ""
        self.head_start = -1
        self.head_end = -1

        for a in self.annots:
            if a.getATTR("REF") == str(id):
                if first:
                    #we need to change this guys index
                    if ref == "":
                        a.setProp("REF", "")
                    else:
                        a.setProp("REF", ref)

                    prevID = a.getID()
                    first = False
                else:
                    a.setProp("REF", prevID)
        self.updateListCtrl()
        self.writeAnnotations()

    def OnAddAnnotButton(self, e):
        span = map(int, self.text_box_right.GetSelection())
        #print span
        new_text = self.fullText[span[0]:span[1]].replace("\n", " ")
        #semantic = self.SEMANTIC[self.SemRadioBox.GetSelection()]
        #type = self.TYPE[self.TypeRadioBox.GetSelection()]
        reference = self.refBox.GetValue()

        #set the head to be the full span if never selected 
        if self.head_start == -1:
            self.head_start = span[0]
        if self.head_end == -1:
            self.head_end = span[1]

        if reference == "":
            coref_id = self.curr_id
        else:
            for a in self.annots:
                if str(a.getID()) == reference:
                    coref_id = a.getATTR("CorefID")

        #new_annot = "%d\t %d,%d\tstring\tCategory=\"%s\"\tSEMANTIC=\"%s\"\tMod=\"%s\"\tText=\"%s\"\n" \
        #    % (self.curr_id, span[0], span[1] - 1, category, semantic, self.modifier, new_text)

        attr = {"REF" : reference, "ID" : self.curr_id, "CorefID" : coref_id,
                "HEAD_START" : self.head_start, "HEAD_END" : self.head_end}

        self.used_ids.append(self.curr_id)

        if self.min != "":
            attr["Min"] = self.min

        new_annot = annotation.Annotation(span[0], span[1], attr.get("ID"), attr, new_text)
        #str_span = "%s,%s" % (span[0], span[1] - 1)
        #props = "Category=\"%s\"\tSEMANTIC=\"%s\"\tMod=\"%s\"\tText=\"%s\"" % (category, semantic, self.modifier, new_text)
        #new_annot = [str(self.curr_id), str_span, props]
        #self.annotList.append(new_annot)
        self.annots.add(new_annot)
        self.updateListCtrl()
        #for e in new_annot:
        #    self.list_box_left.InsertItem(self.curr_id, new_annot.index(e), e)
        #self.text_box_left.SetValue(''.join(self.annotList))
        #self.text_box_left.Update()
        self.curr_id += 1

        #increment till we find an open id #
        while self.curr_id in self.used_ids:
            self.curr_id += 1

        self.idLabel.SetLabel("Current ID:" + str(self.curr_id))
        self.idLabel.Update()
        self.refBox.SetValue(str(self.curr_id - 1))
        self.minLabel.SetLabel("Min: None")
        self.minLabel.Update()
        self.min = ""
        self.head_start = -1
        self.head_end = -1
        #write the annotations out to file
        self.writeAnnotations()

    def setUpListCtrl(self):
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)
        self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
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
            self.list_box_left.SetStringItem(index, 3, annot.getATTR("REF"))
            #self.list_box_left.SetStringItem(index, 4, annot.getATTR("Semantic"))
            #self.list_box_left.SetStringItem(index, 4, annot.getATTR("Type"))
            self.list_box_left.SetStringItem(index, 4, annot.getATTR("Min"))
            self.list_box_left.SetStringItem(index, 5, annot.getText())
            #for e in annot:
                #print e
            #    self.list_box_left.SetStringItem(self.annotList.index(annot), annot.index(e) + 1, e)
            index += 1

        if len(self.annots) > 0:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            #self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE)
        else:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
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
        SEM = re.compile('.*SEMANTIC="([^"]*)\".*')
        SEM2 = re.compile('.*Semantic="([^"]*)\".*')
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
                self.used_ids.append(int(match.group(1)))

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
                attr["Semantic"] = semantic
            else:
                match = SEM2.search(line)
                if match:
                    semantic = match.group(1)
                    attr["Semantic"] = semantic

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
        while self.curr_id in self.used_ids:
            self.curr_id += 1

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
            print "text file not found"
            #self.PushStatusText("Error in opening file.", wx.SB_INFO)

        annotDirName = "annotations"
        annotFileName = "coref_annots"
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

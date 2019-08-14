'''
Created on Jul 27, 2011

@author: ngilbert
'''
import wx
import os
import re

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
        self.dirName = ""
        self.fileName = ""
        self.fullText = ""
        self.modifier = ""
        #self.annotList = []
        self.annots = annotation_set.AnnotationSet("annots")
        self.annotFileName = ""
        self.curr_id = 0
        self.COLS = ["Number", "ID", "Span", "Category", "Semantic", "Modifier", "Full Text"]
        
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
       
        #sizer code 
        #text boxes
    
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.text_box_sizer.Add(self.text_box_left, 2, wx.GROW)
        self.text_box_sizer.Add(self.list_box_left, 2, wx.GROW)
        self.text_box_sizer.Add(self.text_box_right, 1, wx.GROW)
        
        #forms
        self.form_sizer = wx.BoxSizer(wx.VERTICAL)
        
        #self.propLabel = wx.StaticText(self, label="Property: ")
        #self.propTextCtrl = wx.TextCtrl(self, value="")
        self.idLabel = wx.StaticText(self, label="Current ID: " + str(self.curr_id))
        self.modLabel = wx.StaticText(self, label="Modifier: None")
        self.modButton = wx.Button(self, label="Add Modifiers")
        
        self.CATEGORY = ["SUPER", "MAIN", "SUB"]
        self.SEMANTIC = ["ORG", "PER"]
        self.SemRadioBox = wx.RadioBox(self,
            label="SEMANTIC:",
            choices=self.SEMANTIC,
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS)
        self.TypeRadioBox = wx.RadioBox(self,
            label="CATEGORY:",
            choices=self.CATEGORY,
            majorDimension=3,
            style=wx.RA_SPECIFY_COLS)
        
        
        self.saveButton = wx.Button(self, label="Add Annotation")
        self.delButton = wx.Button(self, label="Delete Annotation")
        self.form_sizer_p = wx.BoxSizer(wx.HORIZONTAL)
        self.form_sizer_p.Add(self.saveButton)
        self.form_sizer_p.Add(self.delButton)
        
        #self.form_sizer.Add(self.form_sizer_p)
        self.form_sizer.Add(self.idLabel)
        self.form_sizer.Add(self.modLabel)
        self.form_sizer.Add(self.modButton)
        self.form_sizer.Add(self.SemRadioBox)
        self.form_sizer.Add(self.TypeRadioBox)
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
        self.Bind(wx.EVT_BUTTON, self.OnModButton, self.modButton)
        self.Bind(wx.EVT_BUTTON, self.OnDelButton, self.delButton)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
    
    def writeAnnotations(self):
        outFile = open(self.dirName + "/" + self.annotFileName, 'w')
        id = 0
        for annot in self.annots:
            line = "%d\t%d,%d%s\tText=\"%s\"\n" % (id, annot.getStart(), annot.getEnd(), annot.getProps2String(), annot.getText())
            id += 1
            outFile.write(line)
        outFile.close()
        
    def OnModButton(self, e):
        span = map(int, self.text_box_right.GetSelection())
        self.modifier = self.fullText[span[0]:span[1]].replace("\n", " ")
        self.modLabel.SetLabel("Modifier: %s" % self.modifier)
        self.modLabel.Update()
    
    def OnDelButton(self, e):
        index = self.list_box_left.GetFirstSelected()
        self.annots.remove(index)
        self.updateListCtrl()
        self.writeAnnotations()
        
    def OnAddAnnotButton(self, e):
        span = map(int, self.text_box_right.GetSelection())
        #print span
        new_text = self.fullText[span[0]:span[1]].replace("\n", " ")
        category = self.CATEGORY[self.TypeRadioBox.GetSelection()]
        semantic = self.SEMANTIC[self.SemRadioBox.GetSelection()]
        
        #new_annot = "%d\t %d,%d\tstring\tCategory=\"%s\"\tSEMANTIC=\"%s\"\tMod=\"%s\"\tText=\"%s\"\n" \
        #    % (self.curr_id, span[0], span[1] - 1, category, semantic, self.modifier, new_text)
       
        attr = {"Category" : category, "Semantic" : semantic, "Modifier" : self.modifier} 
        new_annot = annotation.Annotation(span[0], span[1], self.curr_id, attr, new_text)
       
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
        self.idLabel.SetLabel("Current ID:" + str(self.curr_id))
        self.idLabel.Update()
        self.modLabel.SetLabel("Modifier: None")
        self.modLabel.Update()
        self.modifier = ""
        
        #write the annotations out to file
        self.writeAnnotations()
       
    def setUpListCtrl(self):
        for header in self.COLS:
            self.list_box_left.InsertColumn(self.COLS.index(header), header)
        self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_box_left.SetColumnWidth(6, wx.LIST_AUTOSIZE_USEHEADER)
        
    def updateListCtrl(self):
        self.list_box_left.ClearAll()
        self.setUpListCtrl()
        index = 0
        for annot in self.annots:
            self.list_box_left.InsertStringItem(index, str(index))
            self.list_box_left.SetStringItem(index, 1, str(annot.getID()))
            self.list_box_left.SetStringItem(index, 2, "%d,%d" % (annot.getStart(), annot.getEnd()))
            self.list_box_left.SetStringItem(index, 3, annot.getATTR("Category"))
            self.list_box_left.SetStringItem(index, 4, annot.getATTR("Semantic"))
            self.list_box_left.SetStringItem(index, 5, annot.getATTR("Modifier"))
            self.list_box_left.SetStringItem(index, 6, annot.getText())
            #for e in annot:
                #print e
            #    self.list_box_left.SetStringItem(self.annotList.index(annot), annot.index(e) + 1, e)
            index += 1

        if len(self.annots) > 0:                
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE)
            self.list_box_left.SetColumnWidth(6, wx.LIST_AUTOSIZE)
        else:
            self.list_box_left.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
            self.list_box_left.SetColumnWidth(6, wx.LIST_AUTOSIZE_USEHEADER)
        
    def readInAnnots(self, lines):
        #self.annots = annotation_set.AnnotationSet("annots")
        SPAN = re.compile('(\d+),(\d+)')
        ID = re.compile('^(\d+)\s+')
        TEXT = re.compile('.*Text="([^"]*)\".*')   
        CAT = re.compile('.*Category="([^"]*)\".*')   
        SEM = re.compile('.*SEMANTIC="([^"]*)\".*')   
        SEM2 = re.compile('.*Semantic="([^"]*)\".*')   
        MOD = re.compile('.*Mod="([^"]*)\".*')   
        MOD2 = re.compile('.*Modifier="([^"]*)\".*')   
        
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
                
            match = TEXT.search(line)
            if match:
                text = match.group(1)
                
            match = CAT.search(line)
            if match:
                category = match.group(1)
                attr["Category"] = category
                
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
    
    def OnFileOpen(self, e):
        """ File|Open event - Open dialog box. """
        dlg = wx.FileDialog(self, "Open", self.dirName, self.fileName,
                           "Text Files (*.txt)|*.txt|All Files|*.*", wx.OPEN)
        
        if (dlg.ShowModal() == wx.ID_OK):
            self.fileName = dlg.GetFilename()
            self.dirName = dlg.GetDirectory()
            self.annotFileName = "annotations/cats"
            
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
                print "file not found"
                #self.PushStatusText("Error in opening file.", SB_INFO)
                
            #try:
            f = file(os.path.join(self.dirName, self.annotFileName), 'r')
            annotLines = f.readlines()
            f.close()
            
            self.readInAnnots(annotLines)
            self.updateListCtrl()
                #self.text_box_left.SetValue(''.join(self.annotList))
            #except:
            #    print "annot file not found."
                
        dlg.Destroy()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small annotator for the Reconcile system.", "About Teh Annotator", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self, e):
        self.Close(True)  # Close the frame.


import Tkinter as tk

class AskSave(tk.Frame):
    def __init__(self, guiObject):    
        self.guiObject = guiObject
        self.parent = tk.Toplevel()
        tk.Frame.__init__(self, self.parent)
        self.parent.title("Save changes?")
        self.pack()
        self.loadUI()
        
    def loadUI(self):
        self.infoLabel = tk.Label(self, text="If you don't save, any unsaved changes will be lost.")
        self.cwoSavingButton = tk.Button(self, text="Close without saving", command=self.cwoSaving)
        self.cancelButton = tk.Button(self, text="Cancel", command=self.cancel)
        self.saveButton = tk.Button(self, text="Save", command=self.save)
        self.infoLabel.pack()
        self.cwoSavingButton.pack(side=tk.LEFT)
        self.cancelButton.pack(side=tk.LEFT)
        self.saveButton.pack(side=tk.LEFT)
        
    def cwoSaving(self):
        for i in self.guiObject.displayedEntryList:
            i.destroy()
        for i in self.guiObject.displayedAllList:
            i.destroy()
        self.guiObject.fileDict = {}
        self.guiObject.modified = False
        self.guiObject.fileMenu.entryconfig("Save", state=tk.DISABLED)
        self.guiObject.fileMenu.entryconfig("Save As", state=tk.DISABLED)
        self.guiObject.fileMenu.entryconfig("Load", state=tk.NORMAL)
        self.guiObject.fileMenu.entryconfig("Import", state=tk.NORMAL)
        self.guiObject.fileMenu.entryconfig("Close", state=tk.DISABLED)
        self.guiObject.partsFrame.grid_forget()
        self.parent.destroy()
        
    def cancel(self):
        self.parent.destroy()
            
    def save(self):
        self.guiObject.fileS()
        for i in self.guiObject.displayedEntryList:
            i.destroy()
        for i in self.guiObject.displayedAllList:
            i.destroy()
        self.guiObject.fileDict = {}
        self.guiObject.modified = False
        self.guiObject.fileMenu.entryconfig("Save", state=tk.DISABLED)
        self.guiObject.fileMenu.entryconfig("Save As", state=tk.DISABLED)
        self.guiObject.fileMenu.entryconfig("Load", state=tk.NORMAL)
        self.guiObject.fileMenu.entryconfig("Import", state=tk.NORMAL)
        self.guiObject.fileMenu.entryconfig("Close", state=tk.DISABLED)
        self.guiObject.partsFrame.grid_forget()
        self.parent.destroy()

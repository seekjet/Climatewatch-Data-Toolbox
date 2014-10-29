import Tkinter as tk
import json

class SettingsUI(tk.Frame):
    def __init__(self, parent, guiObject):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title = "Settings"
        self.guiObject = guiObject
        self.needToReloadEntries = False
        self.pack()
        self.loadUI()
        
    def loadUI(self):
        tk.Label(self, text="Maximum number of entries to display per part: ").grid(row=0, column=0, sticky=tk.NW)
        self.maxEntriesScale = tk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL, command=self.callback)
        self.maxEntriesScale.set(self.guiObject.global_config["displayedEntries"])
        self.maxEntriesScale.grid(row=0, column=1, sticky=tk.NW)
        tk.Label(self, text="\nDisplay the following fields:").grid(row=1, column=0, sticky=tk.NW)
        
        self.stateList = []
        for i in range(len(self.guiObject.global_config["headers"])):
            self.stateList.append(tk.IntVar())
            if self.guiObject.global_config["headers"][i] in self.guiObject.global_config["displayedFields"]:
                self.stateList[i].set(True)
            else:
                self.stateList[i].set(False)
                
        for i in range(len(self.stateList)):
            tk.Checkbutton(self, text=self.guiObject.global_config["headers"][i], variable=self.stateList[i], onvalue=True, offvalue=False, command=self.callback).grid(row=i+2, column=0, sticky=tk.NW, padx=50)
            
        rowWeAreUpTo = i+3
        tk.Label(self, text="\nDeveloper options: ").grid(row=rowWeAreUpTo, column=0, sticky=tk.NW)
        rowWeAreUpTo += 1
        self.consoleAllowed = tk.IntVar()
        if self.guiObject.global_config["consoleAllowed"] == "yes":
            self.consoleAllowed.set(True)
        else:
            self.consoleAllowed.set(False)
        tk.Checkbutton(self, text="Enable console: ", variable=self.consoleAllowed, onvalue=True, offvalue=False, command=self.callback).grid(row=rowWeAreUpTo, column=0, sticky=tk.NW, padx=50)
        
        rowWeAreUpTo += 1
        tk.Label(self, text="\n").grid(row=rowWeAreUpTo, column=0, sticky=tk.NW)
        
        rowWeAreUpTo += 1
        tk.Button(self, text="Save settings", command=self.commitSettings).grid(row=rowWeAreUpTo, column=0, padx=50)
        tk.Button(self, text="Cancel", command=self.cancel).grid(row=rowWeAreUpTo, column=1, padx=50)
        
    def callback(self, event=None):
        self.needToReloadEntries = True
        
    def commitSettings(self):
        self.guiObject.global_config["displayedEntries"] = self.maxEntriesScale.get()
        self.guiObject.global_config["displayedFields"] = []
        for i in range(len(self.stateList)):
            if self.stateList[i].get():
                self.guiObject.global_config["displayedFields"].append(self.guiObject.global_config["headers"][i])
        if self.consoleAllowed.get():
            self.guiObject.global_config["consoleAllowed"] = "yes"
            self.guiObject.editMenu.entryconfig("Console", state=tk.NORMAL)
            self.guiObject.editMenu.entryconfig("GUI Console", state=tk.NORMAL)
        else:
            self.guiObject.global_config["consoleAllowed"] = "no"
            self.guiObject.editMenu.entryconfig("Console", state=tk.DISABLED)
            self.guiObject.editMenu.entryconfig("GUI Console", state=tk.DISABLED)
        fp = open("resources/global_config.json", "w")
        json.dump(self.guiObject.global_config, fp)
        fp.close()
        if self.needToReloadEntries:
            self.guiObject.after(500, self.guiObject.reload)
        self.parent.destroy()
        
    def cancel(self):
        self.parent.destroy()

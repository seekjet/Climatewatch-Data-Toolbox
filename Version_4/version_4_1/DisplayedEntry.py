import Tkinter as tk
from PIL import Image, ImageTk
from ExpandImage import ExpandImage
from sys import platform as SYS_PLATFORM

def escape(x):
    res = ""
    for i in x:
        if i == "\\": # If it equals a single backslash.
            res += "\\\\" # Add two backslashes
        else:
            res += i # Add whatever the character was
    return res

if "windows" in SYS_PLATFORM.lower():
    file_delimeter = "\\"
else:
    file_delimeter = "/"

class DisplayedEntry:
    def __init__(self, rootCanvas, rootFrame, innerFrame, row, flagcolor, uid):
        self.rootCanvas = rootCanvas
        self.row = row
        self.rootFrame = rootFrame
        self.innerFrame = innerFrame
        self.uid = uid
        self.width = int(self.rootCanvas.cget("width"))
        self.entryCanvas = tk.Canvas(self.innerFrame, height=64, width=self.width-8)
        self.entryCanvas.grid(row=self.row*2, pady=1, padx=1, sticky=tk.NW)
        self.rootCanvas.configure(scrollregion=self.rootCanvas.bbox(tk.ALL),width=self.width,height=430)
        self.picturePath = "resources/default.png"
        
        self.drawItems(flagcolor)
        
    def drawItems(self, flagcolor):
        self.flagRect = self.entryCanvas.create_rectangle(1,1,16,64, fill=flagcolor, outline="#D9D9D9")
        photo = Image.open(self.picturePath)
        aspectRatio = float(photo.size[0])/float(photo.size[1])
        if aspectRatio < 96.0/64.0:
            photo = photo.resize((int(aspectRatio*64), 64), Image.ANTIALIAS)
        else:
            photo = photo.resize((96, int(96/aspectRatio)), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(photo)
        self.picture = tk.Label(self.entryCanvas, image=photo, width=96, height=64, bg="#000000")
        self.picture.bind("<Button-1>", self.expandImage)
        self.picture.photo = photo
        self.entryCanvas.create_window(20, 0, window=self.picture, anchor=tk.NW)
        self.displayedData = tk.Listbox(self.entryCanvas)
        self.entryCanvas.create_window(120, 0, window=self.displayedData, anchor=tk.NW, width=self.width-210, height=66)
        self.moveButton = tk.Button(self.entryCanvas, text="Move", command=self.move)
        self.entryCanvas.create_window(self.width-8, 64, window=self.moveButton, anchor=tk.SE)
        
        self.updateData(self.rootFrame.master.master.fileDict["entries"][str(self.uid)].keys())
        
    def updateData(self, keyList):
        self.displayedData.delete(0, tk.END)
        data = self.rootFrame.master.master.fileDict["entries"][str(self.uid)]
        for i in keyList:
            # So basically if there is a field that is in the form __fieldName__, it is for us, and not part of the official data.
            if (i[0] + i[1] != "__") or (i[len(i)-1] + i[len(i)-1] != "__"):
                self.displayedData.insert(tk.END, str(i) + ": " + str(data[i]))
        
    def expandImage(self, event):
        imageRoot = tk.Toplevel()
        imageFrame = ExpandImage(imageRoot, self.picturePath)
        imageRoot.mainloop()
        
    def move(self):
        self.rootFrame.master.master.move(self.uid)
    
    def destroy(self):
        self.entryCanvas.destroy()
        del self

import Tkinter as tk
from PIL import Image, ImageTk
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

class ExpandImage(tk.Frame):
    def __init__(self, parent, picturePath):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.parent.title("Climatewatch Data Toolbox - "+self.stripFileName(picturePath))
        
        self.picturePath = picturePath
        self.original = Image.open(escape(self.picturePath))
        self.aspectRatio = float(self.original.size[0])/float(self.original.size[1])
        photo = ImageTk.PhotoImage(self.original)
        self.image = tk.Label(self, image=photo, bg="#000000")
        self.image.photo = photo
        self.image.pack(fill = tk.BOTH, expand = True)
        self.pack(fill = tk.BOTH, expand = True)
        
        self.image.bind("<Configure>", self.updateDimens)
        
    def updateDimens(self, event):
        self.parent.geometry(str(event.width)+"x"+str(event.height))
        if self.aspectRatio < float(event.width)/float(event.height):
            photo = ImageTk.PhotoImage(self.original.resize((int(event.height*self.aspectRatio), event.height)))
        else:
            photo = ImageTk.PhotoImage(self.original.resize((event.width, int(event.width/self.aspectRatio))))
        self.image.config(image=photo)
        self.image.photo = photo
        
    def stripFileName(self, fileName):
        temp = ""
        for i in reversed(fileName):
            if i == file_delimeter:
                break
            else:
                temp = i + temp
        return temp
        
    def __del__(self):
        self.image.destroy()

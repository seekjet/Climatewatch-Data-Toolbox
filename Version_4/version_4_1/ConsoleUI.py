import Tkinter as tk

class ConsoleUI(tk.Frame):
    def __init__(self, parent, guiObject):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.guiObject = guiObject
        
        self.parent.title("Console")
        self.config(bg="#F0F0F0")
        self.instruction = tk.Label(self.parent, text="Enter your command (python code):")
        self.instruction.pack()
        
        self.filler1 = tk.Label(self.parent, text="")
        self.filler1.pack()
        
        self.entryField = tk.Entry(self.parent)
        self.entryField.pack()
        
        self.filler2 = tk.Label(self.parent, text="")
        self.filler2.pack()
        
        self.buttonFrame = tk.Frame(self.parent)
        self.buttonFrame.pack()
        
        self.okButton = tk.Button(self.buttonFrame, text="Execute", command=self.execute)
        self.cancelButton = tk.Button(self.buttonFrame, text="Cancel", command=self.cancel)
        self.okButton.pack(side=tk.LEFT)
        self.cancelButton.pack(side=tk.LEFT)
        
    def execute(self):
        self.guiObject.execute( self.entryField.get() )
        self.parent.destroy()
        
    def cancel(self):
        self.parent.destroy()

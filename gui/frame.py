import tkinter
from tkinter.filedialog import askopenfilename


class Frame:

    def __init__(self, frame, core):
        self.frame = frame
        self.core = core
        self.__initialize()
        

    def __initialize(self):
        self.frame.title("machinerie")
        
        self.load_button = tkinter.Button(self.frame, text="Load", command=self.load)
        self.load_button.pack()

        self.label = tkinter.StringVar()
        self.label.set("NONE")

        self.test_button = tkinter.Button(self.frame, text="Test", command=self.test)
        self.test_button.pack()

        self.test_image = tkinter.Label(self.frame, image=None)
        
        self.current_file_label = tkinter.Label(self.frame, textvariable=self.label)
        self.current_file_label.pack()

    def load(self):
        file = askopenfilename(title="Select a picture", filetypes=[("jpeg files", "*.jpg")])

        if file:
            print("Picture selected")
            self.core.setImage(file)
            print("Picture loaded")
            self.update()

    def update(self):
        self.label.set(self.core.image.path)
        self.current_image = self.core.image.getAsITK()
        self.test_canvas = tkinter.Canvas(self.frame, width=self.core.w(), height=self.core.h())
        self.test_canvas.pack()
        self.test_canvas.create_image(0,0, image=self.current_image, anchor="nw")

    def test(self):
        pl = self.core.stupid_seam_finder()
        
        for p in pl["path"]:
            self.test_canvas.create_oval(p[0]-0.5,p[1]-0.5,p[0]+0.5,p[1]+0.5)
        
        

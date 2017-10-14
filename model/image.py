import cv2
import numpy
import PIL.Image as pimg
import PIL.ImageTk as pimgtk

class Image:

    def __init__(self, path):
        self.path = path
        self.__initialize()

    def __initialize(self):
        self.grid = cv2.imread(self.path)
        self.updateCoordinates()
        print(self.w, self.h)

    def updateCoordinates(self):
        self.w = len(self.grid[0])
        self.h = len(self.grid)
        print("Coordinates:", self.w, ":", self.h)


    def get(self, x, y):
        return self.grid[y][x]
    
    def getAsITK(self):
        newImage = cv2.cvtColor(self.grid, cv2.COLOR_BGR2RGB)
        newImage = pimg.fromarray(newImage)
        return pimgtk.PhotoImage(newImage)

    def removeVerticalSeam(self, path):
        ndarrays = []
        for p in path:
            ndarrays.append(numpy.delete(self.grid[p[1]], p[0], 0))
        self.grid = numpy.array(ndarrays)
        self.updateCoordinates()
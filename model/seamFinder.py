import model.energyCalculator as ec
from model.seamCarvingUtil import *
from itertools import chain
import math
class SeamFinder:

    def __init__(self, image):
        self.image = image

        # Object that will provide the energies.
        self.energyCalculator = ec.EnergyCalculator(image)

        # Grid that will contain, for each pixel, a tuple (seam_energy, (x2,y2)).
        # seam_energy : The energy of the lowest-cost seam that ends to this pixel.
        # (x2,y2) : The upper pixel that belongs to the lowest-cost seam.
        # The grid has the following shape : (width,height).
        self.grid = [[(math.inf, (-1, -1)) for y in range(self.image.h)] for x in range(self.image.w)]

        # Variable used to reduce the amount of computation
        # This variable is updated, each time a new minimal seam is computed.
        # It represents the average of the x-part of each pixel coordinate (x,y) that belongs to the seam.
        # @check SeamFinder.compute_paths documentation for more details.
        self.previous_avg_x = 0

    # Compute, for each pixel, the next pixel to follow to build the lowest-cost vertical seam.
    # This algorithm uses dynamic programming to compute it in a reasonable delay.
    # Pixels in the first row are initialized just with their energies and dummy coordinates.
    #  Starting from the second line, each pixel will look at his 3 upper pixels (top-right, top, top-left).
    # - and will choose the one with the lowest-cost.
    # For easiness reasons, we do not compute any pixel in the most-left/right columns.
    # This algorithm is greedy and uses a variable range for his computations.
    # Therefore when a new seam computation occurs, we only re-compute a small area around this coordinate.
    # This is a greedy choice, but it gives a reasonable result and avoids a lot of useless computations.
    # @check SeamFinder.__avg_x_range for nore details.
    # ! Time consuming operation.
    def compute_paths(self):

        # energies in a local variable for better efficiency
        energy_computed = self.energyCalculator.energyComputed
        grid = self.grid

        # Initialization of the first row
        for x in self.avg_x_range():
            grid[x][0] = (energy_computed[x][0], (-1,-1))

        for y in range(1, self.image.h - 1):
            for x in self.avg_x_range():

                # Energy of the three upper pixels
                e1, e2, e3 = grid[x - 1][y - 1][0], grid[x][y - 1][0], grid[x + 1][y - 1][0]
                e = min(e1, e2, e3)

                # We retrieve the coordinates of the lowest energy
                (x2, y2) = (x, y - 1) if e == e2 else (x + 1, y - 1) if e == e3 else (x - 1, y - 1)

                # Data update
                grid[x][y] = (e + energy_computed[x][y], (x2, y2))

    # Return a greedy Range object used in path computation.
    # The Range returned depends on the previous computed seam.
    # @check SeamFinder.previous_avg_x for more details.
    # If the x-average is 0 - it usually means that it's the first computation
    # - then we returned a classic range(1,width).
    # Else, we make an area around the x-coordinate that represents the pixels which are the most-likely
    # - to change one, or more, seam.
    # In addition, we re-compute the two most-right columns to make sure that they won't lead us to a
    # - non-existent pixel.
    def avg_x_range(self):
        if self.previous_avg_x == 0:
            return range(1, self.image.w-1)
        i = max(1,self.previous_avg_x-self.image.w//3)
        j = min(self.image.w-1,self.previous_avg_x+self.image.w//3)

        j = self.image.w-1
        k = max(j,self.image.w-1-self.image.w//10)
        return chain(range(i,j), range(k,self.image.w-1))

    """
        def f1(energy_computed, grid, y):
            def f2(x):
                e1, e2, e3 = grid[x - 1][y - 1][0], grid[x][y - 1][0], grid[x + 1][y - 1][0]
                e = min(e1, e2, e3)
                (x2, y2) = (x, y - 1) if e == e2 else (x + 1, y - 1) if e == e3 else (x - 1, y - 1)
                grid[x][y] = (e + energy_computed[x][y], (x2, y2))

            return f2

        for y in range(1, self.image.h - 1):
            list(map(f1(energy_computed, grid, y), range(1, self.image.w-1)))
    """

    def stupid_seam_finder(self, b=True):
        pe = {"seam_energy":math.inf, "path":[]}
        pe = self.find_vertical_seams(pe)
        return pe

    # Find and return a low-energy seam.
    # Return a dictionary {"seam_energy", "path"}.
    # seam_energy : The energy of the seam found.
    # path : a list of (x,y) coordinates.
    # ! Time consuming operation
    @timer
    def find_vertical_seams(self, pe):
        self.compute_paths()
        return self.find_vertical_seam()


    # Find and return a low-energy seam.
    # It loops over the pixels in the most-bottom row and takes the pixel with the lowest seam energy.
    # Then it climb the grid and add each pixel to a list. After computation, the list is reversed.
    # This will also update the average x-coordinate. @check SeamFinder.previous_avg_x for more details.
    # Return a dictionary {"seam_energy", "path"}.
    # seam_energy : The energy of the seam found.
    # path : a list of (x,y) coordinates, from top to bottom.
    @timer
    def find_vertical_seam(self):
        # width and height in local variables for better efficiency
        w, h = self.image.w, self.image.h

        grid = self.grid

        min = math.inf
        bottom = (-1,-1)
        for x in range(w):
            cur = self.grid[x][h-2][0]
            if cur < min:
                min = cur
                bottom = (x,h-1)
        #print(bottom)
        path = list()
        #path.append(bottom)
        energy = grid[bottom[0]][bottom[1]][0]
        cur = (bottom[0],bottom[1]-1)
        avg_x = 0
        for i in range(h-2,0,-1):
            x, y = cur[0], cur[1]
            avg_x += x
            path.append((x,y))
            cur = self.grid[x][y][1]

        self.previous_avg_x = avg_x//h
        #path.append()
        path.reverse()
        print(len(path), path[0], path[len(path)-1])
        print(len(self.grid), len(self.grid[0]), self.image.w, self.image.h)

        return {"seam_energy": energy, "path": path}

    # Remove every pixel from the path in the grid.
    # Since the grid is shaped like [column][row], it shifts pixels instead of just popping pixels for each row.
    # If the seam is closer to the right-side of the image, then pixels on the right-side of the seam
    #   - are shifted to the left.
    # Else, pixels on the left-side of the seam is shifted to the right.
    # This is computed with the average x-coordinate. @check SeamFinder.previous_avg_x for more details.
    # This technique, in most cases, should not shift more than half of the pixels.
    @timer
    def remove_vertical_seam(self, path):
        if self.previous_avg_x > self.image.w // 2:
            k = 1
            i = self.image.w - 1
        else:
            k = -1
            i = 0
        for (x,y) in path:
            for i in range(max(0,x),min(x,self.image.w)):
                self.grid[i+k][y] = self.grid[i+k][y]
        self.grid.pop(i)
        self.energyCalculator.remove_vertical_seam(path)
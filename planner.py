#!/bin/python3
import os
from random import randrange
from prettytable import PrettyTable
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from numpy import *
import numpy
import datetime


class HousingObject:
    """
    Represent one housing entity, which has a variable size and following
    structure:

    y/x| 0 1 2 3
    -----------
    0|   0 0 0 0
    1|   0 0 0 0
    2|   0 0 0 0
    """

    def __init__(self, width, length, height):
        self.data = [[[False for i in range(height)] for i in range(length)]
                     for j in range(width)]

    def getBlock(self, width, length, height):
        return self.data[width][length][height]

    def setBlock(self, width, length, height):
        self.data[width][length][height] = True

    def __str__(self):
        res = ""
        for floor in range(len(self.data[0][0])):
            res += " --- {}. Floor ---\n".format(floor)
            for l in range(len(self.data[0])):
                for w in range(len(self.data)):
                    res += "X " if self.getBlock(w, l, floor) else "  "
                res += "\n"


class FloorPlanner:
    def __init__(self, grid_size=10, houseSize=2):
        self.gridSize = grid_size
        self.kernelSize = houseSize
        self.floors = [zeros(shape=(grid_size, grid_size))]

    def groundFloor(self):
        for i in range(self.gridSize // self.kernelSize):
            for j in range(self.gridSize // self.kernelSize):
                x = i * self.kernelSize
                y = j * self.kernelSize
                kernel = \
                    self.floors[0][y:y+self.kernelSize,
                                   x:x+self.kernelSize]
                kernel[randrange(2), randrange(2)] = 1
                self.floors[0][y:y + self.kernelSize, x:x +
                               self.kernelSize] = kernel

    def upperFloor(self):
        def countOf(array, number):
            unique, counts = numpy.unique(array, return_counts=True)
            counter = dict(zip(unique, counts))
            if number not in counter:
                return 0
            else:
                return counter[number]

        self.floors.append(ones(shape=(self.gridSize, self.gridSize)))
        for x in range(self.gridSize - self.kernelSize):
            for y in range(self.gridSize - self.kernelSize):
                previousFloor = self.floors[-2][y:y + self.kernelSize, x:x +
                                                self.kernelSize]
                newFloor = self.floors[-1][y:y + self.kernelSize, x:x +
                                           self.kernelSize]
                if countOf(previousFloor, 0) == 4 and \
                   countOf(newFloor, 1) == 4:
                    foo = zeros(shape=(2, 2))
                    foo[randrange(2), randrange(2)] = 2
                    self.floors[-1][y:y + self.kernelSize, x:x +
                                    self.kernelSize] = foo

    def save(self):
        print("Save generated data...")
        curDir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(curDir, "data")
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        fileName = "floorPlan_{}.npy".format(timestamp)
        f = os.path.join(path, fileName)
        print("Save File: {}".format(f))
        numpy.save(f, self.floors)

    def print(self):
        for idx in range(len(self.floors)):
            print("---- {}. Floor ----".format(idx))
            tb = PrettyTable()
            for i in range(self.gridSize):
                tb.add_row(self.floors[idx][i])
            print(str(tb))

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_balcony = []
        y_balcony = []
        z_balcony = []

        x_free = []
        y_free = []
        z_free = []

        x_house = []
        y_house = []
        z_house = []
        # -> Ground Floor
        for y_idx in range(self.gridSize):
            for x_idx in range(self.gridSize):
                # -> Balcony
                if self.floors[0][y_idx, x_idx] == 1:
                    x_balcony.append(x_idx)
                    y_balcony.append(y_idx)
                    z_balcony.append(0)
                # -> house
                else:
                    x_house.append(x_idx)
                    y_house.append(y_idx)
                    z_house.append(0)

        # -> Upper Floors
        for floor_idx in range(1, len(self.floors)):
            for y_idx in range(self.gridSize):
                for x_idx in range(self.gridSize):
                    # -> Balcony
                    if self.floors[floor_idx][y_idx, x_idx] == 2:
                        x_balcony.append(x_idx)
                        y_balcony.append(y_idx)
                        z_balcony.append(floor_idx)
                    # -> house
                    elif self.floors[floor_idx][y_idx, x_idx] == 0:
                        x_house.append(x_idx)
                        y_house.append(y_idx)
                        z_house.append(floor_idx)
                    else:
                        x_free.append(x_idx)
                        y_free.append(y_idx)
                        z_free.append(floor_idx)

        # -> Balcony
        ax.scatter(x_balcony, y_balcony, z_balcony, c='r')
        # -> House
        ax.scatter(x_house, y_house, z_house, c='b')

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Floor')

        plt.show()


if __name__ == '__main__':
    p = FloorPlanner(10)
    p.groundFloor()
    p.upperFloor()
    p.upperFloor()
    p.print()
    p.plot()
    p.save()

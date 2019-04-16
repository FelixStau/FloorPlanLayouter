#!/bin/python3
from random import randrange
from prettytable import PrettyTable
from numpy import *


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
    def __init__(self, grid_size=10):
        self.gridSize = grid_size
        self.firstFloor = zeros(shape=(grid_size, grid_size))
        self.secondFloor = zeros(shape=(grid_size, grid_size))

    def planFirstFloor(self, amountHousing):
        for n in range(amountHousing):
            x = randrange(self.gridSize)
            y = randrange(self.gridSize)
            print("New Field: {}:{}".format(x, y))
            self.firstFloor[x][y] = 1

    def planSecondFloor(self, kernel_size):
        counter = 1
        for x in range(self.gridSize - kernel_size):
            for y in range(self.gridSize - kernel_size):
                selection = self.firstFloor[y:y + kernel_size, x:x +
                                            kernel_size]
                if count_nonzero(self.firstFloor[y:y+kernel_size,x:x+kernel_size]) == 1 and \
                   count_nonzero(self.secondFloor[y:y+kernel_size, x:x+kernel_size]) == 0:
                    print("Selection: {}".format(selection))
                    print("-> {}:{}".format(x, y))
                    foo = ones(shape=(2, 2))
                    #foo[randrange(2), randrange(2)] = 5
                    foo[:, :] = counter
                    self.secondFloor[y:y + kernel_size, x:x +
                                     kernel_size] = foo
                    print("jey")
                    counter += 1

    def print(self):
        print("---- First Floor ----")
        tb1 = PrettyTable()
        for i in range(self.gridSize):
            tb1.add_row(self.firstFloor[i])
        print(str(tb1))
        print("---- Second Floor ----")
        tb2 = PrettyTable()
        for i in range(self.gridSize):
            tb2.add_row(self.secondFloor[i])
        print(str(tb2))


if __name__ == '__main__':
    p = FloorPlanner(10)
    p.planFirstFloor(40)
    p.planSecondFloor(2)
    p.print()

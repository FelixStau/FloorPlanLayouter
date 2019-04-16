bl_info = {
    "name": "GenericHousing",
    "author": "Mr. Secret",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > GenericHousing",
    "description": "Adds a new Housing Object",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
import numpy as np
from random import randrange


class FloorPlanner:
    def __init__(self, length, width, houseSize=2):
        self.length = length
        self.width = width
        self.kernelSize = houseSize
        self.floors = [np.zeros(shape=(length, width))]

    def groundFloor(self):
        for i in range(self.width // self.kernelSize):
            for j in range(self.length // self.kernelSize):
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
            unique, counts = np.unique(array, return_counts=True)
            counter = dict(zip(unique, counts))
            if number not in counter:
                return 0
            else:
                return counter[number]

        self.floors.append(np.ones(shape=(self.length, self.width)))
        for x in range(self.width - self.kernelSize):
            for y in range(self.length - self.kernelSize):
                previousFloor = self.floors[-2][y:y + self.kernelSize, x:x +
                                                self.kernelSize]
                newFloor = self.floors[-1][y:y + self.kernelSize, x:x +
                                           self.kernelSize]
                if countOf(previousFloor, 0) == 4 and \
                   countOf(newFloor, 1) == 4:
                    foo = np.zeros(shape=(2, 2))
                    foo[randrange(2), randrange(2)] = 2
                    self.floors[-1][y:y + self.kernelSize, x:x +
                                    self.kernelSize] = foo

    def plan(self):
        print("Planning Ground Floor")
        self.groundFloor()
        while not np.all(self.floors[-1]):
            print("Planning Upper Floor")
            self.upperFloor()
        print("Planning - DONE")

    def render(self, paddingX, paddingY, paddingZ, plateSize, cubeSize):
        # -> Ground Floor
        for y_idx in range(self.length):
            for x_idx in range(self.width):
                # -> Balcony
                if self.floors[0][y_idx, x_idx] == 1:
                    cube = bpy.ops.mesh.primitive_plane_add(
                        size=plateSize,
                        location=(x_idx + paddingX * x_idx,
                                  y_idx + paddingY * y_idx, 0))
                # -> house
                else:
                    cube = bpy.ops.mesh.primitive_cube_add(
                        size=cubeSize,
                        location=(x_idx + paddingX * x_idx,
                                  y_idx + paddingY * y_idx, 0))
        # -> Upper Floors
        for floor_idx in range(1, len(self.floors)):
            for y_idx in range(self.length):
                for x_idx in range(self.width):
                    # -> Balcony
                    if self.floors[floor_idx][y_idx, x_idx] == 2:
                        cube = bpy.ops.mesh.primitive_plane_add(
                            size=plateSize,
                            location=(x_idx + paddingX * x_idx,
                                      y_idx + paddingY * y_idx,
                                      floor_idx + paddingZ * floor_idx))
                    # -> house
                    elif self.floors[floor_idx][y_idx, x_idx] == 0:
                        cube = bpy.ops.mesh.primitive_cube_add(
                            size=cubeSize,
                            location=(x_idx + paddingX * x_idx,
                                      y_idx + paddingY * y_idx,
                                      floor_idx + paddingZ * floor_idx))
                    else:
                        pass


class GenericHomePlannerOperator(Operator):
    """Create a new Mesh Object"""
    bl_idname = "mesh.generic_home_planner"
    bl_label = "Add GenericHousing"
    bl_options = {'REGISTER', 'UNDO'}
    plannerInst = None
    oldGridLength = 0
    oldGridWidth = 0
    gridLength = bpy.props.IntProperty(name="Grid Length",
                                       default=10,
                                       min=2,
                                       max=100)
    gridWidth = bpy.props.IntProperty(name="Grid Width",
                                      default=10,
                                      min=2,
                                      max=100)
    paddingX = bpy.props.FloatProperty(name="Padding X",
                                       default=1,
                                       min=0,
                                       max=100)
    paddingY = bpy.props.FloatProperty(name="Padding Y",
                                       default=1,
                                       min=0,
                                       max=100)
    paddingZ = bpy.props.FloatProperty(name="Padding Z",
                                       default=1,
                                       min=0,
                                       max=100)
    plateSize = bpy.props.FloatProperty(name="Plate Size",
                                        default=1.0,
                                        min=1.0,
                                        max=100)
    cubeSize = bpy.props.FloatProperty(name="Cube Size",
                                       default=1.0,
                                       min=1.0,
                                       max=100)

    def execute(self, context):
        if self.oldGridLength != self.gridLength or \
           self.oldGridWidth != self.gridWidth:
            self.report({'INFO'}, "Create new Planner")
            self.plannerInst = FloorPlanner(self.gridLength, self.gridWidth)
            self.report({'INFO'}, "Planning")
            self.plannerInst.plan()
            self.oldGridLength = self.gridLength
            self.oldGridWidth = self.gridWidth
        self.report({'INFO'}, "Render Planning")
        self.plannerInst.render(self.paddingX, self.paddingY, self.paddingZ,
                                self.plateSize, self.cubeSize)
        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Registration


def add_object_button(self, context):
    self.layout.operator(GenericHomePlannerOperator.bl_idname,
                         text="GenericHousing",
                         icon='PLUGIN')


def register():
    bpy.utils.register_class(GenericHomePlannerOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(GenericHomePlannerOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()

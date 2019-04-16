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
    def __init__(self, grid_size=10, houseSize=2):
        self.gridSize = grid_size
        self.kernelSize = houseSize
        self.floors = [np.zeros(shape=(grid_size, grid_size))]

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
            unique, counts = np.unique(array, return_counts=True)
            counter = dict(zip(unique, counts))
            if number not in counter:
                return 0
            else:
                return counter[number]

        self.floors.append(np.ones(shape=(self.gridSize, self.gridSize)))
        for x in range(self.gridSize - self.kernelSize):
            for y in range(self.gridSize - self.kernelSize):
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
        
    def render(self, col):
        # -> Ground Floor
        padding = 2
        for y_idx in range(self.gridSize):
            for x_idx in range(self.gridSize):
                # -> Balcony
                if self.floors[0][y_idx, x_idx] == 1:
                    cube = bpy.ops.mesh.primitive_plane_add(
                        location=(x_idx + padding * x_idx, y_idx + padding * y_idx, 0))
                    #col.objects.link(cube)
                # -> house
                else:
                    cube = bpy.ops.mesh.primitive_cube_add(
                        location=(x_idx + padding * x_idx, y_idx + padding * y_idx, 0))
                    #col.objects.link(cube)

        # -> Upper Floors
        for floor_idx in range(1, len(self.floors)):
            for y_idx in range(self.gridSize):
                for x_idx in range(self.gridSize):
                    # -> Balcony
                    if self.floors[floor_idx][y_idx, x_idx] == 2:
                        cube = bpy.ops.mesh.primitive_plane_add(
                            location=(x_idx + padding * x_idx, y_idx + padding * y_idx, floor_idx + padding * floor_idx))
                        #col.objects.link(cube)
                    # -> house
                    elif self.floors[floor_idx][y_idx, x_idx] == 0:
                        cube = bpy.ops.mesh.primitive_cube_add(
                            location=(x_idx + padding * x_idx, y_idx + padding * y_idx, floor_idx  + padding * floor_idx))
                        #col.objects.link(cube)
                    else:
                        pass


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add GenericHousing"
    bl_options = {'REGISTER', 'UNDO'}
    size = bpy.props.IntProperty(name="Size", default=100, min=10, max=1000)

    scale: FloatVectorProperty(
        name="scale",
        default=(1.0, 1.0, 1.0),
        subtype='TRANSLATION',
        description="scaling",
    )

    def execute(self, context):
        col = bpy.data.collections.new("Housing")
        inst = FloorPlanner(self.size)
        inst.plan()
        mesh = bpy.data.meshes.new(name="GenericHousing")
        inst.render(col)
        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        object_data_add(context, mesh, operator=self)
        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="GenericHousing",
        icon='PLUGIN')


# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()

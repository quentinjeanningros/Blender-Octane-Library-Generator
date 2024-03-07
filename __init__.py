# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import os
from bpy.types import Panel

bl_info = {
    "name": "Octane Library Generator",
    "author": "Quentin Jeanningros",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}

class CUSTOM_PT_Panel(Panel):
    bl_label = "Octane Texture Library Generator"
    bl_idname = "OCTANE_TEXTURE_LIB_GEN_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Octane Lib Gen"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "selected_folder", text="Selected Folder")

        row = layout.row()
        operator = row.operator("object.start_batch", text="End Batch")

class OBJECT_OT_StartBatch(bpy.types.Operator):
    bl_idname = "object.start_batch"
    bl_label = "Start Batch"

    @classmethod
    def poll(cls, context):
        return context.scene.selected_folder and os.path.isdir(context.scene.selected_folder)

    def execute(self, context):
        selected_folder = bpy.context.scene.selected_folder
        if selected_folder:
            self.iterate_subfolders(selected_folder)
        return {'FINISHED'}

    def iterate_subfolders(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for subdir in dirs:
                print(os.path.join(root, subdir))

def register():
    bpy.utils.register_class(CUSTOM_PT_Panel)
    bpy.utils.register_class(OBJECT_OT_StartBatch)
    bpy.types.Scene.selected_folder = bpy.props.StringProperty(subtype="DIR_PATH")

def unregister():
    del bpy.types.Scene.selected_folder
    bpy.utils.unregister_class(OBJECT_OT_StartBatch)
    bpy.utils.unregister_class(CUSTOM_PT_Panel)

if __name__ == "__main__":
    register()
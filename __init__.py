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
from bpy.types import Operator, Panel

bl_info = {
    "name": "Generate Catalogs from Selected Folders",
    "author": "Your Name",
    "description": "Generate catalogs based on selected folders",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "category": "Generic",
}

class CUSTOM_OT_GenerateCatalogs(Operator):
    bl_idname = "custom.generate_catalogs"
    bl_label = "Generate Catalogs"

    def execute(self, context):
        selected_folder = context.scene.selected_folder
        if not selected_folder:
            self.report({'ERROR'}, "Please select a folder.")
            return {'CANCELLED'}

        if not os.path.isdir(selected_folder):
            self.report({'ERROR'}, "Selected folder is not valid.")
            return {'CANCELLED'}

        try:
            self.create_catalogs(selected_folder)
        except RuntimeError:
            self.report({'ERROR'}, "Cannot create catalog. Please select an asset library.")
            return {'CANCELLED'}

        return {'FINISHED'}

    def create_and_rename_catalog(folder_path, desired_catalog_name):
        # Assuming 'parent_path' is derived from 'folder_path' contextually
        parent_path = ''  # This would be set based on your folder_path logic

        # Create the new catalog
        bpy.ops.asset.catalog_new(parent_path=parent_path)

        # Hypothetical code to rename the newly created catalog to 'desired_catalog_name'
        # Note: This is illustrative and not based on current bpy API capabilities
        # You would need to find the created catalog ID or reference first
        catalog_id = 'newly_created_catalog_id'  # Placeholder, not actual code
        bpy.data.asset_catalogs[catalog_id].name = desired_catalog_name
        print(f"Catalog renamed to: {desired_catalog_name}")

    def create_catalogs(self, folder_path):
        root_collection = bpy.context.scene.collection
        if not root_collection:
            root_collection = bpy.data.collections.new("Root")
            bpy.context.scene.collection.children.link(root_collection)

        for root, dirs, _ in os.walk(folder_path):
            # for dir_name in dirs:
            #     catalog_name = os.path.relpath(os.path.join(root, dir_name), folder_path)
            #     parent_path = os.path.dirname(catalog_name)
            #     if parent_path == '.':
            #         parent_path = ''  # For the root folder
            #     bpy.ops.asset.catalog_new(parent_path=parent_path)
            #     print("Created catalog:", catalog_name)

class CUSTOM_PT_GenerateCatalogsPanel(Panel):
    bl_label = "Generate Catalogs"
    bl_idname = "CUSTOM_PT_generate_catalogs"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOLS'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "params")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene, "selected_folder", text="Selected Folder")

        row = layout.row()
        row.operator(CUSTOM_OT_GenerateCatalogs.bl_idname, text="Generate Catalogs")

def menu_func(self, context):
    self.layout.operator(CUSTOM_OT_GenerateCatalogs.bl_idname)

def register():
    bpy.utils.register_class(CUSTOM_OT_GenerateCatalogs)
    bpy.utils.register_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.Scene.selected_folder = bpy.props.StringProperty(subtype="DIR_PATH")
    bpy.types.FILEBROWSER_MT_context_menu.append(menu_func)

def unregister():
    del bpy.types.Scene.selected_folder
    bpy.utils.unregister_class(CUSTOM_OT_GenerateCatalogs)
    bpy.utils.unregister_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.FILEBROWSER_MT_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
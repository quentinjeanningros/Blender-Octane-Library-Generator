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
import re
from pathlib import Path
import uuid


bl_info = {
    "name": "Generate Catalogs from Selected Folders",
    "author": "Your Name",
    "description": "Generate catalogs based on selected folders",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "category": "Generic",
}

def format_material_name(name):
    name = name.replace("_", " ")
    name = re.sub(r"(\d+)", r" \1", name)
    name = re.sub(r"(\D)(\d)", r"\1 \2", name)
    name = re.sub(r"(\B[A-Z])", r" \1", name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def create_octane_universal_material(material):
    # Ensure we're using nodes
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # Clear existing nodes to start fresh
    nodes.clear()

    # Create an Octane Universal Material node
    octane_node = nodes.new(type="ShaderNodeOctUniversalMat")  # This type might need to be adjusted
    octane_node.location = (0, 0)  # Optional: Adjust node position

    # Ensure there's a Material Output node
    material_output = nodes.new('ShaderNodeOutputMaterial')
    material_output.location = (200, 0)  # Optional: Adjust node position

    # Connect the Octane Universal Material node to the Material Output node
    material.node_tree.links.new(octane_node.outputs['OutMat'], material_output.inputs['Surface'])

def create_unique_material(formatted_name):
    # Initialize with the base formatted name
    unique_name = formatted_name
    i = 1  # Start counter for suffixes

    # Loop to find a unique name by appending a number
    while unique_name in bpy.data.materials:
        unique_name = f"{formatted_name}.{str(i).zfill(3)}"  # Append a suffix like .001, .002, etc.
        i += 1

    # Once a unique name is found, create and return the new material
    new_mat = bpy.data.materials.new(name=unique_name)
    new_mat.use_fake_user = True
    new_mat.asset_mark()

    # Create and set up the Octane Universal Material node for the new material
    create_octane_universal_material(new_mat)

    return new_mat
def get_catalog_file_path():
    # Get the directory of the current Blender file
    blend_file_path = Path(bpy.data.filepath)
    if not blend_file_path:
        # Handle the case where the .blend file hasn't been saved yet
        raise FileNotFoundError("Blender file has not been saved. Please save your work before running this script.")

    # Ensure the .blend file's directory exists (it should, but this is for safety)
    if not blend_file_path.parent.exists():
        raise FileNotFoundError("Directory of the Blender file does not exist.")

    # Define the path to the catalog file next to the Blender file
    catalog_file_path = blend_file_path.parent / "blender_assets.cats.txt"
    return catalog_file_path

def get_or_create_catalog(full_path, base_path):
    try:
        catalog_file = get_catalog_file_path()
    except FileNotFoundError as e:
        print(e)
        return None

    if not catalog_file.exists():
        catalog_file.touch()

    # Trim the base path from the full path and exclude the material's own directory
    trimmed_path_parts = Path(full_path).relative_to(base_path).parts[:-1]  # Excludes the last directory
    if not trimmed_path_parts:
        # If there are no directories left after trimming, return None to indicate no catalog should be created
        return None

    with open(catalog_file, "r+", encoding="utf-8") as file:
        existing_catalogs = {line.split(":", 1)[1].strip(): line.split(":", 1)[0] for line in file if ":" in line}
        formatted_path = "/".join([format_material_name(part) for part in trimmed_path_parts])

        if formatted_path in existing_catalogs:
            return existing_catalogs[formatted_path]
        else:
            new_uuid = str(uuid.uuid4())
            file.write(f"{new_uuid}:{formatted_path}\n")
            return new_uuid

class CUSTOM_OT_GenerateShaderCatalog(bpy.types.Operator):
    bl_idname = "custom.generate_catalogs"
    bl_label = "Generate Catalogs"

    def execute(self, context):
        if bpy.context.scene.render.engine != 'octane':
            self.report({'ERROR'}, "This addon requires the Octane render engine.")
            return {'CANCELLED'}

        selected_folder = context.scene.selected_folder

        if not selected_folder:
            self.report({'ERROR'}, "Please select a folder.")
            return {'CANCELLED'}

        if not os.path.isdir(selected_folder):
            self.report({'ERROR'}, "Selected folder is not valid.")
            return {'CANCELLED'}

        self.create_shaders_tree(selected_folder)
        return {'FINISHED'}

    def create_shaders_tree(self, folder_path):
        use_catalog_tree = bpy.context.scene.use_catalog_tree
        use_tags = bpy.context.scene.use_tags

        for root, dirs, files in os.walk(folder_path, topdown=True):
            if use_tags:
                relative_path = Path(root).relative_to(folder_path)
                tags = [format_material_name(part) for part in relative_path.parts]

            for name in dirs:
                formatted_name = format_material_name(name)
                mat = create_unique_material(formatted_name)

                # Only modify blender_assets.cats.txt and set catalog_id if use_catalog_tree is True
                if use_catalog_tree:
                    catalog_id = get_or_create_catalog(os.path.join(root, name), folder_path)
                    if catalog_id:  # Ensure catalog_id is not None before assignment
                        mat.asset_data.catalog_id = catalog_id

                # Add tags from folder structure
                if use_tags:
                    for tag in tags:
                        mat.asset_data.tags.new(tag, skip_if_exists=True)

            self.report({'INFO'}, f"Created new material: {mat.name}" + (f", catalog ID: {catalog_id}" if use_catalog_tree and catalog_id else ""))

class CUSTOM_PT_GenerateCatalogsPanel(bpy.types.Panel):
    bl_label = "Octane Catalog Generator"
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

        # Draw the folder selection UI
        row = layout.row()
        row.prop(scene, "selected_folder", text="Selected Folder")

        # Draw the checkbox for using the catalog tree
        row = layout.row()
        row.prop(scene, "use_catalog_tree", text="Create Catalog Tree")

        # Draw the new checkbox for using tags
        row = layout.row()
        row.prop(scene, "use_tags", text="Create Tags")

        # Draw the button to generate catalogs
        row = layout.row()
        row.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname, text="Generate Catalogs")

def menu_func(self, context):
    self.layout.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname)

def register():
    bpy.utils.register_class(CUSTOM_OT_GenerateShaderCatalog)
    bpy.utils.register_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.Scene.selected_folder = bpy.props.StringProperty(subtype="DIR_PATH")
    bpy.types.Scene.use_catalog_tree = bpy.props.BoolProperty(
        name="Create Catalog Tree",
        description="Create and organize materials into a catalog tree",
        default=True  # Checked by default
    )
    bpy.types.Scene.use_tags = bpy.props.BoolProperty(
        name="Create Tags",
        description="Tag materials based on folder structure",
        default=True  # Checked by default
    )
    bpy.types.FILEBROWSER_MT_context_menu.append(menu_func)

def unregister():
    del bpy.types.Scene.selected_folder
    del bpy.types.Scene.use_catalog_tree
    del bpy.types.Scene.use_tags
    bpy.utils.unregister_class(CUSTOM_OT_GenerateShaderCatalog)
    bpy.utils.unregister_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.FILEBROWSER_MT_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
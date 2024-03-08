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
from .utils.paths import split_into_components, match_files_to_socket_names

bl_info = {
    "name": "Generate Catalogs from Selected Folders",
    "author": "Your Name",
    "description": "Generate catalogs based on selected folders",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "category": "Generic",
}

def create_octane_texture_node(texture):
    #TODO Logic to create an Octane texture node for a given texture file
    # Will vary based on the texture type (e.g., ImageTexture, FloatImageTexture, etc.)
    pass

def connect_texture_to_material(material, texture_node):
    #TODO Logic to connect a texture node to the appropriate input of an Octane material
    pass

def format_material_name(name):
    scene = bpy.context.scene

    # Check if name formatting is enabled
    if not scene.format_name:
        return name

    # Replace specified characters with space
    for char in scene.replace_by_space:
        name = name.replace(char, " ")

    # Add space before capital letters if enabled
    if scene.add_space_by_caps:
        name = re.sub(r"(\B[A-Z])", r" \1", name)

    # Add space between words and numbers if enabled
    if scene.add_space_between_word_and_number:
        name = re.sub(r"(\d+)", r" \1", name)
        name = re.sub(r"(\D)(\d)", r"\1 \2", name)

    name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace

    return name

def create_octane_material_base(material):
    # Ensure we're using nodes
    material.use_nodes = True
    nodes = material.node_tree.nodes

    #TODO Create Octane Universal Material node


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
    create_octane_material_base(new_mat)

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

    def find_textures(self, directory):
        # Prepare sockets based on user settings
        sockets = [
            ['base_color', bpy.context.scene.base_color.split(), None],
            ['metallic', bpy.context.scene.metallic.split(), None],
            ['specular', bpy.context.scene.specular.split(), None],
            ['normal', bpy.context.scene.normal.split(), None],
            ['bump', bpy.context.scene.bump.split(), None],
            ['roughness', bpy.context.scene.roughness.split(), None],
            ['gloss', bpy.context.scene.gloss.split(), None],
            ['displacement', bpy.context.scene.displacement.split(), None],
            ['transmission', bpy.context.scene.transmission.split(), None],
            ['emission', bpy.context.scene.emission.split(), None],
            ['alpha', bpy.context.scene.alpha.split(), None],
            ['ambient_occlusion', bpy.context.scene.ambient_occlusion.split(), None]
        ]

        texture_files = {socket[0]: [] for socket in sockets}  # Initialize texture_files dictionary

        # Collect all files in the directory that match the supported image formats
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tiff')):
                    files.append(type('obj', (object,), {'name': os.path.join(root, filename)}))

        # Match files to sockets
        match_files_to_socket_names(files, sockets)

        # Populate the texture_files dictionary based on matched sockets
        for socket in sockets:
            if socket[2]:  # If files were matched to this socket
                texture_type = socket[0]
                for matched_file_path in socket[2]:  # Iterate through matched files (now directly using the paths)
                    texture_files[texture_type].append(matched_file_path)  # Append the file path directly

        return texture_files

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

                # Find texture files and create Octane texture nodes
                textures = self.find_textures(os.path.join(root, name))
                for texture in textures:
                    print(texture)
                    tex_node = create_octane_texture_node(texture)
                    connect_texture_to_material(mat, tex_node)

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

        # Draw the checkbox for formatting name
        row = layout.row()
        row.prop(scene, "format_name", text="Format Name")

        # Only show additional options if format_name is checked
        if scene.format_name:
            box = layout.box()
            box.prop(scene, "replace_by_space", text="Replace by Space")
            box.prop(scene, "add_space_by_caps", text="Add Space by Caps")
            box.prop(scene, "add_space_between_word_and_number", text="Add Space Between Word and Number")

        layout.separator()

        # UI for texture naming conventions
        layout.label(text="Texture Naming Conventions:")
        box = layout.box()
        box.prop(scene, "base_color")
        box.prop(scene, "metallic")
        box.prop(scene, "specular")
        box.prop(scene, "normal")
        box.prop(scene, "bump")
        box.prop(scene, "roughness")
        box.prop(scene, "gloss")
        box.prop(scene, "displacement")
        box.prop(scene, "transmission")
        box.prop(scene, "emission")
        box.prop(scene, "alpha")
        box.prop(scene, "ambient_occlusion")

        layout.separator()

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
    bpy.types.Scene.format_name = bpy.props.BoolProperty(
        name="Format Name",
        description="Format material names based on rules",
        default=True  # Checked by default
    )
    bpy.types.Scene.replace_by_space = bpy.props.StringProperty(
        name="Replace by Space",
        description="Characters to replace by spaces",
        default="_"  # Default characters
    )
    bpy.types.Scene.add_space_by_caps = bpy.props.BoolProperty(
        name="Add Space by Caps",
        description="Add space before capital letters",
        default=True  # Checked by default
    )
    bpy.types.Scene.add_space_between_word_and_number = bpy.props.BoolProperty(
        name="Add Space Between Word and Number",
        description="Add space between words and numbers",
        default=True  # Checked by default
    )
    bpy.types.Scene.base_color = bpy.props.StringProperty(
        name="Base Color",
        default="diffuse diff albedo base col color basecolor",
        description="Naming Components for Base Color maps"
    )
    bpy.types.Scene.metallic = bpy.props.StringProperty(
        name="Metallic",
        default="metallic metalness metal mtl",
        description="Naming Components for Metallic maps"
    )
    bpy.types.Scene.specular = bpy.props.StringProperty(
        name="Specular",
        default="specularity specular spec spc",
        description="Naming Components for Specular maps"
    )
    bpy.types.Scene.normal = bpy.props.StringProperty(
        name="Normal",
        default="normal nor nrm nrml norm",
        description="Naming Components for Normal maps"
    )
    bpy.types.Scene.bump = bpy.props.StringProperty(
        name="Bump",
        default="bump bmp",
        description="Naming Components for Bump maps"
    )
    bpy.types.Scene.roughness = bpy.props.StringProperty(
        name="Roughness",
        default="roughness rough rgh",
        description="Naming Components for Roughness maps"
    )
    bpy.types.Scene.gloss = bpy.props.StringProperty(
        name="Gloss",
        default="gloss glossy glossiness",
        description="Naming Components for Glossy maps"
    )
    bpy.types.Scene.displacement = bpy.props.StringProperty(
        name="Displacement",
        default="displacement displace disp dsp height heightmap",
        description="Naming Components for Displacement maps"
    )
    bpy.types.Scene.transmission = bpy.props.StringProperty(
        name="Transmission",
        default="transmission transparency",
        description="Naming Components for Transmission maps"
    )
    bpy.types.Scene.emission = bpy.props.StringProperty(
        name="Emission",
        default="emission emissive emit",
        description="Naming Components for Emission maps"
    )
    bpy.types.Scene.alpha = bpy.props.StringProperty(
        name="Alpha",
        default="alpha opacity",
        description="Naming Components for Alpha maps"
    )
    bpy.types.Scene.ambient_occlusion = bpy.props.StringProperty(
        name="Ambient Occlusion",
        default="ao ambient occlusion",
        description="Naming Components for Ambient Occlusion maps"
    )
    bpy.types.FILEBROWSER_MT_context_menu.append(menu_func)

def unregister():
    del bpy.types.Scene.selected_folder
    del bpy.types.Scene.use_catalog_tree
    del bpy.types.Scene.use_tags
    del bpy.types.Scene.base_color
    del bpy.types.Scene.metallic
    del bpy.types.Scene.specular
    del bpy.types.Scene.normal
    del bpy.types.Scene.bump
    del bpy.types.Scene.roughness
    del bpy.types.Scene.gloss
    del bpy.types.Scene.displacement
    del bpy.types.Scene.transmission
    del bpy.types.Scene.emission
    del bpy.types.Scene.alpha
    del bpy.types.Scene.ambient_occlusion
    del bpy.types.Scene.format_name
    del bpy.types.Scene.replace_by_space
    del bpy.types.Scene.add_space_by_caps
    del bpy.types.Scene.add_space_between_word_and_number
    bpy.utils.unregister_class(CUSTOM_OT_GenerateShaderCatalog)
    bpy.utils.unregister_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.FILEBROWSER_MT_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
import bpy
import os
from pathlib import Path
from .utils.materials import create_unique_material
from .utils.catalog import get_or_create_catalog
from .utils.parsing import format_material_name
from .utils.materials import match_files_to_socket_names, create_octane_texture_node, connect_texture_to_material

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


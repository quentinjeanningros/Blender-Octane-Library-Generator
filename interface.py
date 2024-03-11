import bpy
import os
from pathlib import Path
from bpy.props import IntProperty, BoolProperty, StringProperty, EnumProperty, FloatProperty, PointerProperty
from .utils.materials import create_materials_according_settings
from .utils.parsing import format_material_name
from .utils.catalog import get_or_create_catalog, set_material_preview_with_operator
from .utils.render import render_and_save

class CUSTOM_OT_GenerateShaderCatalog(bpy.types.Operator):
    # Metadata about this operator, including its identifier and label
    bl_idname = "custom.generate_catalogs"
    bl_label = "Generate Catalogs"

    def execute(self, context):
        # Implementation of the operator's action.
        # Checks for various preconditions (e.g., correct render engine, valid folder selection) before proceeding.
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

        # Additional checks for the 'Render' preview type, ensuring a valid object is selected for mockups.
        if bpy.context.scene.preview_type == 'Render':
            if not bpy.context.scene.object_mock:
                self.report({'ERROR'}, "Please select an object to mock.")
                return {'CANCELLED'}
            if bpy.context.scene.object_mock.type != 'MESH':
                self.report({'ERROR'}, "Selected object is not a mesh.")
                return {'CANCELLED'}

        self.create_shaders_tree(selected_folder)
        return {'FINISHED'}

    def create_assets(self, name, folder_path, texture_naming_conventions, settings, catalog_id ,tags):
        formatted_name = format_material_name(name)
        data_array = create_materials_according_settings(formatted_name, texture_naming_conventions, settings, folder_path)
        mat_array = []
        for data in data_array:
            mat = data['material']
            if not mat:
                return None
            mat.use_fake_user = True
            mat.asset_mark()

            if catalog_id:
                mat.asset_data.catalog_id = catalog_id

            for tag in tags:
                mat.asset_data.tags.new(tag, skip_if_exists=True)

            # Sets up the material preview based on the provided settings.
            preview_image_path = data['albedo']
            if settings['preview_type'] == 'UseColorMap' and preview_image_path:
                set_material_preview_with_operator(bpy.context, mat, preview_image_path)

            elif settings['preview_type'] == 'Render':
                # For render previews, checks if a rerender is necessary and performs it if so.
                preview_path = os.path.join(folder_path, "preview.png")
                preview_exist = os.path.exists(preview_path)
                if not preview_exist or bpy.context.scene.force_rerender:
                    obj = bpy.context.scene.object_mock
                    if obj.data.materials:
                        obj.data.materials[0] = mat
                    else:
                        obj.data.materials.append(mat)
                    render_and_save(folder_path, "preview", bpy.context.scene.resolution_x, bpy.context.scene.resolution_y)
                set_material_preview_with_operator(bpy.context, mat, preview_path)


            mat_array.append(mat)

        return mat_array

    def create_shaders_tree(self, folder_path):
        use_catalog_tree = bpy.context.scene.use_catalog_tree
        use_tags = bpy.context.scene.use_tags

        # Extracts naming conventions from scene properties
        texture_naming_conventions = {
            "transmission": bpy.context.scene.transmission.split(' '),
            "albedo": bpy.context.scene.albedo.split(' '),
            "ambiant_occlusion": bpy.context.scene.ambiant_occlusion.split(' '),
            "metallic": bpy.context.scene.metallic.split(' '),
            "specular": bpy.context.scene.specular.split(' '),
            "roughness": bpy.context.scene.roughness.split(' '),
            "opacity": bpy.context.scene.opacity.split(' '),
            "bump": bpy.context.scene.bump.split(' '),
            "normal": bpy.context.scene.normal.split(' '),
            "displacement": bpy.context.scene.displacement.split(' '),
            "emission": bpy.context.scene.emission.split(' ')
        }

        # Compiles material and rendering settings from scene properties
        extensions_list = bpy.context.scene.file_type.split(' ')
        extensions_tuple = tuple(['.' + ext for ext in extensions_list])
        settings = {
            "file_types": extensions_tuple,
            "resolution_priority": bpy.context.scene.resolution_priority,
            "alt_col_handling": bpy.context.scene.alt_col_handling,
            "texture_setup": bpy.context.scene.default_texture_setup,
            "displacement_type": bpy.context.scene.texture_setup_displacement,
            "displacement_midlevel": bpy.context.scene.displacement_mid_level,
            "displacement_height": bpy.context.scene.displacement_height,
            "gamma": bpy.context.scene.texture_setup_default_gamma,
            "preview_type": bpy.context.scene.preview_type
        }

        # Formats the folder name and initiates asset creation for the root folder
        folder_name = format_material_name(os.path.basename(folder_path))
        if folder_path.endswith('\\') or folder_path.endswith('/'):
            folder_name = format_material_name(os.path.basename(folder_path[:-1]))
        self.create_assets(folder_name, folder_path, texture_naming_conventions, settings, None, [])

        # Iterates over subfolders to create assets, applying tags and possibly catalog IDs
        for root, dirs, _ in os.walk(folder_path, topdown=True):
            if use_tags:
                relative_path = Path(root).relative_to(folder_path)
                tags = [format_material_name(part) for part in relative_path.parts]

            for name in dirs:
                path = os.path.join(root, name)
                catalog_id = None
                # Only modify blender_assets.cats.txt and set catalog_id if use_catalog_tree is True
                if use_catalog_tree:
                    catalog_id = get_or_create_catalog(os.path.join(root, name), folder_path)
                self.create_assets(name, path, texture_naming_conventions, settings, catalog_id, tags)

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

        layout.separator()
        layout.label(text="Name formating:")
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

        # Draw the settings for node generation
        layout.label(text="Node Generation:")
        box = layout.box()
        box.prop(scene, "file_type", text="File type and priority")
        box.prop(scene, "resolution_priority", text="Priority")
        box.prop(scene, "alt_col_handling", text="On multiple color maps")
        box.prop(scene, "default_texture_setup", text="If both available, use")
        box.prop(scene, "texture_setup_displacement", text="Setup Displacement")
        box.prop(scene, "displacement_mid_level", text="Displacement Mid Level")
        box.prop(scene, "displacement_height", text="Displacement Height")
        box.prop(scene, "texture_setup_default_gamma", text="Setup Gamma")

        layout.separator()

        # Draw the settings for preview generation
        layout.label(text="Preview:")
        box = layout.box()
        box.prop(scene, "preview_type", text="Preview Type")
        if scene.preview_type == 'Render':
            box.prop(scene, "object_mock", text="Lock to Object")
            box.prop(scene, "force_rerender", text="Render preview even if it exists")
            box.prop(scene, "resolution_x", text="Resolution X")
            box.prop(scene, "resolution_y", text="Resolution Y")
            box.label(text="Warning: Be sure to check alpha render")
        layout.separator()

        # UI for texture naming conventions
        layout.label(text="Texture Naming Conventions:")
        box = layout.box()
        box.prop(scene, "transmission")
        box.prop(scene, "albedo")
        box.prop(scene, "ambiant_occlusion")
        box.prop(scene, "metallic")
        box.prop(scene, "specular")
        box.prop(scene, "roughness")
        box.prop(scene, "opacity")
        box.prop(scene, "bump")
        box.prop(scene, "normal")
        box.prop(scene, "displacement")
        box.prop(scene, "emission")

        layout.separator()
        layout.label(text="Warning: Start OctaneServer before")

        # Draw the button to generate catalogs
        row = layout.row()
        row.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname, text="Generate Catalogs")


def menu_func(self, _):
    self.layout.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname)

# Definitions for UI panels and property groups, providing a graphical interface for the add-on's functionality

def register_ui():
    # Registers the operator and UI components with Blender, making them available to the user.
    # Also defines custom properties that appear in the Blender UI, allowing users to configure the add-on's behavior.
    bpy.utils.register_class(CUSTOM_OT_GenerateShaderCatalog)
    bpy.utils.register_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.Scene.selected_folder = StringProperty(subtype="DIR_PATH")
    bpy.types.Scene.use_catalog_tree = BoolProperty(
        name="Create Catalog Tree",
        description="Create and organize materials into a catalog tree",
        default=True  # Checked by default
    )
    bpy.types.Scene.use_tags = BoolProperty(
        name="Create Tags",
        description="Tag materials based on folder structure",
        default=True  # Checked by default
    )
    bpy.types.Scene.format_name = BoolProperty(
        name="Format Name",
        description="Format material names based on rules",
        default=True  # Checked by default
    )
    bpy.types.Scene.replace_by_space = StringProperty(
        name="Replace by Space",
        description="Characters to replace by spaces",
        default="_"  # Default characters
    )
    bpy.types.Scene.add_space_by_caps = BoolProperty(
        name="Add Space by Caps",
        description="Add space before capital letters",
        default=True  # Checked by default
    )
    bpy.types.Scene.add_space_between_word_and_number = BoolProperty(
        name="Add Space Between Word and Number",
        description="Add space between words and numbers",
        default=True  # Checked by default
    )
    bpy.types.Scene.file_type = StringProperty(
        name="File Type and Priority",
        default="jpg jpeg png exr hdr tiff tif",
        description="File types to look for and their priority"
    )
    bpy.types.Scene.resolution_priority = EnumProperty(
        name="Resolution Priority",
        items=(
            ('FileType', 'File type', 'Take first file type in the list'),
            ('FileName', 'File name', 'Take first file name in the list'),
            ("SmallerRes", "Smaller resolution", "Take the smaller resolution"),
            ("BiggerRes", "Bigger resolution", "Take the bigger resolution"),
        ),
        default='SmallerRes',
        description="Select the resolution priority when multiple files are found"
    )
    bpy.types.Scene.alt_col_handling = EnumProperty(
        name="Alternative Color handling",
        items=(
            ("NewNode", "Create a disabled node", "Add a new node to the shader tree, but it's disabled"),
            ("NewMaterial", "Create a new material", "Create a new material with the new color map"),
            ("First", "Take the first one", "Use the first color map found"),
            ("Last", "Take the last one", "Use the last color map found"),
        ),
        default='NewNode',
        description="What happens when multiple color maps are found"
    )
    bpy.types.Scene.default_texture_setup = EnumProperty(
        name="Shader's texture setup displacement",
        items=(
            ("Both", "Both", "Setup node will use both Bump and Displacement nodes"),
            ("Bump", "Bump", "Setup node will use Bump node"),
            ("Displacement", "Displacement", "Setup node will use Displacement node"),
        ),
        default='Displacement',
        description="If both available, use this node for setup textures for shader"
    )
    bpy.types.Scene.texture_setup_displacement = EnumProperty(
        name="Shader's texture setup displacement",
        items=(
            ("TextureDisplacement", "Texture Displacement", "Setup node will use Texture Displacement node"),
            ("VertexDisplacement", "Vertex Displacement", "Setup node will use Vertex Displacement node")
        ),
        default='TextureDisplacement',
        description="When setup textures for shader, for displacement it'll use this node"
    )
    bpy.types.Scene.texture_setup_default_gamma = FloatProperty(
        name="Shader's texture setup default gamma",
        default=2.2,
        min=0.0,
        description="When setup textures for shader, it'll use this gamma for all textures"
    )
    bpy.types.Scene.displacement_mid_level = FloatProperty(
        name="Displacement Mid Level",
        default=0.05,
        min=0.0,
        description="When displacement is used, it'll use this mid level for all textures"
    )
    bpy.types.Scene.displacement_height = FloatProperty(
        name="Displacement Height",
        default=0.05,
        min=0.0,
        description="When displacement is used, it'll use this height for all textures"
    )
    bpy.types.Scene.preview_type = EnumProperty(
        name="Preview Type",
        items=(
            ("NoPreview", "No preview (Fast)", "Don't set any preview image"),
            ("UseColorMap", "Use color map (Fast)", "Use the first color map as preview image"),
            ("Render", "Render (Slow)", "Render an image for the preview")
        ),
        default='Render',
        description="How to set the preview image for the material"
    )
    bpy.types.Scene.object_mock = PointerProperty(
        name="Object Mock",
        type=bpy.types.Object
    )
    bpy.types.Scene.force_rerender = BoolProperty(
        name="Force re-render preview",
        description="Force re-render the preview image for the material",
        default=False
    )
    bpy.types.Scene.resolution_x = IntProperty(
        name="Resolution X",
        default=200,
        min=1,
        description="Resolution X for the preview render",
        subtype='PIXEL'
    )
    bpy.types.Scene.resolution_y = IntProperty(
        name="Resolution X",
        default=200,
        min=1,
        description="Resolution X for the preview render",
        subtype='PIXEL'
    )
    bpy.types.Scene.transmission = StringProperty(
        name="Transmission",
        default="transmission transparency",
        description="Naming Components for Transmission maps"
    )
    bpy.types.Scene.albedo = StringProperty(
        name="Albedo",
        default="diffuse diff albedo base col color basecolor",
        description="Naming Components for color maps"
    )
    bpy.types.Scene.ambiant_occlusion = StringProperty(
        name='Ambient Occlusion',
        default='ao ambient occlusion',
        description='Naming Components for AO maps'
    )
    bpy.types.Scene.metallic = StringProperty(
        name="Metallic",
        default="metallic metalness metal mtl",
        description="Naming Components for Metallic maps"
    )
    bpy.types.Scene.specular = StringProperty(
        name="Specular",
        default="specularity specular spec spc reflectivity reflectivity refl",
        description="Naming Components for Specular maps"
    )
    bpy.types.Scene.roughness = StringProperty(
        name="Roughness",
        default="roughness rough rgh gloss glossiness gls",
        description="Naming Components for Roughness maps"
    )
    bpy.types.Scene.opacity = StringProperty(
        name="Opacity",
        default="alpha opacity",
        description="Naming Components for Alpha maps"
    )
    bpy.types.Scene.bump = StringProperty(
        name="Bump",
        default="bump bmp",
        description="Naming Components for Bump maps"
    )
    bpy.types.Scene.normal = StringProperty(
        name="Normal",
        default="normal nor nrm nrml norm",
        description="Naming Components for Normal maps"
    )
    bpy.types.Scene.displacement = StringProperty(
        name="Displacement",
        default="displacement displace disp dsp height heightmap",
        description="Naming Components for Displacement maps"
    )
    bpy.types.Scene.emission = StringProperty(
        name="Emission",
        default="emission emissive emit",
        description="Naming Components for Emission maps"
    )
    bpy.types.Scene.emission = StringProperty(
        name="Emission",
        default="emission emissive emit",
        description="Naming Components for Emission maps"
    )
    bpy.types.FILEBROWSER_MT_context_menu.append(menu_func)

def unregister_ui():
    # Unregisters the operator and UI components from Blender, cleaning up on add-on disable.
    # Also removes the custom properties from the Blender UI.
    del bpy.types.Scene.selected_folder
    del bpy.types.Scene.use_catalog_tree
    del bpy.types.Scene.use_tags
    del bpy.types.Scene.format_name
    del bpy.types.Scene.replace_by_space
    del bpy.types.Scene.add_space_by_caps
    del bpy.types.Scene.add_space_between_word_and_number
    del bpy.types.Scene.file_type
    del bpy.types.Scene.resolution_priority
    del bpy.types.Scene.default_texture_setup
    del bpy.types.Scene.texture_setup_displacement
    del bpy.types.Scene.displacement_mid_level
    del bpy.types.Scene.displacement_height
    del bpy.types.Scene.texture_setup_default_gamma
    del bpy.types.Scene.preview_type
    del bpy.types.Scene.object_mock
    del bpy.types.Scene.force_rerender
    del bpy.types.Scene.resolution_x
    del bpy.types.Scene.resolution_y
    del bpy.types.Scene.transmission
    del bpy.types.Scene.albedo
    del bpy.types.Scene.metallic
    del bpy.types.Scene.specular
    del bpy.types.Scene.roughness
    del bpy.types.Scene.opacity
    del bpy.types.Scene.bump
    del bpy.types.Scene.normal
    del bpy.types.Scene.displacement
    del bpy.types.Scene.emission
    bpy.utils.unregister_class(CUSTOM_OT_GenerateShaderCatalog)
    bpy.utils.unregister_class(CUSTOM_PT_GenerateCatalogsPanel)
    bpy.types.FILEBROWSER_MT_context_menu.remove(menu_func)
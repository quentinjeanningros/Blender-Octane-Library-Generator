import bpy
import os
from pathlib import Path
from bpy.props import BoolProperty, StringProperty, EnumProperty, FloatProperty
from .utils.materials import create_material
from .utils.parsing import format_material_name
from .utils.catalog import get_or_create_catalog
from .utils.parsing import format_material_name

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

        settings = {
            "texture_setup": bpy.context.scene.default_texture_setup,
            "displacement": bpy.context.scene.texture_setup_displacement,
            "gamma": bpy.context.scene.texture_setup_default_gamma
        }

        folder_name = format_material_name(os.path.basename(folder_path))
        if folder_path.endswith('\\') or folder_path.endswith('/'):
            folder_name = format_material_name(os.path.basename(folder_path[:-1]))
        formatted_name = format_material_name(folder_name)
        mat = create_material(formatted_name, texture_naming_conventions, settings, folder_path)

        for root, dirs, _ in os.walk(folder_path, topdown=True):
            if use_tags:
                relative_path = Path(root).relative_to(folder_path)
                tags = [format_material_name(part) for part in relative_path.parts]

            for name in dirs:
                path = os.path.join(root, name)
                formatted_name = format_material_name(name)
                mat = create_material(formatted_name, texture_naming_conventions, settings, path)
                if not mat:
                    continue

                mat.use_fake_user = True
                mat.asset_mark()
                # Only modify blender_assets.cats.txt and set catalog_id if use_catalog_tree is True
                if use_catalog_tree:
                    catalog_id = get_or_create_catalog(os.path.join(root, name), folder_path)
                    if catalog_id:  # Ensure catalog_id is not None before assignment
                        mat.asset_data.catalog_id = catalog_id

                # Add tags from folder structure
                if use_tags:
                    for tag in tags:
                        mat.asset_data.tags.new(tag, skip_if_exists=True)



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

        layout.label(text="Node Generation:")
        box = layout.box()
        box.prop(scene, "default_texture_setup", text="If both available, use")
        box.prop(scene, "texture_setup_displacement", text="Texture Setup Displacement")
        box.prop(scene, "texture_setup_default_gamma", text="Texture Setup Default Gamma")

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

        # Draw the button to generate catalogs
        row = layout.row()
        row.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname, text="Generate Catalogs")


def menu_func(self, _):
    self.layout.operator(CUSTOM_OT_GenerateShaderCatalog.bl_idname)


def register_ui():
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
    bpy.types.Scene.default_texture_setup = EnumProperty(
        name="Shader's texture setup displacement",
        items=(
            ("Bump", "Bump", "Setup node will use Bump node"),
            ("Displacement", "Displacement", "Setup node will use Displacement node"),
        ),
        default='Displacement',
        description="If both available, use this node for setup textures for shader"
    )
    bpy.types.Scene.texture_setup_displacement = EnumProperty(
        name="Shader's texture setup displacement",
        items=(
            ("OctaneTextureDisplacement", "Texture Displacement", "Setup node will use Texture Displacement node"),
            ("OctaneVertexDisplacement", "Vertex Displacement", "Setup node will use Vertex Displacement node")
        ),
        default='OctaneTextureDisplacement',
        description="When setup textures for shader, for displacement it'll use this node"
    )
    bpy.types.Scene.texture_setup_default_gamma = FloatProperty(
        name="Shader's texture setup default gamma",
        default=2.2,
        min=0.0,
        description="When setup textures for shader, it'll use this gamma for all textures"
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
    del bpy.types.Scene.selected_folder
    del bpy.types.Scene.use_catalog_tree
    del bpy.types.Scene.use_tags
    del bpy.types.Scene.format_name
    del bpy.types.Scene.replace_by_space
    del bpy.types.Scene.add_space_by_caps
    del bpy.types.Scene.add_space_between_word_and_number
    del bpy.types.Scene.default_texture_setup
    del bpy.types.Scene.texture_setup_displacement
    del bpy.types.Scene.texture_setup_default_gamma
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
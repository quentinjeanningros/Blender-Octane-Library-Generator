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

bl_info = {
    "name": "Generate Catalogs from Selected Folders",
    "author": "Your Name",
    "description": "Generate catalogs based on selected folders",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "category": "Generic",
}

from .interface import CUSTOM_PT_GenerateCatalogsPanel, CUSTOM_OT_GenerateShaderCatalog
import bpy

def menu_func(self, _):
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
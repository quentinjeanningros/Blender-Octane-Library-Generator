import bpy
from .paths import split_into_components, match_files_to_socket_names

def create_octane_texture_node(texture):
    #TODO Logic to create an Octane texture node for a given texture file
    # Will vary based on the texture type (e.g., ImageTexture, FloatImageTexture, etc.)
    pass

def connect_texture_to_material(material, texture_node):
    #TODO Logic to connect a texture node to the appropriate input of an Octane material
    pass

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
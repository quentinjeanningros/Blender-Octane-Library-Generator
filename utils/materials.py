import bpy
import os
from pathlib import Path
from .parsing import match_files_to_keys, fetch_files_at_path
from .constants import GAP, OCTANE_NODE, UNIVERSAL_MATERIAL_SOCKET, TEXTURE_EMISSION_SOCKET, IMAGE_TEXTURE_SOCKET, DISPLACEMENT_SOCKET, MULTIPLY_TEXTURE_SOCKET, TRANSFORM_SOCKET, NODE_POSITION

def create_link(links, from_node, from_socket_name, to_node, to_socket_name):
    if to_socket_name in to_node.inputs and from_socket_name in from_node.outputs:
        return links.new(to_node.inputs[to_socket_name], from_node.outputs[from_socket_name])
    return None

def create_empty_material(mat_name):
    unique_name = mat_name
    i = 1  # Start counter for suffixes

    # Loop to find a unique name by appending a number
    while unique_name in bpy.data.materials:
        unique_name = f"{mat_name}.{str(i).zfill(3)}"  # Append a suffix like .001, .002, etc.
        i += 1

    # Create a new material
    mat = bpy.data.materials.new(name=unique_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Add an OctaneUniversalMaterial node
    universal_node = nodes.new(OCTANE_NODE['UniversalMaterial'])
    universal_node.location = NODE_POSITION['UniversalMaterial']

    output_node = nodes.new(OCTANE_NODE['MaterialOutput'])
    output_node.location = NODE_POSITION['MaterialOutput']
    create_link(links, universal_node, 'Material out', output_node, 'Surface')
    return {'material': mat, 'nodes': nodes, 'links': links, 'universal': universal_node, 'output': output_node}


def create_texture_node(nodes, texture_type, texture_path, location, gamma = 2.2):
    # Check if the texture is already loaded
    image = next((img for img in bpy.data.images if img.filepath == texture_path), None)

    # If the texture is not loaded, load it
    if image is None:
        image = bpy.data.images.load(texture_path)

    texture_node = nodes.new(OCTANE_NODE['ImageTexture'])
    texture_node.location = location
    texture_node.label = texture_type
    texture_node.name = texture_type
    texture_node.inputs[IMAGE_TEXTURE_SOCKET['Gamma']].default_value = float(gamma)
    texture_node.image = image
    return texture_node


def create_material(mat_name, keys, settings, folder_path):
    sockets = [
        ['Transmission', keys['transmission'], []],
        ['Albedo', keys['albedo'], []],
        ['Ambient Occlusion', keys['ambiant_occlusion'], []],
        ['Metallic', keys['metallic'], []],
        ['Specular', keys['specular'], []],
        ['Roughness', keys['roughness'], []],
        ['Opacity', keys['opacity'], []],
        ['Bump', keys['bump'], []],
        ['Normal', keys['normal'], []],
        ['Displacement', keys['displacement'], []],
        ['Emission', keys['emission'], []]
    ]

    all_keys = set()
    for k in keys.values():
        all_keys.update(k)
    files_with_keys = match_files_to_keys(fetch_files_at_path(folder_path), all_keys)

    for s in sockets:
        for f, k in files_with_keys.items():
            for key in k:
                if key in s[1]:
                    s[2].append(f)


    # Remove sockets without found files
    sockets = [s for s in sockets if s[2]]

    if not sockets:
        return None

    data = create_empty_material(mat_name)
    mat = data['material']
    nodes = data['nodes']
    links = data['links']
    universal_node = data['universal']

    transform_node = nodes.new(OCTANE_NODE['3DTransform'])
    transform_node.location = NODE_POSITION['3DTransform']

    albedo_node = None
    albedo_text = None
    ao_node = None
    displacement_link = None
    bump_link = None

    for i, s in enumerate(sockets):
        texture_type = s[0]
        texture_files = s[2]
        texture_path = os.path.join(folder_path, texture_files[0])

        if texture_type == 'Transmission' or texture_type == 'Albedo' or texture_type == 'Metallic' or texture_type == 'Specular' or texture_type == 'Roughness' or texture_type == 'Opacity' or texture_type == 'Bump' or texture_type == 'Normal':
            texture_node = create_texture_node(nodes, texture_type, texture_path, NODE_POSITION[texture_type], settings['gamma'])
            create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
            link = create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET[texture_type])
            if texture_type == 'Albedo':
                albedo_text = texture_path
                albedo_node = texture_node
            if texture_type == 'Bump':
                bump_link = link
        elif texture_type == 'Ambient Occlusion':
            ao_node = create_texture_node(nodes, texture_type, texture_path, NODE_POSITION[texture_type], settings['gamma'])
            create_link(links, transform_node, TRANSFORM_SOCKET['Out'], ao_node, IMAGE_TEXTURE_SOCKET['Transform'])
            create_link(links, ao_node, IMAGE_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Albedo'])
        elif texture_type == 'Displacement':
            displacement_node = nodes.new(OCTANE_NODE[settings['displacement_type']])
            displacement_node.location = NODE_POSITION['DisplacementNode']
            displacement_node.inputs[DISPLACEMENT_SOCKET['Midlevel']].default_value = settings['displacement_midlevel']
            displacement_node.inputs[DISPLACEMENT_SOCKET['Height']].default_value = settings['displacement_height']
            texture_node = create_texture_node(nodes, texture_type, texture_path, NODE_POSITION[texture_type], settings['gamma'])
            create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
            create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], displacement_node, DISPLACEMENT_SOCKET['Texture'])
            displacement_link  = create_link(links, displacement_node, DISPLACEMENT_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Displacement'])
        elif texture_type == 'Emission':
            emission_node = nodes.new(OCTANE_NODE['TextureEmission'])
            emission_node.location = NODE_POSITION['EmissionNode']
            texture_node = create_texture_node(nodes, texture_type, texture_path, NODE_POSITION[texture_type], settings['gamma'])
            create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
            create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], emission_node, TEXTURE_EMISSION_SOCKET['Texture'])
            create_link(links, emission_node, TEXTURE_EMISSION_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Emission'])

    if ao_node and albedo_node:
        multiply_node = nodes.new(OCTANE_NODE['MultiplyTexture'])
        multiply_node.location = NODE_POSITION['MultiplyNode']
        albedo_node.location = (albedo_node.location[0] - GAP + 50, albedo_node.location[1] + 50)
        ao_node.location = (ao_node.location[0] - GAP * 2 + 100, ao_node.location[1] + 150)
        create_link(links, albedo_node, IMAGE_TEXTURE_SOCKET['Out'], multiply_node, MULTIPLY_TEXTURE_SOCKET['In1'])
        create_link(links, ao_node, IMAGE_TEXTURE_SOCKET['Out'], multiply_node, MULTIPLY_TEXTURE_SOCKET['In2'])
        create_link(links, multiply_node, MULTIPLY_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Albedo'])

    if bump_link and displacement_link:
        print( settings['displacement_type'])
        if settings['texture_setup'] == 'Displacement':
            print('Removing bump link')
            links.remove(bump_link)
        elif settings['texture_setup'] == 'Bump':
            links.remove(displacement_link)

    nodes.update()
    links.update()
    return {'material': mat, 'albedo': albedo_text}
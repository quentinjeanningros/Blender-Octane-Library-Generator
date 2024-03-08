import bpy
import os
from pathlib import Path
from .parsing import match_files_to_keys, fetch_files_at_path

GAP = 300


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
    universal_node = nodes.new('OctaneUniversalMaterial')
    universal_node.location = (0, 0)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (GAP, 0)
    create_link(links, universal_node, 'Material out', output_node, 'Surface')
    return {'material': mat, 'nodes': nodes, 'links': links}


def create_texture_node(nodes, texture_type, texture_path, location):
    texture_node = nodes.new('OctaneRGBImage')
    texture_node.location = location
    texture_node.label = texture_type
    texture_node.name = texture_type
    texture_node.image = bpy.data.images.load(texture_path)
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

    data = create_empty_material(mat_name)
    mat = data['material']
    nodes = data['nodes']
    links = data['links']

    transform_node = nodes.new('OctaneTransformValue')
    transform_node.location = (-GAP*2, 0)

    for i, s in enumerate(sockets):
        texture_type = s[0]
        texture_files = s[2]
        texture_path = os.path.join(folder_path, texture_files[0])

        if texture_type == 'Albedo':
            texture_node = create_texture_node(nodes, texture_type, texture_path, (-GAP, GAP * i))
            create_link(links, texture_node, 'Texture out', transform_node, 'Albedo')


    nodes.update()
    links.update()
    return mat

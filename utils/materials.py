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
    print(location)
    texture_node.location = location
    texture_node.label = texture_type
    texture_node.name = texture_type
    texture_node.inputs[IMAGE_TEXTURE_SOCKET['Gamma']].default_value = float(gamma)
    texture_node.image = image
    return texture_node

def create_appropriate_node(texture_type, links, nodes, transform_node, universal_node, texture_path, settings, position_shift = (0, 0)):
    node_pos = (NODE_POSITION[texture_type][0] + position_shift[0], NODE_POSITION[texture_type][1] + position_shift[1])
    gamma = settings['gamma']
    if texture_type == 'Transmission' or texture_type == 'Albedo' or texture_type == 'Metallic' or texture_type == 'Specular' or texture_type == 'Roughness' or texture_type == 'Opacity' or texture_type == 'Bump' or texture_type == 'Normal':
        texture_node = create_texture_node(nodes, texture_type, texture_path, node_pos, gamma)
        create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
        link = create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET[texture_type])
        return {'node': texture_node, 'link': link}
    elif texture_type == 'Ambient Occlusion':
        ao_node = create_texture_node(nodes, texture_type, texture_path, node_pos, gamma)
        create_link(links, transform_node, TRANSFORM_SOCKET['Out'], ao_node, IMAGE_TEXTURE_SOCKET['Transform'])
        link = create_link(links, ao_node, IMAGE_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Albedo'])
        return {'node': ao_node, 'link': link}
    elif texture_type == 'Displacement':
        displacement_node = nodes.new(OCTANE_NODE[settings['displacement_type']])
        displacement_node.location = (NODE_POSITION['DisplacementNode'][0] + position_shift[0], NODE_POSITION['DisplacementNode'][1] + position_shift[1])
        displacement_node.inputs[DISPLACEMENT_SOCKET['Midlevel']].default_value = settings['displacement_midlevel']
        displacement_node.inputs[DISPLACEMENT_SOCKET['Height']].default_value = settings['displacement_height']
        texture_node = create_texture_node(nodes, texture_type, texture_path, node_pos, gamma)
        create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
        create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], displacement_node, DISPLACEMENT_SOCKET['Texture'])
        displacement_link  = create_link(links, displacement_node, DISPLACEMENT_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Displacement'])
        return {'node': displacement_node, 'link': displacement_link}
    elif texture_type == 'Emission':
        emission_node = nodes.new(OCTANE_NODE['TextureEmission'])
        emission_node.location = (NODE_POSITION['EmissionNode'][0] + position_shift[0], NODE_POSITION['EmissionNode'][1] + position_shift[1])
        texture_node = create_texture_node(nodes, texture_type, texture_path, node_pos, gamma)
        create_link(links, transform_node, TRANSFORM_SOCKET['Out'], texture_node, IMAGE_TEXTURE_SOCKET['Transform'])
        create_link(links, texture_node, IMAGE_TEXTURE_SOCKET['Out'], emission_node, TEXTURE_EMISSION_SOCKET['Texture'])
        link = create_link(links, emission_node, TEXTURE_EMISSION_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Emission'])
        return {'node': emission_node, 'link': link}

def create_material_nodes(name, sockets, settings):
    data = create_empty_material(name)
    mat = data['material']
    nodes = data['nodes']
    links = data['links']
    universal_node = data['universal']

    transform_node = nodes.new(OCTANE_NODE['3DTransform'])
    transform_node.location = NODE_POSITION['3DTransform']

    albedo_nodes = []
    albedo_text = None
    ao_node = None
    displacement_link = None
    bump_link = None

    for s in sockets:
        texture_type = s['type']
        texture_path = s['paths'][0]

        node_groupe = None
        if texture_type == 'Albedo':
            for index, path in enumerate(s['paths']):
                position_shift = (0, 50 * index)
                groupe = create_appropriate_node(texture_type, links, nodes, transform_node, universal_node, path, settings, position_shift)
                node = groupe['node']
                if index == 0:
                    albedo_text = path
                else :
                    node.hide = True
                node.name = node.name + ' Alt-' + str(index + 1)
                node.label = node.label + ' Alt-' + str(index + 1)
                albedo_nodes.append(node)
            create_link(links, albedo_nodes[0], IMAGE_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Albedo'])

        else :
            node_groupe = create_appropriate_node(texture_type, links, nodes, transform_node, universal_node, texture_path, settings)
            texture_node = node_groupe['node']
            texture_link = node_groupe['link']
            if texture_type == 'Ambient Occlusion':
                ao_node = texture_node
            elif texture_type == 'Bump':
                bump_link = texture_link
            elif texture_type == 'Displacement':
                displacement_link = texture_node

    if ao_node and len(albedo_nodes) >= 1:
        multiply_node = nodes.new(OCTANE_NODE['MultiplyTexture'])
        multiply_node.location = NODE_POSITION['MultiplyNode']
        for albedo_node in albedo_nodes:
            albedo_node.location = (albedo_node.location[0] - GAP + 50, albedo_node.location[1] + 50)
        ao_node.location = (ao_node.location[0] - GAP * 2 + 100, ao_node.location[1] + 150)
        create_link(links, albedo_nodes[0], IMAGE_TEXTURE_SOCKET['Out'], multiply_node, MULTIPLY_TEXTURE_SOCKET['In1'])
        create_link(links, ao_node, IMAGE_TEXTURE_SOCKET['Out'], multiply_node, MULTIPLY_TEXTURE_SOCKET['In2'])
        create_link(links, multiply_node, MULTIPLY_TEXTURE_SOCKET['Out'], universal_node, UNIVERSAL_MATERIAL_SOCKET['Albedo'])

    if bump_link and displacement_link:
        if settings['texture_setup'] == 'Displacement':
            links.remove(bump_link)
        elif settings['texture_setup'] == 'Bump':
            links.remove(displacement_link)

    nodes.update()
    links.update()
    return {'material': mat, 'albedo': albedo_text}

def create_materials_according_settings(mat_name, keys, settings, folder_path):
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
    files_with_keys = match_files_to_keys(fetch_files_at_path(folder_path, settings['file_types']), all_keys)

    for s in sockets:
        for f, k in files_with_keys.items():
            for key in k:
                if key in s[1]:
                    s[2].append(f)


    clean_sockets = []
    for item in sockets:
        if item[2]:
            new_item = {'type' :item[0], 'paths' : []}
            for path in item[2]:
                new_item['paths'].append(os.path.join(folder_path, path))
            clean_sockets.append(new_item)

    if not clean_sockets:
        return []

    def get_file_type_order(path):
        for file_type in settings['file_types']:
            if path.endswith(file_type):
                return settings['file_types'].index(file_type)
        return len(settings['file_types'])

    ordered_sockets = []
    if settings['resolution_priority'] == 'FileType':
        for item in clean_sockets:
            sorted_paths = sorted(item['paths'], key=get_file_type_order)
            ordered_sockets.append({'type' : item['type'], 'paths' : sorted_paths})
    elif settings['resolution_priority'] == 'SmallerRes':
        for item in clean_sockets:
            sorted_paths = sorted(item['paths'], key=lambda x: Path(x).stat().st_size)
            ordered_sockets.append({'type' : item['type'], 'paths' : sorted_paths})
    elif settings['resolution_priority'] == 'BiggerRes':
        for item in clean_sockets:
            sorted_paths = sorted(item['paths'], key=lambda x: Path(x).stat().st_size, reverse=True)
            ordered_sockets.append({'type' : item['type'], 'paths' : sorted_paths})
    else:
        ordered_sockets = clean_sockets


    data_array = []
    # Find all 'Albedo' items in ordered_sockets
    albedo_paths = [path for item in ordered_sockets if item['type'] == 'Albedo' for path in item['paths']]
    if len(albedo_paths) > 1 and settings['alt_col_handling'] == 'NewMaterial':
        # For each 'Albedo' item, append a new list to socket_lists that contains only this item
        for index, path in enumerate(albedo_paths):
            unique_sockets = [i.copy() for i in ordered_sockets]
            for socket in unique_sockets:
                if socket['type'] == 'Albedo':
                    socket['paths'] = [path]
            unique_name = mat_name + ' Alt-' + str(index+1)
            data = create_material_nodes(unique_name, unique_sockets, settings)
            data_array.append(data)
    elif len(albedo_paths) > 1 and settings['alt_col_handling'] == 'First':
        ordered_sockets = [i for i in ordered_sockets if i['type'] != 'Albedo']
        ordered_sockets.append({'type' : 'Albedo', 'paths' : [albedo_paths[0]]})
        data = create_material_nodes(mat_name, ordered_sockets, settings)
        data_array.append(data)
    elif len(albedo_paths) > 1 and settings['alt_col_handling'] == 'Last':
        ordered_sockets = [i for i in ordered_sockets if i['type'] != 'Albedo']
        ordered_sockets.append({'type' : 'Albedo', 'paths' : [albedo_paths[-1]]})
        data = create_material_nodes(mat_name, ordered_sockets, settings)
        data_array.append(data)
    else :
        data = create_material_nodes(mat_name, ordered_sockets, settings)
        data_array.append(data)

    return data_array
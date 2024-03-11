# Defines node types for Octane Render engine used in material creation
OCTANE_NODE = {
  'UniversalMaterial': 'OctaneUniversalMaterial',
  'ImageTexture': 'OctaneRGBImage',
  'TextureEmission': 'OctaneTextureEmission',
  'TextureDisplacement': 'OctaneTextureDisplacement',
  'VertexDisplacement': 'OctaneVertexDisplacement',
  '3DTransform': 'Octane3DTransformation',
  'MaterialOutput': 'ShaderNodeOutputMaterial',
  'MultiplyTexture': 'OctaneMultiplyTexture',
}

# Defines socket names for the 'UniversalMaterial' node
UNIVERSAL_MATERIAL_SOCKET = {
  'Transmission': 'Transmission',
  'Albedo': 'Albedo',
  'Metallic': 'Metallic',
  'Specular': 'Specular',
  'Roughness': 'Roughness',
  'Opacity': 'Opacity',
  'Bump': 'Bump',
  'Normal': 'Normal',
  'Displacement': 'Displacement',
  'Emission': 'Emission',
}

# More constants for other node and socket types follow...
TEXTURE_EMISSION_SOCKET = {
  'Texture': 'Texture',
  'Out': 'Emission out',
}

IMAGE_TEXTURE_SOCKET = {
  'Transform': 'UV transform',
  'Out': 'Texture out',
  'Gamma': 'Legacy gamma',
}

TRANSFORM_SOCKET = {
  'Out': 'Transform out',
}

MULTIPLY_TEXTURE_SOCKET = {
  'In1': 'Texture 1',
  'In2': 'Texture 2',
  'Out': 'Texture out',
}

DISPLACEMENT_SOCKET = {
  'Texture': 'Texture',
  'Midlevel': 'Mid level',
  'Height': 'Height',
  'Out': 'Displacement out',
}

# Defines a constant gap used for arranging nodes visually in the Blender node editor
GAP = 300

# Defines default positions for each type of node in the node editor, ensuring a clean and organized node layout
NODE_POSITION = {
  'MaterialOutput': (GAP, 0),
  '3DTransform': (-GAP*4, 50),
  'UniversalMaterial': (0, 150),
  'Transmission': (-GAP, 500),
  'Albedo': (-GAP, 100),
  'Ambient Occlusion': (-GAP, 100),
  'MultiplyNode': (-GAP, 25),
  'Metallic': (-GAP*3, -300),
  'Specular': (-GAP*2, -250),
  'Roughness': (-GAP, -300),
  'Opacity': (-GAP*3, -700),
  'Bump': (-GAP*2, -650),
  'Normal': (-GAP, -700),
  'Displacement': (-GAP*2, -1050),
  'DisplacementNode': (-GAP, -1100),
  'Emission': (-GAP*2, -1450),
  'EmissionNode': (-GAP, -1350),
}
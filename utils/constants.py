OCTANE_NODE = {
  'UniversalMaterial': 'OctaneUniversalMaterial',
  'ImageTexture': 'OctaneRGBImage',
  'TextureEmission': 'OctaneTextureEmission',
  'TextureDisplacement': 'OctaneTextureDisplacement',
  'VertexDisplacement': 'OctaneVertexDisplacement',
  '3DTransform': 'Octane3DTransformation',
  'MaterialOutput': 'ShaderNodeOutputMaterial',
}

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
  'Out': 'Displacement out',
}
import bpy
import os

def render_and_save(output_dir, output_filename, resolution_x, resolution_y):
    # Set the render settings (optional, customize as needed)
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # Set the image format to JPEG (or another)
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.context.scene.render.resolution_percentage = 100

    # Define the render output path
    bpy.context.scene.render.filepath = os.path.join(output_dir, output_filename)

    # Execute render operation
    bpy.ops.render.render(write_still=True)
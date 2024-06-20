#  Phase3 Code contains the code to export OBJ, Materials.rad, and render the scene with all the commands seperately


bl_info = {
    "name": "Radiance Exporter",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Properties > Radiance Exporter",
    "description": "Adds a section for exporting and rendering with Radiance",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}

import bpy
import os
import subprocess
import time
from mathutils import Vector

class RadianceExporterPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Radiance Rendering"
    bl_idname = "RENDER_PT_radiance_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("export_scene.radiance", text="Export and Render")

class ExportRadiance(bpy.types.Operator):
    """Exports and renders the scene with Radiance"""
    bl_idname = "export_scene.radiance"
    bl_label = "Export and Render"

    def execute(self, context):
        # Get the blend file path and create the "Radiance Rendering" directory
        blend_file_path = bpy.data.filepath
        if not blend_file_path:
            self.report({'ERROR'}, "Please save the Blender file before exporting.")
            return {'CANCELLED'}

        blend_file_dir = os.path.dirname(blend_file_path)
        radiance_dir = os.path.join(blend_file_dir, "Radiance Rendering")

        if not os.path.exists(radiance_dir):
            os.makedirs(radiance_dir)

        # Export OBJ file
        obj_file = os.path.join(radiance_dir, "model.obj")
        bpy.ops.export_scene.obj(filepath=obj_file, check_existing=True, use_selection=False, use_materials=False, axis_forward='-Z', axis_up='Y')

        # Create materials.rad file
        materials_file = os.path.join(radiance_dir, "materials.rad")
        with open(materials_file, "w") as file:
            file.write("void plastic white\n0\n0\n5 1 1 1 0 0\n")

        # Run obj2mesh
        rtm_file = os.path.join(radiance_dir, "model.rtm")
        subprocess.run(["obj2mesh", "-a", materials_file, obj_file, rtm_file])

        # Create scene.rad file
        scene_file = os.path.join(radiance_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write("void mesh model\n1 model.rtm\n0\n0\n")

        # Run oconv
        oct_file = os.path.join(radiance_dir, "scene.oct")
        subprocess.run(["oconv", scene_file, ">", oct_file])
        
        time.sleep(2)
        # Get camera parameters
        cam = bpy.data.objects['Camera']
        location = cam.location
        up = cam.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
        direction = cam.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))

        # Run rpict
        pic_file = os.path.join(radiance_dir, "render.pic")
        subprocess.run(["rpict",
                        "-vp", str(location.x), str(location.y), str(location.z),
                        "-vd", str(direction.x), str(direction.y), str(direction.z),
                        "-vu", str(up.x), str(up.y), str(up.z),
                        "-av", "1", "1", "1",
                        "-ab", "2",
                        oct_file, ">", pic_file])

        self.report({'INFO'}, "Radiance rendering completed. Output: {}".format(pic_file))
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RadianceExporterPanel)
    bpy.utils.register_class(ExportRadiance)

def unregister():
    bpy.utils.unregister_class(RadianceExporterPanel)
    bpy.utils.unregister_class(ExportRadiance)

if __name__ == "__main__":
    register()
# Phase 2 Code contains the code to export both OBJ and Materials.rad file

bl_info = {
    "name": "Radiance Exporter",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Properties > Radiance Exporter",
    "description": "Adds a section for exporting OBJ, MTL, and RAD files for Radiance Rendering",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}

import bpy
import os

class RadianceExporterPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Radiance Exporter"
    bl_idname = "RENDER_PT_radiance_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("export_scene.radiance", text="Export Radiance")

class ExportRadiance(bpy.types.Operator):
    """Exports OBJ, MTL, and RAD files for Radiance Rendering"""
    bl_idname = "export_scene.radiance"
    bl_label = "Export Radiance"

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

        # Export OBJ and MTL files
        obj_file = os.path.join(radiance_dir, "scene.obj")
        mtl_file = os.path.join(radiance_dir, "scene.mtl")
        bpy.ops.export_scene.obj(filepath=obj_file, check_existing=True, use_materials=True, path_mode='AUTO')

        # Export RAD file
        rad_file = os.path.join(radiance_dir, "materials.rad")
        materials = bpy.data.materials
        with open(rad_file, "w") as file:
            for material in materials:
                # Write material definition to file
                file.write("void plastic {}\n".format(material.name))
                file.write("0\n0\n5\n")
                file.write("{} {} {}\n".format(*material.diffuse_color[:3]))
                file.write("{}\n".format(material.specular_intensity))
                file.write("{}\n\n".format(material.roughness))

        self.report({'INFO'}, "Exported Radiance files to {}".format(radiance_dir))
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RadianceExporterPanel)
    bpy.utils.register_class(ExportRadiance)

def unregister():
    bpy.utils.unregister_class(RadianceExporterPanel)
    bpy.utils.unregister_class(ExportRadiance)

if __name__ == "__main__":
    register()
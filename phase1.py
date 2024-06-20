#  Phase 1 Code contains the code for the OBJ Exporter Panel


bl_info = {
    "name": "Simple OBJ Exporter",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Properties > OBJ Exporter",
    "description": "Adds a section for exporting OBJ files",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}

import bpy

class OBJExporterPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "OBJ Exporter"
    bl_idname = "RENDER_PT_obj_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("export_scene.obj", text="Export OBJ")

def register():
    bpy.utils.register_class(OBJExporterPanel)

def unregister():
    bpy.utils.unregister_class(OBJExporterPanel)

if __name__ == "__main__":
    register()

import bpy
import json
from bpy.props import StringProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper

class JSONLoaderProperties(bpy.types.PropertyGroup):
    json_filepath: StringProperty(
        name="JSON File Path",
        description="Path to the JSON file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore

class JSON_OT_LoadFile(Operator, ImportHelper):
    bl_idname = "json.load_file"
    bl_label = "Load JSON File"
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    ) # type: ignore

    def execute(self, context):
        context.scene.json_loader_props.json_filepath = self.filepath
        self.report({'INFO'}, "JSON file loaded: " + self.filepath)
        return {'FINISHED'}

class RENDER_PT_CustomPanel(Panel):
    bl_label = "JSON Render Settings"
    bl_idname = "RENDER_PT_custom_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        json_props = scene.json_loader_props

        layout.operator("json.load_file", text="Upload JSON File")
        
        if json_props.json_filepath:
            layout.label(text="File: " + json_props.json_filepath)
            layout.operator("json.print_details", text="Render")

class JSON_OT_PrintDetails(Operator):
    bl_idname = "json.print_details"
    bl_label = "Print JSON Details"

    def execute(self, context):
        json_props = context.scene.json_loader_props
        json_filepath = json_props.json_filepath

        try:
            with open(json_filepath, 'r') as json_file:
                json_data = json.load(json_file)
                print("JSON Data:")
                print(json.dumps(json_data, indent=4))
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read JSON file: {e}")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(JSONLoaderProperties)
    bpy.utils.register_class(JSON_OT_LoadFile)
    bpy.utils.register_class(JSON_OT_PrintDetails)
    bpy.utils.register_class(RENDER_PT_CustomPanel)
    bpy.types.Scene.json_loader_props = bpy.props.PointerProperty(type=JSONLoaderProperties)

def unregister():
    bpy.utils.unregister_class(JSONLoaderProperties)
    bpy.utils.unregister_class(JSON_OT_LoadFile)
    bpy.utils.unregister_class(JSON_OT_PrintDetails)
    bpy.utils.unregister_class(RENDER_PT_CustomPanel)
    del bpy.types.Scene.json_loader_props

if __name__ == "__main__":
    register()

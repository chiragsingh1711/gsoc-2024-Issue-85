# Phase 6: Resolution of the Image output taken from the user through Blender GUI
# Always make sure to change the aspect ratio along with the resolution of the image


bl_info = {
    "name": "Radiance Exporter",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Render Properties > Radiance Exporter",
    "description": "Adds a section for exporting and rendering with Radiance using rad",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}

import bpy
import os
import subprocess
import mathutils

import ifcopenshell
import ifcopenshell.geom
import multiprocessing

import json

from bpy.props import StringProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper



class RadianceExporterPanel(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Radiance Exporter"
    bl_idname = "RENDER_PT_radiance_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.label(text="Resolution")
#        row = layout.row()
        
        row.prop(scene, "radiance_resolution_x", text="X")
        row = layout.row()
        row.label(text="")
        row.prop(scene, "radiance_resolution_y", text="Y")

        
        row = layout.row()
        row.operator("export_scene.radiance", text="Export and Render")

class ExportRadiance(bpy.types.Operator):
    """Exports and renders the scene with Radiance using rad"""
    bl_idname = "export_scene.radiance"
    bl_label = "Export and Render"


    def getResolution(self, context):
        scene = context.scene
        resolution_x = scene.radiance_resolution_x
        resolution_y = scene.radiance_resolution_y
        return resolution_x, resolution_y

    # def getQuality(self, context):
    #     scene = context.scene
    #     quality = scene.radiance_quality
    #     return quality

    def execute(self, context):
        
        # Get the resolution from the user input
        resolution_x, resolution_y = self.getResolution(context)
        
        # Calculate the aspect ratio
        aspect_ratio = resolution_x / resolution_y


        # Get the blend file path and create the "Radiance Rendering" directory
        self.report({'INFO'}, "Exporting Radiance files...")
        blend_file_path = bpy.data.filepath
        if not blend_file_path:
            self.report({'ERROR'}, "Please save the Blender file before exporting.")
            return {'CANCELLED'}

        blend_file_dir = os.path.dirname(blend_file_path)
        radiance_dir = os.path.join(blend_file_dir, "Radiance Rendering")
        
        self.report({'INFO'}, "Radiance directory: {}".format(radiance_dir))

        if not os.path.exists(radiance_dir):
            os.makedirs(radiance_dir)

        # Export OBJ file
        # obj_file = os.path.join(radiance_dir, "model.obj")
        # bpy.ops.export_scene.obj(filepath=obj_file, check_existing=True, use_seleiction=False, use_materials=True, axis_forward='-Z', axs_up='Y')

        # Get the directory path of the current blend file
        blend_file_path = bpy.data.filepath
        blend_file_directory = os.path.dirname(blend_file_path)

        # Create a new directory for the output files
        output_directory = os.path.join(blend_file_directory, "Radiance Rendering")
        os.makedirs(output_directory, exist_ok=True)

        settings = ifcopenshell.geom.settings()

        # Settings for obj
        settings.set(settings.STRICT_TOLERANCE, True)
        settings.set(settings.INCLUDE_CURVES, True)
        settings.set(settings.USE_ELEMENT_GUIDS, True)
        settings.set(settings.APPLY_DEFAULT_MATERIALS, True)
        settings.set(settings.USE_WORLD_COORDS, True)

        # Specify the input IFC file path

        ifc_file_path = 'C:/Users/Chirag Singh/Desktop/gsoc-Phase1/Export Testing/IFC testing/TestCubes/Cubes.ifc'

        # Open the IFC file
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Specify the output file paths relative to the blend file's location
        obj_file_path = os.path.join(output_directory, "model.obj")
        mtl_file_path = os.path.join(output_directory, "model.mtl")

        # Serialise to obj
        serialiser = ifcopenshell.geom.serializers.obj(obj_file_path, mtl_file_path, settings)

        serialiser.setFile(ifc_file)
        serialiser.setUnitNameAndMagnitude("METER", 1.0)
        serialiser.writeHeader()

        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
        if iterator.initialize():
            while True:
                serialiser.write(iterator.get())
                if not iterator.next():
                    break
        serialiser.finalize()

        style = []
        with open(f"C:/Users/Chirag Singh/Desktop/gsoc-Phase1/Export Testing/Radiance Rendering/model.obj", "r") as obj_file:
            # Iterate through each line in the file
            for line in obj_file:
                # Check if the line starts with "usemtl"
                if line.startswith("usemtl"):
                    l = line.strip().split(" ")
                    style.append(l[1])

        with open('material_mapping.json', 'r') as file:
            data = json.load(file)

        material_mappings = data['material_mapping']
        for mapping in material_mappings:
            material = mapping['material']
            radiance_material = mapping['radiance_material']
            print(f"Material: {material}, Radiance Material: {radiance_material}")

        # Create materials.rad file
        materials_file = os.path.join(radiance_dir, "materials.rad")
        with open(materials_file, "w") as file:
            file.write("void plastic white\n0\n0\n5 1 1 1 0 0\n")
            file.write("void plastic blue_plastic\n0\n0\n5 0.1 0.2 0.8 0.05 0.1\n");
            file.write("void plastic red_plastic\n0\n0\n5 0.8 0.1 0.2 0.05 0.1\n");
            file.write("void metal silver_metal\n0\n0\n5 0.8 0.8 0.8 0.9 0.1\n");
            file.write("void glass clear_glass\n0\n0\n3 0.96 0.96 0.96\n");
            file.write("void light white_light\n0\n0\n3 1.0 1.0 1.0\n");
            file.write("void trans olive_trans\n0\n0\n7 0.6 0.7 0.4 0.05 0.05 0.7 0.2\n");

            for i in set(style):
                for j in material_mappings:
                    if j['material'] == i:
                        file.write("inherit alias "+i+" "+j['radiance_material']+"\n")
                        break
            
            
        self.report({'INFO'}, "Exported Materials Rad file to: {}".format(materials_file))

        # Run obj2mesh
        rtm_file = os.path.join(radiance_dir, "model.rtm")
        subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file])


        # Create scene.rad file
        scene_file = os.path.join(radiance_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write("void mesh model\n1 model.rtm\n0\n0\n")

        self.report({'INFO'}, "Exported Scene file to: {}".format(scene_file))

        # Get camera parameters

        CameraArray = []
        

        for obj in bpy.context.scene.objects:
            if obj.type == "CAMERA":
                cam = {}
                cam['obj'] = obj
                cam['location'] = obj.location
                cam['up'] = obj.matrix_world.to_quaternion() @ mathutils.Vector((0.0, 1.0, 0.0))
                cam['direction'] = obj.matrix_world.to_quaternion() @ mathutils.Vector((0.0, 0.0, -1.0))
                CameraArray.append(cam)
        self.report({'INFO'}, "{}".format(CameraArray))
        
        

        # Get bounding box of the scene
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for coord in obj.bound_box:
                    min_x = min(min_x, coord[0])
                    max_x = max(max_x, coord[0])
                    min_y = min(min_y, coord[1])
                    max_y = max(max_y, coord[1])
                    min_z = min(min_z, coord[2])
                    max_z = max(max_z, coord[2])
        
        #  Self report all the values for Zone E
        self.report({'INFO'}, "min_x: {}".format(min_x))
        self.report({'INFO'}, "max_x: {}".format(max_x))
        self.report({'INFO'}, "min_y: {}".format(min_y))
        self.report({'INFO'}, "max_y: {}".format(max_y))
        self.report({'INFO'}, "min_z: {}".format(min_z))
        self.report({'INFO'}, "max_z: {}".format(max_z))
        

        # Create scene.rif file
        rif_file = os.path.join(radiance_dir, "scene.rif")
        with open(rif_file, "w") as file:
            file.write("# Specify where the compiled octree should be generated\n")
            file.write("OCTREE=scene.oct\n")
            file.write("# Specify an (I)nterior or (E)xterior scene, along with the bounding box of the scene, obtainable via `getbbox scene.rad`\n")
            file.write("ZONE=E {} {} {} {} {} {}\n".format(min_x, max_x, min_y, max_y, min_z, max_z))
#            file.write("ZONE=E -2.25546 4.06512 -3.15161 3.16896 -2.94847 3.3721\n")
            file.write("# A list of of the rad files which make up our scene\n")
            file.write("scene=scene.rad\n")
            file.write("# Camera view options\n")
            for cam in CameraArray:
                location = cam['location']
                direction = cam['direction']
                up = cam['up']
                file.write("view=-vp {} {} {} -vd {} {} {} -vu {} {} {}\n".format(
                    location.x, location.y, location.z,
                    direction.x, direction.y, direction.z,
                    up.x, up.y, up.z
                ))
            file.write("# Option overrides to specify when rendering\n")
            file.write("render=-av 1 1 1 -pa {}\n".format(aspect_ratio))
            file.write("# Choose how indirect the lighting is\n")
            file.write("INDIRECT=2\n")
            file.write("# Choose the quality of the image, from LOW, MEDIUM, or HIGH\n")
            file.write("QUALITY=MEDIUM\n")
            file.write("# Choose the resolution of mesh detail, from LOW, MEDIUM, or HIGH\n")
            file.write("DETAIL=MEDIUM\n")
            file.write("# Choose the light value variance variability, from LOW, MEDIUM, or HIGH\n")
            file.write("VARIABILITY=MEDIUM\n")
            file.write("# Reolution of the image\n")
            file.write("RESOLUTION={} {}\n".format(resolution_x, resolution_y))
            file.write("# Where to output the raw render\n")
            file.write("RAWFILE=output_raw\n")
            file.write("# Where to output a filtered version of the render (scaled down for antialiasing, exposure correction, etc)\n")
            file.write("PICTURE=output\n")
            file.write("# The time duration in minutes before reporting a status update of the render progress\n")
            file.write("REPORT=0.1\n")

        try:
            process = subprocess.run(["rad", rif_file],cwd=radiance_dir, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            print(e)
            self.report({'ERROR'}, "Radiance rendering failed. Error: {}".format(e.stdout))
            return {'CANCELLED'}

        self.report({'INFO'}, "Radiance rendering completed. Output: {}".format(os.path.join(radiance_dir, "output.pic")))
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RadianceExporterPanel)
    bpy.utils.register_class(ExportRadiance)

    bpy.types.Scene.radiance_resolution_x = bpy.props.IntProperty(
        name="X",
        description="Horizontal resolution of the output image",
        default=1920,
        min=1
    )

    bpy.types.Scene.radiance_resolution_y = bpy.props.IntProperty(
        name="Y",
        description="Vertical resolution of the output image",
        default=1080,
        min=1
    )

def unregister():
    bpy.utils.unregister_class(RadianceExporterPanel)
    bpy.utils.unregister_class(ExportRadiance)

if __name__ == "__main__":
    register()
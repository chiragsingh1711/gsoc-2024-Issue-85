import os
import pyradiance as pr

import bpy
import subprocess
import mathutils
import time

from pathlib import Path
from typing import Union, Optional, Sequence


import json

import ifcopenshell
import ifcopenshell.geom
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


from bpy.props import StringProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper


def save_obj2mesh_output(inp: Union[bytes, str, Path], output_file: str, **kwargs):
        output_bytes = pr.obj2mesh(inp, **kwargs)
        with open(output_file, 'wb') as f:
            f.write(output_bytes)


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
        row.prop(scene, "ifc_file_name")
        
        row = layout.row()
        row.label(text="Resolution")
        row.prop(scene, "radiance_resolution_x", text="X")
        
        row = layout.row()
        row.label(text="")
        row.prop(scene, "radiance_resolution_y", text="Y")
        
        row = layout.row()
        row.prop(scene, "radiance_quality")
        
        row = layout.row()
        row.prop(scene, "radiance_detail")
        
        row = layout.row()
        row.prop(scene, "radiance_variability")
        
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
        try:
            # Get the resolution from the user input
            resolution_x, resolution_y = self.getResolution(context)
            quality = context.scene.radiance_quality.upper()
            detail = context.scene.radiance_detail.upper()
            variability = context.scene.radiance_variability.upper()
            
            # Calculate the aspect ratio
            aspect_ratio = resolution_x / resolution_y

            # Get the blend file path and create the "Radiance Rendering" directory
            self.report({'INFO'}, "Exporting Radiance files...")
            blend_file_path = bpy.data.filepath
            if not blend_file_path:
                self.report({'ERROR'}, "Please save the Blender file before exporting.")
                return {'CANCELLED'}

            blend_file_dir = os.path.dirname(blend_file_path)
            radiance_dir = os.path.join(blend_file_dir, "RadianceRendering")
            
            self.report({'INFO'}, "Radiance directory: {}".format(radiance_dir))

            if not os.path.exists(radiance_dir):
                os.makedirs(radiance_dir)

            try:
                # IFC file export and processing
                settings = ifcopenshell.geom.settings()
                # Settings for obj
                settings.set(settings.STRICT_TOLERANCE, True)
                settings.set(settings.INCLUDE_CURVES, True)
                settings.set(settings.USE_ELEMENT_GUIDS, True)
                settings.set(settings.APPLY_DEFAULT_MATERIALS, True)
                settings.set(settings.USE_WORLD_COORDS, True)

                ifc_file_name = context.scene.ifc_file_name
                ifc_file_path = os.path.join(blend_file_dir, f"{ifc_file_name}.ifc")
                
                if not os.path.exists(ifc_file_path):
                    self.report({'ERROR'}, f"IFC file not found: {ifc_file_path}")
                    return {'CANCELLED'}
                

                ifc_file = ifcopenshell.open(ifc_file_path)

                obj_file_path = os.path.join(radiance_dir, "model.obj")
                mtl_file_path = os.path.join(radiance_dir, "model.mtl")
                

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

            except Exception as e:
                self.report({'ERROR'}, f"Error in IFC processing: {str(e)}")
                return {'CANCELLED'}

            try:
                # Material processing
                style = []
                with open(obj_file_path, "r") as obj_file:
                    # Iterate through each line in the file
                    for line in obj_file:
                        # Check if the line starts with "usemtl"
                        if line.startswith("usemtl"):
                            l = line.strip().split(" ")
                            style.append(l[1])

                with open('material_mapping.json', 'r') as file:
                    data = json.load(file)

                material_mappings = data['material_mapping']
                
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

            except Exception as e:
                self.report({'ERROR'}, f"Error in material processing: {str(e)}")
                return {'CANCELLED'}


            try:
                # Run obj2mesh
                rtm_file = os.path.join(radiance_dir, "model.rtm")
                # subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file], check=True)
                save_obj2mesh_output(obj_file_path, rtm_file, matfiles=[materials_file])
                
                # Create scene.rad file
                scene_file = os.path.join(radiance_dir, "scene.rad")
                with open(scene_file, "w") as file:
                    file.write("void mesh model\n1 "+rtm_file+"\n0\n0\n")

                self.report({'INFO'}, "Exported Scene file to: {}".format(scene_file))

            except Exception as e:
                self.report({'ERROR'}, f"Error creating scene file: {str(e)}")
                return {'CANCELLED'}

            try:
                # Py Radiance code
                scene = pr.Scene("ascene")

                material_path = os.path.join(radiance_dir, "materials.rad")
                scene_path = os.path.join(radiance_dir, "scene.rad")
                # skyglow_path = os.path.join(radiance_dir, "skyglow.rad")

                scene.add_material(material_path)
                scene.add_surface(scene_path)
                # scene.add_source(skyglow_path)

                aview = pr.View(position=(1, 1.5, 1), direction=(1, 0, 0))
                scene.add_view(aview)

                print("Reached here")
                image = pr.render(scene, ambbounce=1, resolution=(resolution_x, resolution_y),
                      quality=quality, detail=detail, variability=variability)
                xres, yres = pr.get_image_dimensions(image)
                pixels = pr.pvalue(image, header=False, outform='f', resstr=False)
                iar = np.frombuffer(pixels, dtype=np.single).reshape(xres, yres, 3)
                luminance = iar[:, :, 0] * 47.4 + iar[:, :, 1] * 119.9 + iar[:, :, 2] * 11.6

                
                # using a viridis color map
                cmap = plt.cm.viridis
                # setup a logrithm normalizer
                norm = LogNorm()
                plt.axis("off")
                fimage = cmap(norm(luminance))
                # plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), label=r"$\mathrm{cd/m^2}$")

                raw_hdr_path = os.path.join(radiance_dir, "raw.hdr")
                with open(raw_hdr_path, "wb") as wtr:
                    wtr.write(image)

                timage = pr.pcond(raw_hdr_path, human=True)
                tpix = pr.pvalue(timage, header=False, resstr=False, outform='f')
                tiar = np.frombuffer(tpix, dtype=np.single).reshape(xres, yres, 3)
                plt.imshow(tiar * (1.0 / 2.2))

                self.report({'INFO'}, "Radiance rendering completed. Output: {}".format(os.path.join(radiance_dir, "output.pic")))
                return {'FINISHED'}

            except Exception as e:
                self.report({'ERROR'}, f"Error in Radiance rendering: {str(e)}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {str(e)}")
            return {'CANCELLED'}

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

    bpy.types.Scene.ifc_file_name = bpy.props.StringProperty(
        name="IFC File Name",
        description="Name of the IFC file to use (without .ifc extension)",
        default="AC20-FZK-Haus"
    )

    bpy.types.Scene.radiance_quality = bpy.props.EnumProperty(
        name="Quality",
        description="Radiance rendering quality",
        items=[
            ('LOW', "Low", "Low quality"),
            ('MEDIUM', "Medium", "Medium quality"),
            ('HIGH', "High", "High quality")
        ],
        default='MEDIUM'
    )

    bpy.types.Scene.radiance_detail = bpy.props.EnumProperty(
        name="Detail",
        description="Radiance rendering detail",
        items=[
            ('LOW', "Low", "Low detail"),
            ('MEDIUM', "Medium", "Medium detail"),
            ('HIGH', "High", "High detail")
        ],
        default='MEDIUM'
    )

    bpy.types.Scene.radiance_variability = bpy.props.EnumProperty(
        name="Variability",
        description="Radiance rendering variability",
        items=[
            ('LOW', "Low", "Low variability"),
            ('MEDIUM', "Medium", "Medium variability"),
            ('HIGH', "High", "High variability")
        ],
        default='MEDIUM'
    )

def unregister():
    bpy.utils.unregister_class(RadianceExporterPanel)
    bpy.utils.unregister_class(ExportRadiance)
    del bpy.types.Scene.radiance_resolution_x
    del bpy.types.Scene.radiance_resolution_y
    del bpy.types.Scene.ifc_file_name
    del bpy.types.Scene.radiance_quality
    del bpy.types.Scene.radiance_detail
    del bpy.types.Scene.radiance_variability

if __name__ == "__main__":
    register()
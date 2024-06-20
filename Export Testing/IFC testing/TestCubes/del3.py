import os
import ifcopenshell
import ifcopenshell.geom
import multiprocessing
import bpy

# Get the currently loaded IFC file from the Blender BIM addon
ifc_file = bpy.context.scene.BIMProperties.ifc_file

if ifc_file:
    # Get the directory path of the current blend file
    blend_file_path = bpy.data.filepath
    blend_file_directory = os.path.dirname(blend_file_path)

    # Create a new directory for the output files
    output_directory = os.path.join(blend_file_directory, "output")
    os.makedirs(output_directory, exist_ok=True)

    settings = ifcopenshell.geom.settings()

    # Settings for obj
    settings.set(settings.STRICT_TOLERANCE, True)
    settings.set(settings.INCLUDE_CURVES, True)
    settings.set(settings.USE_ELEMENT_GUIDS, True)
    settings.set(settings.APPLY_DEFAULT_MATERIALS, True)
    settings.set(settings.USE_WORLD_COORDS, True)

    # Specify the output file paths relative to the blend file's location
    obj_file_path = os.path.join(output_directory, "output.obj")
    mtl_file_path = os.path.join(output_directory, "output.mtl")

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
else:
    print("No IFC file is currently loaded in Blender.")
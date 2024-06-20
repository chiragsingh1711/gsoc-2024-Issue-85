import os
import ifcopenshell
import bpy
import ifcopenshell.geom
import multiprocessing

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

# Specify the input IFC file path

ifc_file_path = 'C:/Users/Chirag Singh/Desktop/gsoc-Phase1/Export Testing/IFC testing/TestCubes/Cubes.ifc'

# Open the IFC file
ifc_file = ifcopenshell.open(ifc_file_path)

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
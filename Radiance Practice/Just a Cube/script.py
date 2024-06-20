import bpy
from mathutils import Vector

cam = bpy.data.objects['Camera']
location = cam.location
up = cam.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
direction = cam.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))

print(
    '-vp ' + str(location.x) + ' ' + str(location.y) + ' ' +  str(location.z) + ' ' +
    '-vd ' + str(direction.x) + ' ' + str(direction.y) + ' ' + str(direction.z) + ' ' +
    '-vu ' + str(up.x) + ' ' + str(up.y) + ' ' + str(up.z)
)
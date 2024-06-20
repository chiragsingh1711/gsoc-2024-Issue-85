import os
from matplotlib.colors import LogNorm
import pyradiance as pr

# Set the current working directory
os.chdir("C:/Users/Chirag Singh/Desktop/gsoc-Phase1/PyRadiance testing")

scene = pr.Scene("ascene")

# Absolute paths for materials and surfaces
material_path = os.path.join(os.getcwd(), "Objects/materials.rad")
exterior_walls_path = os.path.join(os.getcwd(), "Objects/ExteriorWalls.rad")
interior_wall_path = os.path.join(os.getcwd(), "Objects/InteriorWall.rad")
ceiling_path = os.path.join(os.getcwd(), "Objects/Ceiling.rad")
floor_path = os.path.join(os.getcwd(), "Objects/Floor.rad")
skyglow_path = os.path.join(os.getcwd(), "Objects/skyglow.rad")

scene.add_material(material_path)
scene.add_surface(exterior_walls_path)
scene.add_surface(interior_wall_path)
scene.add_surface(ceiling_path)
scene.add_surface(floor_path)
scene.add_source(skyglow_path)

aview = pr.View(position=(1, 1.5, 1), direction=(1, 0, 0))
scene.add_view(aview)

print("Reached here")
image = pr.render(scene, ambbounce=1)

import numpy as np
xres, yres = pr.get_image_dimensions(image)
pixels = pr.pvalue(image, header=False, outform='f', resstr=False)
iar = np.frombuffer(pixels, dtype=np.single).reshape(xres, yres, 3)
luminance = iar[:, :, 0] * 47.4 + iar[:, :, 1] * 119.9 + iar[:, :, 2] * 11.6

import matplotlib.pyplot as plt
# using a viridis color map
cmap = plt.cm.viridis
# setup a logrithm normalizer
norm = LogNorm()
plt.axis("off")
fimage = cmap(norm(luminance))
plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), label=r"$\mathrm{cd/m^2}$")

raw_hdr_path = os.path.join(os.getcwd(), "raw.hdr")
with open(raw_hdr_path, "wb") as wtr:
    wtr.write(image)

timage = pr.pcond(raw_hdr_path, human=True)
tpix = pr.pvalue(timage, header=False, resstr=False, outform='f')
tiar = np.frombuffer(tpix, dtype=np.single).reshape(xres, yres, 3)
plt.imshow(tiar * (1.0 / 2.2))
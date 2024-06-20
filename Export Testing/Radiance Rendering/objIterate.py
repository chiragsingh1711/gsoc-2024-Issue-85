# Open the OBJ file for reading


# C:/Users/Chirag Singh/Desktop/gsoc-Phase1/Export Testing/Radiance Rendering

style = []
styleId = []
other = []

with open(f"C:/Users/Chirag Singh/Desktop/gsoc-Phase1/Export Testing/Radiance Rendering/model.obj", "r") as obj_file:
    # Iterate through each line in the file
    for line in obj_file:
        # Check if the line starts with "usemtl"
        if line.startswith("usemtl"):
            # Print the line
            l = line.strip().split(" ")
            # print(l[1].split("-"))
            style.append(l[1])
            if(len(l[1].split("-")) > 2):
                styleId.append(l[1].split("-")[3])
            else:
                other.append(l[1])

for i in set(style):
    s = ""
    print("inherit alias "+i+" white")
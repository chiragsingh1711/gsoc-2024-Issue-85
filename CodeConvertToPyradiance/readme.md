# Radiance Exporter for Blender

This Blender add-on allows you to export and render your scene using Radiance, directly from within Blender. It provides a user-friendly interface to set rendering parameters and export your IFC model for Radiance rendering.

## Installation and Usage

1. **Prepare Your IFC Model**:
   Place your target IFC model in the same directory as your `scene.blend` file.

2. **Open the Blender File**:
   Open `scene.blend` in Blender, and import the IFC project you just added.

3. **Add the Script**:

   - Copy the code from `transfer2.py`.
   - In Blender, go to the Scripting workspace.
   - Create a new text file in the Text Editor.
   - Paste the copied code into this new text file.

4. **Run the Script**:
   Click the "Run Script" button or press Alt+P to execute the script.

5. **Access the Radiance Exporter Panel**:
   After running the script, a new section titled "Radiance Exporter" will appear in the Render Properties panel.

6. **Set Rendering Parameters**:

   - Set the desired resolution by adjusting the X and Y dimensions.
   - Choose the Quality, Detail, and Variability settings (Medium is recommended for each).

7. **Export and Render**:

   - Click the "Export and Render" button.
   - Note: In the current version, you may encounter errors on the first and second attempts.
   - Try clicking the "Export and Render" button up to three times. The output image should be generated on the third attempt.

8. **View Results**:
   After successful rendering, you can find the output image in the "RadianceRendering" folder, located in the same directory as your Blender file.

## Troubleshooting

- Ensure that Radiance is properly installed on your system and accessible from the command line.
- If you encounter persistent errors, check the Blender System Console for more detailed error messages.
- Verify that the IFC file is correctly placed and named in the same directory as the Blender file.

## Notes

- This add-on is currently in development, and some features may not work as expected.
- The need for multiple render attempts is a known issue that will be addressed in future updates.

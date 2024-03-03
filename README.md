# Piglet Automation
This repository contains files developed for the IiA project that automate Piglet's input and output processes. It simplifies input files and automates data iterations for piles and soil types, generating charts essential for pile design and geotechnical reports.

# General Instructions for Installation:
1. Save the "Piglet" folder to the C:\ directory. Do not modify any of its contents.
2. Install Rhino 7.
3. Install Grasshopper plugins:
	1. Right-click on the files located in the subfolder of “Piglet” named "gh plugins."
  	2. Click on "Unblock" -> Apply -> Ok.
  	3. Unzip the folders.
  	4. Move their contents to the following path: C:\Users\Name.Surname\AppData\Roaming\Grasshopper\Libraries.
4. For file “huiinstall_1”:
  	1. Right-click on the file "huiinstall_1".
  	2. Click on "Arup - Request Run as Admin."
  	3. Wait for confirmation of the request and proceed with the installation until completion.

# Excel Input Instructions:

**Warnings:**
- It is possible to change the beginning of the Excel input file name but always leave " _piglet_input" at the end (e.g., "24.02.01Project1_piglet_input").
- Be careful not to place two different Excel input files in the same location. There's a risk that the results of one analysis may overwrite those of the previous one. Always create separate folders to analyze different Excel input sheets.
- Pay attention to the number of options selected in the dropdown menu located in cell B1 of the "Ground Data" and "Piles Data" pages. Make sure you have chosen the correct number to avoid lengthening the analysis time with unnecessary iterations.
- Do not change the names of the sheets in this Excel input.
- Do not change the position of the sheets in this Excel input.

**Limits:**
- Maximum of 12 Load Cases.
- Maximum of 30 piles.
- Maximum of 10 options for Piles Data.
- Maximum of 10 options for Ground Data.
- Maximum of 3 diverse options for Axial Capacity per each Pile Option.
- All piles with the same Axial Capacity must have the same length within the same Option (e.g., 5 piles with Axial Capacity 5080, L= 23 m, 3 piles with 4000 Axial Capacity, L= 20 m, etc.).
- On the "Armature MN" page, you can input up to a maximum of 6 Armatures, which will be applied to all iterations.

# Instructions  for Starting a New Project:
1. Copy and paste the contents of the "to copy" subfolder into the folder you want to use for the new project. This folder will be used for processing data and saving diagrams.
2. Open the input Excel file ending with "_piglet_input" and enter the project data following the instructions on the first page named "Instructions."
3. Once data input is complete, save and close the file.
4. Double-click on the Grasshopper script named "IiA_Piglet_Earthworm_Script" and wait for the interface to appear.
5. Click on "Browse" to find the recently saved input Excel file and select it.
6. Click once on the toggle "Turn ON to Read Piglet Inputs" and wait for it to turn green. After reading the Excel file, the interface will indicate the number of iterations specified in the input file (number of Ground options x number of Pile options).
7. To proceed with the analysis, click once on the toggle "Turn ON to Run Piglet Analysis" and wait for it to turn green. If changes to the input are needed, deactivate the first toggle, reopen the input Excel file, make necessary modifications, save, and click the first toggle again to read the new file.
8. Along with the " _piglet_input" Excel file and the Grasshopper script, a "Piglet_Output" folder will be created with two subfolders ("DIAGRAMS" and "JSON") and two .exe files. Do not modify them; they will be automatically used by the script.
9. Once the "Turn ON to Run Piglet Analysis" toggle is green, click on the "Turn ON to Plot Piglet Charts" toggle. This will modify the Excel files in the "DIAGRAMS" folder. When this toggle turns green, enter the "DIAGRAMS" folder to review the Excel files containing the charts. The script generates one Excel document per iteration specified in the Input sheet.
10. Now, review each Excel file, examine the results, and adjust chart filters if needed (default filters show all Load Cases and Piles). 
**Tip:** Avoid modifying the default zoom in Excel sheets; scroll vertically or horizontally without zooming.
11. Once satisfied with the charts and ready to export, save and close all modified Excel files. Go back to the Piglet interface and click once on the last toggle "Turn ON to Export Piglet Charts." Wait; this step may take a few minutes depending on the number of iterations. The script will export the diagrams by automatically opening each Excel file and navigating through all pages. Wait until this process finishes, and the toggle turns green. The interface will indicate where the images of each diagram have been saved.
12. Check the designated folder to ensure the export of all diagrams meets expectations.
13. If you want to repeat the analysis or analyze new input Excel files, disable all four toggles in reverse order and select the "Browse" option to locate the path of the new input file. 
**Warning:** Ensure it is not located with the previously used input file to avoid data overwriting issues.

# Next Steps:
1. **Investigate Depth-Related Shear and Moment Issues:**
   - Dive deeper into the issue of shear and moment related to depth, potentially by modifying the Earthworm plugin to obtain the relevant data and ensure the functionality of charts on the "T and M with Depth" page.

2. **Earthworm Plugin on Arup Compute:**
- Explore the possibility of making the Earthworm plugin available in Arup Compute for broader accessibility and usage.

3. **Expand Options with Iteration Filtering:**
- Expand the available options of Piles, Ground and Load Cases, allowing for the ability to filter the iterations to be analysed.

4. **Alp Calibration Integration:**
- Evaluate Alp compatibility and seamless incorporation for calibration within the workflow.

5. **Integrate the Developed Workflow into AWF or TDA:**
   - Integrate the developed workflow into platforms like AWF or TDA to elevate the level of automation. This will facilitate easier access to the developed tools and processes.


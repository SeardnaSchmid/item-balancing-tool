# Building the Executable for Windows

## Option 1: If you have Windows

1. Make sure you have Python installed on your Windows machine.
2. Open a command prompt and navigate to the item-balancing-tool folder.
3. Run the build script:
   ```
   python build_exe.py
   ```
4. Wait for the build to complete (this may take a few minutes).
5. Once done, you'll find the executable in the `dist` folder.
6. Share the entire `dist` folder with your friend. They only need to run the .exe file.

## Option 2: Using a Virtual Machine or WSL

If you're building on Linux but want to create a Windows executable:

1. Set up a Windows virtual machine (using VirtualBox, VMware, etc.)
2. Copy the entire project folder to the VM
3. Install Python on the VM
4. Follow the steps in Option 1

## Option 3: Using a Cross-Compilation Service

There are online services that can build Windows executables from Python code:

1. GitHub Actions can be configured to build Windows executables
2. There are commercial services that offer this functionality

## Sharing with Your Friend

1. Zip the entire `dist` folder (which contains the .exe and data.json)
2. Send the zip file to your friend
3. Include the user_guide.md file for instructions

## What Your Friend Needs to Do

1. Extract the zip file to a folder on their computer
2. Double-click the .exe file to run the application
3. A web browser will open with the tool running

That's it! They don't need to install Python or any dependencies.

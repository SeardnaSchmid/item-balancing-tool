"""
Build script for creating a standalone Windows executable of the Item Balancing Tool.
This script uses PyInstaller to package the application into a single .exe file.
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    print("Building Item Balancing Tool Executable...")
    
    # Check if PyInstaller is installed, install if not
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean up previous build artifacts if they exist
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Removing old {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    if os.path.exists('item_balancer.spec'):
        os.remove('item_balancer.spec')
    
    # Create the PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=ItemBalancingTool",
        "--onefile",
        "--windowed",  # No console window
        "--icon=NONE",  # You can add an icon file here if you have one
        "--add-data=data.json;.",  # Include data.json in the package
        "app.py"
    ]
    
    # On Linux/Mac, use colon instead of semicolon for path separators
    if platform.system() != "Windows":
        cmd[5] = "--add-data=data.json:."
    
    # Run PyInstaller
    print("Running PyInstaller to create executable...")
    subprocess.check_call(cmd)
    
    # Create a simple readme file for the distribution
    with open("dist/README.txt", "w") as f:
        f.write("""Item Balancing Tool

Thank you for using the Item Balancing Tool!

Instructions:
1. Keep data.json in the same folder as the executable
2. Double-click ItemBalancingTool.exe to run the application
3. The app will open in your default web browser

Note: The first time you run the app, Windows may show a security warning.
Click "More info" and then "Run anyway" to proceed.
""")
    
    print("\nBuild completed successfully!")
    print("\nThe executable is located in the 'dist' folder.")
    print("Share the 'dist' folder with your friend. They just need to run ItemBalancingTool.exe")

if __name__ == "__main__":
    main()

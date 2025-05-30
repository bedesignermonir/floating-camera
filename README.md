Download the code first
open the folder and go to folder addressbar and type cmd on addressber and press enter
when the cmd is open type python ok.py
now your camera is showing up as a circle webcam
ctrl + scroll up to zoom the circle and scroll down to zoom out
alt + scroll up to zoom the camera inside circle and scroll down to zoom out inside the circle.

If you have any question then feel free ask me on telegram: https://t.me/teamabccom



note:

Install Python:

Go to the official Python website: https://www.python.org/downloads/
Download the latest stable version of Python for Windows (usually "Windows installer (64-bit)").
IMPORTANT: During the installation, make sure to check the box that says "Add Python.exe to PATH". This is crucial for running Python commands easily from your command prompt.
Complete the installation.
Install Libraries:

Open your Command Prompt (search for "cmd" in the Windows search bar and open it).
Type the following commands one by one and press Enter after each:
Bash

pip install opencv-python
pip install numpy
pip install Pillow
pip install tk
opencv-python: This is the library we'll use to capture video from your webcam and process image data.
numpy: This is a fundamental library for numerical operations in Python, often used with OpenCV.
Pillow (PIL Fork): This will help us with image manipulation, specifically for creating the circular mask.
tk: This is Python's standard GUI (Graphical User Interface) toolkit, which we'll use to create the floating window.

Save the File:

Click "File" -> "Save As...".
Navigate to a folder where you want to save your script (e.g., your Documents folder, or create a new folder like C:\FloatingWebcam).
Name the file floating_webcam.py (make sure the .py extension is there).
Set "Save as type" to "All Files" if you're using Notepad, to ensure it doesn't add a .txt extension.

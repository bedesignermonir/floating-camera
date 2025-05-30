#This code is made by bedesignermonir
# run this command.
# pip install opencv-python-headless Pillow


import cv2
import tkinter as tk
from tkinter import Label, ttk
from PIL import Image, ImageTk, ImageDraw
import time
import ctypes

# For high-DPI awareness on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    pass
except Exception as e:
    print(f"DPI Awareness error: {e}")

# Global variables
current_zoom_level = 1.0 # For resizing the entire circle (Ctrl+Alt+Scroll)
internal_zoom_level = 1.0 # For zooming *within* the circle (Alt+Scroll)

# Function to update the webcam feed
def update_frame():
    global last_frame_time, current_zoom_level, internal_zoom_level

    current_time = time.time() * 1000  # current time in milliseconds
    
    # Get current window size (which should be square after on_window_configure)
    current_window_size = root.winfo_width() 
    circle_diameter = current_window_size
    
    if current_time - last_frame_time >= frame_delay:
        ret, frame = cap.read()
        if ret:
            h, w, _ = frame.shape
            # print(f"DEBUG: Original Webcam Frame Size: {w}x{h}") # Debugging original frame size

            # --- CROPPING LOGIC with Internal Zoom ---
            # Calculate the dimensions of the square we want to crop from the *original* frame
            base_crop_side = min(w, h)
            
            effective_crop_side = int(base_crop_side / internal_zoom_level)
            
            # Ensure effective_crop_side doesn't exceed original dimensions and is at least 1
            effective_crop_side = max(1, min(effective_crop_side, base_crop_side))

            # Calculate starting coordinates for the centered crop based on the effective_crop_side
            start_x = (w - effective_crop_side) // 2
            start_y = (h - effective_crop_side) // 2
            
            # Ensure coordinates are within bounds
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = start_x + effective_crop_side
            end_y = start_y + effective_crop_side

            # Adjust end_x/end_y if they somehow went out of bounds (shouldn't with max/min)
            end_x = min(w, end_x)
            end_y = min(h, end_y)

            cropped_frame = frame[start_y:end_y, start_x:end_x]
            
            # print(f"DEBUG: Cropped Frame Size (before resize): {cropped_frame.shape[1]}x{cropped_frame.shape[0]}") # Debugging
            
            # Check if cropped_frame is empty before resizing
            if cropped_frame.shape[0] == 0 or cropped_frame.shape[1] == 0:
                print("WARNING: Cropped frame is empty, skipping update.")
                lmain.after(10, update_frame)
                return

            # Resize the cropped frame to the current desired circle_diameter (window size)
            resized_frame = cv2.resize(cropped_frame, (circle_diameter, circle_diameter), interpolation=cv2.INTER_AREA)
            # print(f"DEBUG: Resized Frame Size (for display): {resized_frame.shape[1]}x{resized_frame.shape[0]}") # Debugging

            # Convert to RGB format
            cv2image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            
            # Create a circular mask and apply it
            mask = Image.new("L", (circle_diameter, circle_diameter), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, circle_diameter, circle_diameter), fill=255)
            
            img.putalpha(mask) # Apply the circular mask as an alpha channel
            
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update the image on the canvas
            if hasattr(lmain, 'image_id'):
                lmain.delete(lmain.image_id)
            lmain.image_id = lmain.create_image(0, 0, image=imgtk, anchor=tk.NW, tags="webcam_feed")
            lmain.imgtk = imgtk # Keep a reference

        last_frame_time = current_time
    
    # Schedule the next update
    lmain.after(10, update_frame)

# Create the main window
root = tk.Tk()
root.title("Floating Webcam")
root.attributes("-topmost", True)  # Keep the window on top

# Set a unique background color for transparency on Windows
transparent_color = '#010101' # A very dark gray, almost black
root.config(bg=transparent_color)
root.wm_attributes('-transparentcolor', transparent_color)

# Remove window decorations (borders, title bar)
root.overrideredirect(True)

# Initial window size
initial_size = 400 

# Open the webcam
cap = cv2.VideoCapture(0) 

# --- OPTIONAL: Uncomment and adjust these lines if your webcam's default resolution is too low ---
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) 
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# --------------------------------------------------------------------------------------------------

desired_fps = 30 
frame_delay = int(1000 / desired_fps)  
last_frame_time = 0

# Create a Canvas to display the webcam feed and handles
lmain = tk.Canvas(root, bg=transparent_color, highlightthickness=0) # No border for canvas
lmain.pack(fill=tk.BOTH, expand=True)  # Make the canvas expand to fit the window

# --- Function to set initial geometry after Tkinter has started ---
def set_initial_geometry():
    root.geometry(f"{initial_size}x{initial_size}")
    on_window_configure(None) # Force a configure event to update handle positions and image

# Schedule the initial geometry setting
root.after(1, set_initial_geometry) 

# --- Resizing Logic (using explicit handles) ---
resize_handle_size = 15 # Size of the corner resize squares
resize_handles = {}
active_handle = None
_resize_start_x = 0
_resize_start_y = 0
_resize_start_width = 0
_resize_start_height = 0
_resize_start_window_x = 0
_resize_start_window_y = 0

def create_resize_handles():
    # Clear existing handles
    for tag in ["resize_handle_nw", "resize_handle_ne", "resize_handle_sw", "resize_handle_se"]:
        lmain.delete(tag)

    # Positions are relative to the canvas
    # ALL HANDLES ARE CREATED WITH state='hidden' AND WILL REMAIN HIDDEN
    resize_handles["nw"] = lmain.create_rectangle(0, 0, resize_handle_size, resize_handle_size, 
        fill='gray', outline='white', tags='resize_handle_nw', state='hidden')
    resize_handles["ne"] = lmain.create_rectangle(root.winfo_width() - resize_handle_size, 0, root.winfo_width(), resize_handle_size,
        fill='gray', outline='white', tags='resize_handle_ne', state='hidden')
    resize_handles["sw"] = lmain.create_rectangle(0, root.winfo_height() - resize_handle_size, resize_handle_size, root.winfo_height(),
        fill='gray', outline='white', tags='resize_handle_sw', state='hidden')
    resize_handles["se"] = lmain.create_rectangle(root.winfo_width() - resize_handle_size, root.winfo_height() - resize_handle_size,
        root.winfo_width(), root.winfo_height(),
        fill='gray', outline='white', tags='resize_handle_se', state='hidden')

    # Bind events to the tags created - these bindings still allow resizing if you manage to click
    # the hidden areas (e.g., via keyboard navigation or if you change state='normal' temporarily)
    for handle_type, handle_id in resize_handles.items():
        lmain.tag_bind(handle_id, "<ButtonPress-1>", lambda e, h_type=handle_type: start_resize(e, h_type))
        lmain.tag_bind(handle_id, "<B1-Motion>", do_resize)
        lmain.tag_bind(handle_id, "<ButtonRelease-1>", lambda e: set_active_handle(None))

def set_active_handle(handle_type):
    global active_handle
    active_handle = handle_type

def start_resize(event, handle_type):
    global active_handle, _resize_start_x, _resize_start_y, \
           _resize_start_width, _resize_start_height, \
           _resize_start_window_x, _resize_start_window_y
    
    active_handle = handle_type # Set the active handle directly
    _resize_start_x = event.x_root
    _resize_start_y = event.y_root
    _resize_start_width = root.winfo_width()
    _resize_start_height = root.winfo_height()
    _resize_start_window_x = root.winfo_x()
    _resize_start_window_y = root.winfo_y()

def do_resize(event):
    if not active_handle:
        return

    dx = event.x_root - _resize_start_x
    dy = event.y_root - _resize_start_y

    new_width = _resize_start_width
    new_height = _resize_start_height
    new_x = _resize_start_window_x
    new_y = _resize_start_window_y

    min_window_size = 100 # Minimum size for the window

    if 'e' in active_handle: # East side
        new_width = max(min_window_size, _resize_start_width + dx)
    if 's' in active_handle: # South side
        new_height = max(min_window_size, _resize_start_height + dy)
    if 'w' in active_handle: # West side
        new_width = max(min_window_size, _resize_start_width - dx)
        new_x = _resize_start_window_x + dx
    if 'n' in active_handle: # North side
        new_height = max(min_window_size, _resize_start_height - dy)
        new_y = _resize_start_window_y + dy

    # Always maintain a square aspect ratio for the circle
    target_size = min(new_width, new_height)
    new_width = target_size
    new_height = target_size
    
    # Adjust x,y if resizing from top/left to keep the top-left corner in place
    if 'w' in active_handle:
        new_x = _resize_start_window_x + (_resize_start_width - new_width)
    if 'n' in active_handle:
        new_y = _resize_start_window_y + (_resize_start_height - new_height)

    root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    # The on_window_configure callback will handle updating the canvas and webcam feed

# This function is called whenever the window size changes
def on_window_configure(event):
    current_width = root.winfo_width()
    current_height = root.winfo_height()

    # Ensure the window remains square
    new_size = min(current_width, current_height)
    if current_width != new_size or current_height != new_size:
        root.geometry(f"{new_size}x{new_size}")
        current_width = new_size # Update for consistency
        current_height = new_size

    # Redraw and position resize handles - they are created as hidden, so they stay hidden
    create_resize_handles()
    
    # Trigger webcam update to redraw image at new size
    update_frame()


# Function to handle dragging of the window (for moving the window)
# Modified to require Ctrl + Click
def start_move(event):
    # Check if Ctrl key is pressed and if not over a resize handle
    # The handles are now hidden, so the check `lmain.find_withtag(tk.CURRENT) not in resize_handles.values()`
    # is still good practice but less critical for visibility.
    if (event.state & 0x4): # 0x4 is Ctrl
        global x, y
        x = event.x
        y = event.y
    else:
        x = None # Do not initiate move if Ctrl not pressed

def do_move(event):
    global x, y
    if x is not None and y is not None: # Only move if start_move was initiated
        deltax = event.x - x
        deltay = event.y - y
        root.geometry(f"+{root.winfo_x() + deltax}+{root.winfo_y() + deltay}")

# Bind mouse events to handle window dragging on the canvas
lmain.bind("<Button-1>", start_move)
lmain.bind("<B1-Motion>", do_move)

# --- Close Button (REMOVED) and Hover Controls (NOW COMPLETELY REMOVED FOR VISIBILITY) ---

# The close button widget is no longer created or placed.
# The show_controls and hide_controls functions are now removed as they are no longer needed
# to manage the visibility of the "X" button or resize handles.
# The resize handles are created as 'hidden' and stay hidden.

# Remove the root.bind('<Enter>', show_controls) and root.bind('<Leave>', hide_controls)
# as they are no longer needed.


# --- Keyboard Binding for Exit ---
def exit_app(event):
    if event.keysym == 'q': 
        root.destroy()

root.bind('<Key>', exit_app) 

# --- Ctrl + Alt + Mouse Scroll for Full Circle Zoom (Resize) ---
def zoom_window_size(event):
    global current_zoom_level, initial_size
    
    # Check for Ctrl (0x4) and Alt (0x8) modifiers
    if (event.state & 0x4) and (event.state & 0x8): 
        if event.delta > 0: # Scroll up (zoom in)
            current_zoom_level *= 1.1 
        else: # Scroll down (zoom out)
            current_zoom_level *= 0.9 

        current_zoom_level = max(0.2, min(current_zoom_level, 5.0)) # Min 20%, Max 500%

        new_size = int(initial_size * current_zoom_level)
        min_window_size = 100
        new_size = max(new_size, min_window_size)

        current_x = root.winfo_x()
        current_y = root.winfo_y()

        old_center_x = current_x + root.winfo_width() / 2
        old_center_y = current_y + root.winfo_height() / 2
        
        new_x = int(old_center_x - new_size / 2)
        new_y = int(old_center_y - new_size / 2)

        root.geometry(f"{new_size}x{new_size}+{new_x}+{new_y}")

# --- Alt + Mouse Scroll for Internal Camera Zoom ---
def zoom_camera_feed(event):
    global internal_zoom_level
    
    # Check for Alt (0x8) modifier ONLY, and NOT Ctrl (0x4)
    if (event.state & 0x8) and not (event.state & 0x4): 
        if event.delta > 0: # Scroll up (zoom in)
            internal_zoom_level *= 1.1 
        else: # Scroll down (zoom out)
            internal_zoom_level *= 0.9 

        internal_zoom_level = max(1.0, min(internal_zoom_level, 3.0)) 
        
        # Force a frame update to apply the new internal zoom
        update_frame()


# Bind mouse wheel event with modifiers to the root window
# The 'add="+ "' ensures both MouseWheel bindings work simultaneously
root.bind('<MouseWheel>', zoom_window_size) 
root.bind('<MouseWheel>', zoom_camera_feed, add="+") 


# Run the main loop
root.mainloop()

# Release the webcam when the window is closed
cap.release()
cv2.destroyAllWindows()
# Import all required modules
from tkinter import *
from tkinter import filedialog, messagebox
import ctypes
import win32gui
import numpy as np
import json
from PIL import Image, ImageTk, ImageGrab
from keras.models import load_model


# Initialize the Tkinter window and load CNN model
def initialize():
    top = Tk()
    top.geometry("300x350")
    top.title("Multilanguage Handwritten Character Recognition")
    model = load_model("./train/model.h5")
    with open("./train/mappings.json") as f:
        json_dict = json.load(f)
    mappings = {int(k): v for k, v in json_dict.items()}
    return top, model, mappings


# This function is fired when the user clicks on the "Clear" button
def clear():
    canvas.delete("all")


# This function is fired when the user clicks on the "Predict button"
def predict():
    # Get the windows handle ID for the canvas
    canvas_handle = canvas.winfo_id()
    # Get the canvas window's coordinates from ID using win32 API
    canvas_rect = win32gui.GetWindowRect(canvas_handle)
    # Grab the canvas' content
    img = ImageGrab.grab(canvas_rect)
    # Resize the content for CNN input
    # We've trained our model to work with 32x32 images
    img = img.resize((32, 32)).convert("L")
    img = np.array(img)
    img = img.reshape((1, 32, 32, 1))
    # Scale down pixel values from 0-255 to 0-1
    img = img / 255
    # Predict which character is drawn on the convas
    Y = model.predict([img])[0]
    class_ = np.argmax(Y)
    # Display the result of the prediction
    messagebox.showinfo("Prediction", "I believe it's the {}".format(mappings[class_]))


# This function is fired when the user clicks on the "Upload" button
def upload_image():
    # Define global variable to prevent image from getting garbage collected
    global img
    # Specify which file types can be selected within the file selection dialog
    filetypes = (("png files (*.png)", "*.png"), ("jpg files (*.jpg)", "*.jpg"))
    try:
        # Display the file selection dialog and save the path of the image file
        filename = filedialog.askopenfilename(
            title="Select an image", filetypes=filetypes
        )
        # Read image from path and resize to (300, 300) to fit on canvas
        img = ImageTk.PhotoImage(Image.open(filename).resize((300, 300)))
        # Put image on canvas
        canvas.create_image(0, 0, anchor=NW, image=img)
    except:
        pass


# This function is fired whenever user drags their mouse on the canvas while using the
# left click
def mouse_event(event):
    x, y = event.x, event.y
    canvas.create_oval(x, y, x, y, fill="white", outline="white", width=25)


if __name__ == "__main__":
    # Fixes issue of Tkinter not recognizing screen resolution correctly
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # windows >= 8.1
    except:
        ctypes.windll.user32.SetProcessDPIAware()  # win 8.0 or less

    # Initialize Tkinter window and load CNN model
    (root, model, mappings) = initialize()
    # Create a frame element to hold the buttons
    button_frame = Frame(root)
    # Create a canvas element to provide space to the user to draw characters
    canvas = Canvas(root, bg="black", height=300, width=300)
    # Bind an event to the canvas
    # Fire mouse_event() whenever mouse is dragged on canvas with left click on
    canvas.bind("<B1-Motion>", mouse_event)
    # Create 3 action buttons:
    #   to clear the canvas
    #   to use what's on the canvas as input
    #   to use an image as input
    clear_button = Button(button_frame, text="Clear", command=clear)
    predict_button = Button(button_frame, text="Predict", command=predict)
    upload_button = Button(button_frame, text="Upload", command=upload_image)
    # Draw GUI elements on screen
    canvas.pack()
    clear_button.pack(side="left")
    upload_button.pack(side="right")
    predict_button.pack(side="right")
    button_frame.pack()
    # Start event loop
    root.mainloop()

'''
 User Interface

'''
import tkinter as tk
from tkinter import ttk, filedialog
from constants import *
def initialize(main):

# Function to open file dialog and update input file path
  def select_input_file():
      file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
      if file_path:
          input_file_var.set(file_path)

  # Function to update constants based on checkbox states
  def update_constants():
      CREATE_PDF = create_pdf_var.get()
      if CREATE_PDF: 
        show_pdf_checkbox.config(state=tk.NORMAL)
        SHOW_PDF = show_pdf_var.get()
      else:
        SHOW_PDF = False
        show_pdf_var.set(False)
        show_pdf_checkbox.config(state=tk.DISABLED)

      SHOW_IMAGE = show_image_var.get()

  # Create the main window
  root = tk.Tk()
  root.title("Meta-Pixel Configuration")

  # Create variables for checkboxes
  create_pdf_var = tk.BooleanVar(value=CREATE_PDF)
  show_pdf_var = tk.BooleanVar(value=SHOW_PDF)
  show_image_var = tk.BooleanVar(value=SHOW_IMAGE)

  # Create checkboxes
  create_pdf_checkbox = ttk.Checkbutton(root, text="Create PDF", variable=create_pdf_var, command=update_constants)
  show_pdf_checkbox = ttk.Checkbutton(root, text="Show PDF", variable=show_pdf_var, command=update_constants)
  show_image_checkbox = ttk.Checkbutton(root, text="Show Image", variable=show_image_var, command=update_constants)

  # Create a button that calls the main function
  create_button = ttk.Button(root, text="CREATE", command=main)

  # Layout checkboxes and button
  create_pdf_checkbox.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
  show_pdf_checkbox.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
  show_image_checkbox.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
  create_button.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)

  # Create variable and label for input file
  input_file_var = tk.StringVar()
  input_file_label = tk.Label(root, text="Input File", width=20)
  input_file_entry = tk.Entry(root, textvariable=input_file_var, width=50)
  input_file_button = ttk.Button(root, text="Select Input File", command=select_input_file)

  # Layout input file widgets
  input_file_label.grid(row=5, column=0, padx=10, pady=5)
  input_file_entry.grid(row=5, column=1, padx=10, pady=5)
  input_file_button.grid(row=5, column=2, padx=10, pady=5)


  # Run the main loop
  root.mainloop()

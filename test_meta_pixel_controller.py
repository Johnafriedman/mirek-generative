import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from meta_pixel_controller import Controller, Model
from PIL import Image

class TestMetaPixelController(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.app = Controller(self.model)
        self.app.update_idletasks()
        self.image = MagicMock(spec=Image)

    def tearDown(self):
        self.app.destroy()

    def test_load_all_widgets(self):
        # Mock the methods called by load_all_widgets
        self.app.load_input_widgets = MagicMock()
        self.app.load_output_file_widgets = MagicMock()
        self.app.load_output_widgets = MagicMock()
        self.app.load_shapes_widgets = MagicMock()
        self.app.load_analysis_widgets = MagicMock()
        self.app.load_color_widgets = MagicMock()

        # Call the method under test
        self.app.load_all_widgets()

        # Verify that each method was called once
        self.app.load_input_widgets.assert_called_once()
        self.app.load_output_file_widgets.assert_called_once()
        self.app.load_output_widgets.assert_called_once()
        self.app.load_shapes_widgets.assert_called_once()
        self.app.load_analysis_widgets.assert_called_once()
        self.app.load_color_widgets.assert_called_once()

    def test_load_input_widgets(self):
        self.app.entry_input_dir = tk.Entry(self.app)
        self.app.model.input_dir = "test_input_dir"
        self.app.load_input_widgets()
        self.assertEqual(self.app.entry_input_dir.get(), "test_input_dir")

    def test_load_output_file_widgets(self):
        self.app.entry_output_dir = tk.Entry(self.app)
        self.app.model.output_dir = "test_output_dir"
        self.app.load_output_file_widgets()
        self.assertEqual(self.app.entry_output_dir.get(), "test_output_dir")

    def test_load_output_widgets(self):
        self.app.entry_files = tk.Entry(self.app)
        self.app.model.files = "test_files"
        self.app.load_output_widgets()
        self.assertEqual(self.app.entry_files.get(), "test_files")

    def test_load_shapes_widgets(self):
        self.app.entry_shapes = tk.Entry(self.app)
        self.app.model.shapes = "test_shapes"
        self.app.load_shapes_widgets()
        self.assertEqual(self.app.entry_shapes.get(), "test_shapes")

    def test_load_analysis_widgets(self):
        self.app.entry_edge_min = tk.Entry(self.app)
        self.app.model.edge_min = "test_edge_min"
        self.app.load_analysis_widgets()
        self.assertEqual(self.app.entry_edge_min.get(), "test_edge_min")

    def test_load_color_widgets(self):
        self.app.entry_transparent_threshold = tk.Entry(self.app)
        self.app.model.transparent_threshold = "test_transparent_threshold"
        self.app.load_color_widgets()
        self.assertEqual(self.app.entry_transparent_threshold.get(), "test_transparent_threshold")

if __name__ == '__main__':
    unittest.main()
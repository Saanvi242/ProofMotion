"""
tests/test_image_processing.py
------------------------------
Unit and integration tests for CGIP image processing algorithms.
Verifies manual implementations of:
- Grayscale conversion (ITU-R BT.601 luminance weighting)
- Binary thresholding
- Gaussian smoothing and 2D convolution
- Mean box filtering
- Median filtering
- Sobel edge detection (Gx, Gy, magnitude)
- Canny edge detection (OpenCV reference)
- Boundary handling and error validations
"""

import unittest
import numpy as np
import cgip.image_processing as img_proc


class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        # Create a deterministic synthetic test pattern (50x50 RGB)
        self.img_rgb = img_proc.generate_synthetic_image("shapes", size=50)

    def test_manual_grayscale_weights(self):
        # Create pure Red, Green, Blue 1x1 test pixels
        # Pure Red: (255, 0, 0) -> 0.299 * 255 = 76.245 -> 76
        red_pixel = np.array([[[255, 0, 0]]], dtype=np.uint8)
        gray_r = img_proc.manual_grayscale(red_pixel)
        self.assertEqual(gray_r[0, 0], round(0.299 * 255))

        # Pure Green: (0, 255, 0) -> 0.587 * 255 = 149.685 -> 150
        green_pixel = np.array([[[0, 255, 0]]], dtype=np.uint8)
        gray_g = img_proc.manual_grayscale(green_pixel)
        self.assertEqual(gray_g[0, 0], round(0.587 * 255))

        # Pure Blue: (0, 0, 255) -> 0.114 * 255 = 29.07 -> 29
        blue_pixel = np.array([[[0, 0, 255]]], dtype=np.uint8)
        gray_b = img_proc.manual_grayscale(blue_pixel)
        self.assertEqual(gray_b[0, 0], round(0.114 * 255))

        # Grayscale image output shape & dtype
        gray = img_proc.manual_grayscale(self.img_rgb)
        self.assertEqual(gray.shape, (50, 50))
        self.assertEqual(gray.dtype, np.uint8)

    def test_manual_threshold(self):
        img_gray = np.array([
            [10, 50, 100],
            [127, 128, 200]
        ], dtype=np.uint8)

        binary = img_proc.manual_threshold(img_gray, thresh_val=128)
        self.assertEqual(binary.shape, (2, 3))
        self.assertEqual(binary.dtype, np.uint8)

        # Values < 128 become 0; values >= 128 become 255
        expected = np.array([
            [0, 0, 0],
            [0, 255, 255]
        ], dtype=np.uint8)
        np.testing.assert_array_equal(binary, expected)

    def test_gaussian_kernel_normalization(self):
        ksize = 5
        sigma = 1.0
        kernel = img_proc.manual_gaussian_kernel(ksize=ksize, sigma=sigma)
        self.assertEqual(kernel.shape, (5, 5))
        # Sum of Gaussian weights must equal 1.0
        self.assertAlmostEqual(float(np.sum(kernel)), 1.0, places=5)
        # Center of kernel must be the peak maximum
        self.assertEqual(kernel[2, 2], np.max(kernel))

    def test_manual_gaussian_blur(self):
        blurred = img_proc.manual_gaussian_blur(self.img_rgb, ksize=5, sigma=1.5)
        self.assertEqual(blurred.shape, self.img_rgb.shape)
        self.assertEqual(blurred.dtype, np.uint8)
        # Output values must be within valid uint8 range [0, 255]
        self.assertTrue(np.all(blurred >= 0))
        self.assertTrue(np.all(blurred <= 255))

    def test_manual_mean_blur(self):
        mean_blurred = img_proc.manual_mean_blur(self.img_rgb, ksize=5)
        self.assertEqual(mean_blurred.shape, self.img_rgb.shape)
        self.assertEqual(mean_blurred.dtype, np.uint8)

    def test_manual_median_filter_noise_reduction(self):
        # Create an image with isolated salt-and-pepper impulse noise
        clean_img = np.full((15, 15), 100, dtype=np.uint8)
        noisy_img = clean_img.copy()
        noisy_img[7, 7] = 255  # impulse spike at center

        filtered = img_proc.manual_median_filter(noisy_img, ksize=3)
        self.assertEqual(filtered.shape, clean_img.shape)
        # Center impulse spike must be filtered out to neighborhood median (100)
        self.assertEqual(filtered[7, 7], 100)

    def test_manual_sobel_edge_detection(self):
        # Step edge: left half black (0), right half white (255)
        step_img = np.zeros((20, 20), dtype=np.uint8)
        step_img[:, 10:] = 255

        mag, gx, gy = img_proc.manual_sobel(step_img)
        self.assertEqual(mag.shape, (20, 20))
        self.assertEqual(mag.dtype, np.uint8)

        # Vertical edge must produce significant horizontal gradient Gx at boundary column
        self.assertGreater(np.max(np.abs(gx[:, 9:11])), 100.0)
        # Horizontal gradient Gy should be zero or negligible for vertical edge
        self.assertLess(np.max(np.abs(gy)), 1e-4)

    def test_opencv_canny_reference(self):
        edges = img_proc.opencv_canny_reference(self.img_rgb, low_thresh=50, high_thresh=150)
        self.assertEqual(edges.shape, (50, 50))
        self.assertEqual(edges.dtype, np.uint8)

    def test_invalid_input_handling(self):
        with self.assertRaises(ValueError):
            img_proc.manual_grayscale(None)

        with self.assertRaises(FileNotFoundError):
            img_proc.load_image("non_existent_image_file.png")

    def test_image_file_save_and_load(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_path = os.path.join(tmp_dir, "test_output.png")
            # Save synthetic image
            success = img_proc.save_image(test_path, self.img_rgb)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(test_path))

            # Reload and verify contents
            reloaded = img_proc.load_image(test_path)
            self.assertEqual(reloaded.shape, self.img_rgb.shape)
            np.testing.assert_array_equal(reloaded, self.img_rgb)

    def test_build_image_step(self):
        step = img_proc.build_image_step(self.img_rgb, "gaussian", {"kernel_size": 5, "sigma": 1.2})
        self.assertEqual(step.title, "Image Studio: GAUSSIAN")
        self.assertIn("original_array", step.values)
        self.assertIn("processed_array", step.values)
        self.assertEqual(step.render_data.mode, "image")
        self.assertIsNotNone(step.render_data.image_data["original"])
        self.assertIsNotNone(step.render_data.image_data["processed"])
        self.assertIn("px", step.render_data.image_data["orig_dims"])


if __name__ == "__main__":
    unittest.main()


"""
cgip/image_processing.py
------------------------
Genuine Computer Graphics and Image Processing (CGIP) Algorithms.

Contains authentic mathematical and algorithmic implementations:
- Manual Grayscale Conversion: Y = 0.299R + 0.587G + 0.114B (ITU-R BT.601)
- Manual Binary Thresholding: dst(x, y) = 255 if src(x, y) >= T else 0
- Manual Gaussian Filter: 2D Gaussian kernel generation and spatial convolution
- Manual Mean Box Filter: Uniform neighborhood averaging
- Manual Median Filter: Non-linear spatial filter for impulse noise removal
- Manual Sobel Edge Detection: Gx, Gy convolution kernels and magnitude sqrt(Gx² + Gy²)
- OpenCV Reference Canny Edge Detection (explicitly documented as library-assisted)
- Image file I/O validation and conversion to PyQt5 QImage
"""

import os
import math
import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional, List
from PyQt5.QtGui import QImage
from core.step_model import VisualizationStep, RenderData


# --------------------------------------------------------------------------
# Image Format & PyQt Conversion Helpers
# --------------------------------------------------------------------------
def numpy_to_qimage(img_np: np.ndarray) -> QImage:
    """Convert RGB/BGR/Grayscale NumPy array to PyQt5 QImage safely."""
    if img_np is None:
        return QImage()

    img_contiguous = np.ascontiguousarray(img_np)

    if len(img_contiguous.shape) == 2:
        # Grayscale (H, W) uint8
        h, w = img_contiguous.shape
        bytes_per_line = w
        gray_uint8 = np.uint8(np.clip(img_contiguous, 0, 255))
        return QImage(gray_uint8.data, w, h, bytes_per_line, QImage.Format_Grayscale8).copy()

    elif len(img_contiguous.shape) == 3:
        h, w, ch = img_contiguous.shape
        if ch == 3:
            # Assume RGB uint8
            bytes_per_line = 3 * w
            rgb_uint8 = np.uint8(np.clip(img_contiguous, 0, 255))
            return QImage(rgb_uint8.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        elif ch == 4:
            bytes_per_line = 4 * w
            rgba_uint8 = np.uint8(np.clip(img_contiguous, 0, 255))
            return QImage(rgba_uint8.data, w, h, bytes_per_line, QImage.Format_RGBA8888).copy()

    return QImage()


def load_image(filepath: str) -> np.ndarray:
    """
    Load an image from disk with validation.
    Returns RGB uint8 NumPy array.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Image file not found: {filepath}")

    bgr = cv2.imread(filepath, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Failed to decode image file: {filepath}. Supported formats: PNG, JPG, BMP, WebP.")

    if len(bgr.shape) < 2 or bgr.shape[0] == 0 or bgr.shape[1] == 0:
        raise ValueError("Invalid image dimensions (image is empty).")

    # Convert BGR (OpenCV default) to RGB for internal consistency
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb


def save_image(filepath: str, img: np.ndarray) -> bool:
    """
    Save RGB or Grayscale NumPy array to disk.
    """
    if img is None:
        raise ValueError("Cannot save None image.")

    if len(img.shape) == 3 and img.shape[2] == 3:
        # Convert RGB to BGR for OpenCV writer
        out_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        out_img = img

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    success = cv2.imwrite(filepath, out_img)
    if not success:
        raise IOError(f"Failed to write image to {filepath}")
    return True


def generate_synthetic_image(pattern: str = "shapes", size: int = 300) -> np.ndarray:
    """
    Generate high-contrast geometric test images in RGB format.
    """
    img = np.zeros((size, size, 3), dtype=np.uint8)

    if pattern == "shapes":
        # Background: Dark navy
        img[:] = (20, 26, 32)
        # Gold rectangle: (216, 169, 78) in RGB
        cv2.rectangle(img, (40, 40), (140, 140), (216, 169, 78), -1)
        # Teal circle: (78, 199, 176) in RGB
        cv2.circle(img, (200, 180), 55, (78, 199, 176), -1)
        # Coral diagonal line: (228, 104, 93) in RGB
        cv2.line(img, (30, 260), (270, 70), (228, 104, 93), 4)
        # Green triangle: (89, 196, 138) in RGB
        pts = np.array([[70, 200], [140, 270], [30, 270]], np.int32)
        cv2.fillPoly(img, [pts], (89, 196, 138))

    elif pattern == "checkerboard":
        cell = size // 8
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    img[i*cell:(i+1)*cell, j*cell:(j+1)*cell] = (225, 230, 235)
                else:
                    img[i*cell:(i+1)*cell, j*cell:(j+1)*cell] = (30, 36, 44)

    elif pattern == "salt_and_pepper":
        # High contrast background with impulse noise
        img[:] = (60, 70, 85)
        cv2.circle(img, (size//2, size//2), size//3, (216, 169, 78), -1)
        # Add random salt-and-pepper impulse noise
        rng = np.random.RandomState(42)
        num_noise = int(size * size * 0.08)
        # Salt (white)
        ys = rng.randint(0, size, num_noise // 2)
        xs = rng.randint(0, size, num_noise // 2)
        img[ys, xs] = (255, 255, 255)
        # Pepper (black)
        ys_p = rng.randint(0, size, num_noise // 2)
        xs_p = rng.randint(0, size, num_noise // 2)
        img[ys_p, xs_p] = (0, 0, 0)

    else:
        # Smooth grayscale gradient
        for y in range(size):
            val = int(255 * (y / size))
            img[y, :] = (val, val, val)

    return img


# --------------------------------------------------------------------------
# Genuine CGIP Backend Algorithms (Manual Implementations)
# --------------------------------------------------------------------------

def manual_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Genuine manual Grayscale conversion using ITU-R BT.601 standard luminance weights:
    Y = 0.299 * R + 0.587 * G + 0.114 * B

    Inputs:
        img: (H, W, 3) RGB or (H, W) Grayscale NumPy array.
    Returns:
        (H, W) uint8 grayscale image.
    """
    if img is None:
        raise ValueError("Input image cannot be None.")

    if len(img.shape) == 2:
        return np.uint8(np.clip(img, 0, 255)).copy()

    if len(img.shape) == 3 and img.shape[2] >= 3:
        r = img[:, :, 0].astype(np.float64)
        g = img[:, :, 1].astype(np.float64)
        b = img[:, :, 2].astype(np.float64)

        # Standard ITU-R BT.601 luma formula
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        return np.uint8(np.clip(np.round(luma), 0, 255))

    raise ValueError(f"Unsupported image shape for grayscale conversion: {img.shape}")


def manual_threshold(img: np.ndarray, thresh_val: int = 128) -> np.ndarray:
    """
    Genuine manual binary thresholding:
    dst(x, y) = 255 if src(x, y) >= thresh_val else 0

    Inputs:
        img: RGB or Grayscale NumPy array.
        thresh_val: integer cutoff in [0..255].
    Returns:
        (H, W) uint8 binary image.
    """
    gray = manual_grayscale(img)
    thresh_val = max(0, min(255, int(thresh_val)))
    binary = np.where(gray >= thresh_val, np.uint8(255), np.uint8(0))
    return binary


def manual_convolve2d(img: np.ndarray, kernel: np.ndarray, pad_mode: str = "edge") -> np.ndarray:
    """
    Genuine 2D spatial convolution of a 2D single-channel image with an arbitrary 2D kernel.
    Handles image boundaries via boundary reflection / clamping (pad_mode="edge").
    """
    h, w = img.shape
    kh, kw = kernel.shape
    pad_h = kh // 2
    pad_w = kw // 2

    # Pad boundaries
    padded = np.pad(img.astype(np.float64), ((pad_h, pad_h), (pad_w, pad_w)), mode=pad_mode)

    # 2D correlation / convolution with flipped kernel
    k_flipped = np.flip(np.flip(kernel, 0), 1)

    # Vectorized sliding window extraction using stride tricks or fast window accumulation
    from numpy.lib.stride_tricks import as_strided
    shape = (h, w, kh, kw)
    strides = (padded.strides[0], padded.strides[1], padded.strides[0], padded.strides[1])
    windows = as_strided(padded, shape=shape, strides=strides)

    # Element-wise multiply and sum over kernel axes
    convolved = np.einsum('ijkl,kl->ij', windows, k_flipped)
    return convolved


def manual_gaussian_kernel(ksize: int = 5, sigma: float = 1.0) -> np.ndarray:
    """
    Generate normalized 2D Gaussian convolution kernel:
    G(x, y) = (1 / 2πσ²) · e^(-(x² + y²) / 2σ²)
    """
    if ksize % 2 == 0:
        ksize += 1
    ksize = max(3, ksize)
    sigma = max(0.1, float(sigma))

    radius = ksize // 2
    y, x = np.mgrid[-radius:radius+1, -radius:radius+1]
    kernel = np.exp(-(x**2 + y**2) / (2.0 * sigma**2))
    kernel_sum = kernel.sum()
    if kernel_sum > 0:
        kernel = kernel / kernel_sum
    return kernel


def manual_gaussian_blur(img: np.ndarray, ksize: int = 5, sigma: float = 1.5) -> np.ndarray:
    """
    Genuine manual Gaussian smoothing filter.
    Calculates Gaussian weights and performs 2D spatial convolution.
    Works for single-channel grayscale and multi-channel RGB.
    """
    kernel = manual_gaussian_kernel(ksize=ksize, sigma=sigma)

    if len(img.shape) == 2:
        convolved = manual_convolve2d(img, kernel)
        return np.uint8(np.clip(np.round(convolved), 0, 255))
    elif len(img.shape) == 3:
        channels = []
        for ch in range(img.shape[2]):
            c_conv = manual_convolve2d(img[:, :, ch], kernel)
            channels.append(np.uint8(np.clip(np.round(c_conv), 0, 255)))
        return np.stack(channels, axis=2)

    raise ValueError(f"Unsupported image shape for Gaussian blur: {img.shape}")


def manual_mean_blur(img: np.ndarray, ksize: int = 5) -> np.ndarray:
    """
    Genuine manual Mean (Box) Smoothing filter.
    Replaces each pixel with the arithmetic mean of its (ksize x ksize) neighborhood.
    """
    if ksize % 2 == 0:
        ksize += 1
    ksize = max(3, ksize)
    kernel = np.ones((ksize, ksize), dtype=np.float64) / (ksize * ksize)

    if len(img.shape) == 2:
        convolved = manual_convolve2d(img, kernel)
        return np.uint8(np.clip(np.round(convolved), 0, 255))
    elif len(img.shape) == 3:
        channels = []
        for ch in range(img.shape[2]):
            c_conv = manual_convolve2d(img[:, :, ch], kernel)
            channels.append(np.uint8(np.clip(np.round(c_conv), 0, 255)))
        return np.stack(channels, axis=2)

    raise ValueError(f"Unsupported image shape for mean blur: {img.shape}")


def manual_median_filter(img: np.ndarray, ksize: int = 5) -> np.ndarray:
    """
    Genuine manual Median filter.
    Replaces each pixel with the statistical median value in its (ksize x ksize) window.
    Effective for removing salt-and-pepper impulse noise while preserving sharp boundaries.
    """
    if ksize % 2 == 0:
        ksize += 1
    ksize = max(3, ksize)
    radius = ksize // 2

    def filter_2d(channel_2d: np.ndarray) -> np.ndarray:
        h, w = channel_2d.shape
        padded = np.pad(channel_2d, radius, mode="edge")
        from numpy.lib.stride_tricks import as_strided
        shape = (h, w, ksize, ksize)
        strides = (padded.strides[0], padded.strides[1], padded.strides[0], padded.strides[1])
        windows = as_strided(padded, shape=shape, strides=strides)
        # Flatten the (ksize, ksize) windows to (h, w, ksize*ksize) and take median
        flat_windows = windows.reshape(h, w, ksize * ksize)
        med = np.median(flat_windows, axis=2)
        return np.uint8(np.clip(np.round(med), 0, 255))

    if len(img.shape) == 2:
        return filter_2d(img)
    elif len(img.shape) == 3:
        channels = [filter_2d(img[:, :, ch]) for ch in range(img.shape[2])]
        return np.stack(channels, axis=2)

    raise ValueError(f"Unsupported image shape for median filter: {img.shape}")


def manual_sobel(img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Genuine manual Sobel Edge Detection:
    Applies horizontal kernel Gx and vertical kernel Gy:
        Gx = [[-1,  0,  1],
              [-2,  0,  2],
              [-1,  0,  1]]

        Gy = [[-1, -2, -1],
              [ 0,  0,  0],
              [ 1,  2,  1]]

    Returns:
        (magnitude_uint8, grad_x_float, grad_y_float)
    """
    gray = manual_grayscale(img).astype(np.float64)

    kx = np.array([
        [-1.0, 0.0, 1.0],
        [-2.0, 0.0, 2.0],
        [-1.0, 0.0, 1.0]
    ], dtype=np.float64)

    ky = np.array([
        [-1.0, -2.0, -1.0],
        [ 0.0,  0.0,  0.0],
        [ 1.0,  2.0,  1.0]
    ], dtype=np.float64)

    gx = manual_convolve2d(gray, kx, pad_mode="edge")
    gy = manual_convolve2d(gray, ky, pad_mode="edge")

    # Gradient Magnitude = sqrt(Gx² + Gy²)
    mag = np.sqrt(gx**2 + gy**2)

    # Scale / clip to [0..255]
    mag_uint8 = np.uint8(np.clip(mag, 0, 255))
    return mag_uint8, gx, gy


def opencv_canny_reference(img: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> np.ndarray:
    """
    OpenCV-based Canny Edge Detector.
    Explicitly documented as an external reference comparison algorithm.
    """
    gray = manual_grayscale(img)
    low_thresh = max(0, min(255, int(low_thresh)))
    high_thresh = max(0, min(255, int(high_thresh)))
    return cv2.Canny(gray, low_thresh, high_thresh)


# --------------------------------------------------------------------------
# Dispatcher & Visualization Step Builder
# --------------------------------------------------------------------------

def process_image(
    img: np.ndarray,
    operation: str,
    params: Dict[str, Any] = None
) -> Tuple[np.ndarray, str, str]:
    """
    Executes the specified CGIP image processing operation.
    Returns: (processed_image, equation_str, explanation_str)
    """
    params = params or {}
    op = operation.lower()

    if op == "grayscale":
        proc = manual_grayscale(img)
        eq = "Y = 0.299·R + 0.587·G + 0.114·B  (ITU-R BT.601 Manual Implementation)"
        expl = ("Converts 3-channel RGB image to single-channel luminance using human eye sensitivity weights. "
                "Calculation executed manually via NumPy matrix arithmetic.")
        return proc, eq, expl

    elif op == "threshold":
        thresh_val = int(params.get("threshold", 128))
        proc = manual_threshold(img, thresh_val=thresh_val)
        eq = f"dst(x, y) = 255 if src(x, y) ≥ {thresh_val} else 0  (Manual Binary Segmentation)"
        expl = (f"Partitions pixels into foreground (255) and background (0) based on cutoff T={thresh_val}. "
                "Executed manually using direct pixel array threshold comparison.")
        return proc, eq, expl

    elif op == "gaussian":
        ksize = int(params.get("kernel_size", 5))
        if ksize % 2 == 0:
            ksize += 1
        sigma = float(params.get("sigma", 1.5))
        proc = manual_gaussian_blur(img, ksize=ksize, sigma=sigma)
        eq = (f"G(x, y) = (1 / 2πσ²) · exp(-(x² + y²) / 2σ²)\n"
              f"Kernel: {ksize}×{ksize},  σ = {sigma:.2f}  (Manual 2D Convolution)")
        expl = ("Low-pass Gaussian spatial filter. Generates continuous 2D Gaussian kernel coefficients "
                "and convolves over spatial neighborhoods with edge replication.")
        return proc, eq, expl

    elif op == "mean":
        ksize = int(params.get("kernel_size", 5))
        if ksize % 2 == 0:
            ksize += 1
        proc = manual_mean_blur(img, ksize=ksize)
        eq = f"dst(x, y) = (1 / {ksize}²) · ∑∑ src(x + i, y + j)  (Manual Box Mean Filter)"
        expl = ("Averages all pixels within rectangular neighborhood to attenuate high-frequency noise. "
                "Executed manually via 2D spatial neighborhood convolution.")
        return proc, eq, expl

    elif op == "median":
        ksize = int(params.get("kernel_size", 5))
        if ksize % 2 == 0:
            ksize += 1
        proc = manual_median_filter(img, ksize=ksize)
        eq = f"dst(x, y) = median( {ksize}×{ksize} neighborhood )  (Manual Median Filter)"
        expl = ("Non-linear filter replacing each center pixel with the statistical median of its neighborhood. "
                "Removes salt-and-pepper impulse noise while preserving sharp geometric edges.")
        return proc, eq, expl

    elif op == "sobel":
        mag, _, _ = manual_sobel(img)
        eq = ("Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]\n"
              "Gy = [[-1, -2, -1], [ 0, 0, 0], [ 1, 2, 1]]\n"
              "Magnitude = √(Gx² + Gy²)  (Manual Sobel Convolution)")
        expl = ("First-derivative gradient operator approximating horizontal and vertical spatial derivatives. "
                "Magnitude highlights steep intensity transitions corresponding to object boundaries.")
        return mag, eq, expl

    elif op == "canny":
        low_t = int(params.get("low_threshold", 50))
        high_t = int(params.get("high_threshold", 150))
        edges = opencv_canny_reference(img, low_thresh=low_t, high_thresh=high_t)
        eq = (f"Canny Multi-Stage Filter (OpenCV Library Reference):\n"
              f"Hysteresis Thresholds: Low = {low_t}, High = {high_t}")
        expl = ("Multi-stage edge detector providing library reference comparison: "
                "1) Gaussian smoothing, 2) Gradient computation, 3) Non-maximum suppression, 4) Dual-threshold hysteresis.")
        return edges, eq, expl

    return img.copy(), "Identity", "Unprocessed image."


def build_image_step(
    orig_np: np.ndarray,
    operation: str,
    params: Dict[str, Any] = None
) -> VisualizationStep:
    """
    Constructs a VisualizationStep with before/after QImages for rendering in the viewport.
    """
    proc_np, eq, expl = process_image(orig_np, operation, params)

    orig_ch = orig_np.shape[2] if len(orig_np.shape) > 2 else 1
    proc_ch = proc_np.shape[2] if len(proc_np.shape) > 2 else 1
    orig_dims = f"{orig_np.shape[1]} × {orig_np.shape[0]} px, {orig_ch} ch"
    proc_dims = f"{proc_np.shape[1]} × {proc_np.shape[0]} px, {proc_ch} ch"

    # For display rendering, if image is very large, downscale display preview for instant GUI fluidity
    max_disp_dim = 1000
    if max(orig_np.shape[:2]) > max_disp_dim:
        scale = max_disp_dim / float(max(orig_np.shape[:2]))
        new_w, new_h = int(orig_np.shape[1] * scale), int(orig_np.shape[0] * scale)
        disp_orig = cv2.resize(orig_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
        disp_proc = cv2.resize(proc_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        disp_orig = orig_np
        disp_proc = proc_np

    q_orig = numpy_to_qimage(disp_orig)
    q_proc = numpy_to_qimage(disp_proc)

    rd = RenderData(
        mode="image",
        image_data={
            "original": q_orig,
            "processed": q_proc,
            "orig_dims": orig_dims,
            "proc_dims": proc_dims,
            "title_orig": "Original Image (Input)",
            "title_proc": f"Processed Result ({operation.capitalize()})"
        }
    )

    return VisualizationStep(
        index=1,
        title=f"Image Studio: {operation.upper()}",
        equation=eq,
        explanation=expl,
        values={
            "operation": operation,
            "params": params or {},
            "original_array": orig_np,
            "processed_array": proc_np,
            "dimensions": (orig_np.shape[1], orig_np.shape[0])
        },
        metrics={
            "height": orig_np.shape[0],
            "width": orig_np.shape[1],
            "channels": orig_ch,
            "algorithm": operation
        },
        render_data=rd
    )

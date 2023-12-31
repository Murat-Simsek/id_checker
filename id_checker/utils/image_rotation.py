import cv2
import numpy as np
from skimage.color import rgb2gray
from skimage.transform import rotate
from skimage.transform import hough_line, hough_line_peaks
from scipy.stats import mode
from skimage.filters import threshold_otsu, sobel


class ImageRotation:
    def process_image(self, input_image_path, output_image_path):
        # Binarize image
        rgb_image = cv2.imread(input_image_path)
        image = rgb2gray(rgb_image)
        threshold = threshold_otsu(image)
        binarized_image = image < threshold

        # Find edges
        image_edges = sobel(binarized_image)

        # Find tilt angle
        h, theta, d = hough_line(image_edges)
        accum, angles, dists = hough_line_peaks(h, theta, d)

        if angles.size > 0:
            tilt_angle = np.rad2deg(angles[0])  # Use the first angle
        else:
            tilt_angle = None  # Handle the case of no lines

        # Only use mode calculation if angles have multiple values
        if angles.size > 1 and tilt_angle is None:
            tilt_angle = np.rad2deg(mode(angles)[0][0])

        if tilt_angle is not None:
            if tilt_angle < 0:
                tilt_angle = tilt_angle + 90
            else:
                tilt_angle = tilt_angle - 90

        # Rotate image
        img_rotated = rotate(rgb_image, tilt_angle)
        img_rotated = cv2.convertScaleAbs(img_rotated * 255)

        # Save the rotated image to the specified output path
        cv2.imwrite(output_image_path, img_rotated)

        return binarized_image, image_edges, tilt_angle

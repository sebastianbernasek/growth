import numpy as np
from copy import deepcopy

from ..measure import LognormalSampler


def disk(radius, dtype=int):
    """
    Returns flat disk structuring element.

    * Borrowed directly from scikit-image.

    """
    L = np.arange(-radius, radius + 1)
    X, Y = np.meshgrid(L, L)
    return np.array((X ** 2 + Y ** 2) <= radius ** 2, dtype=dtype)


class NucleusLabel:
    """
    Class for drawing an individual nucleus label on an existing image.
    """

    def __init__(self, xy, label=1, radius=6):
        """

        Args:

            xy (np.ndarray[float]) - nucleus position in cartesian coordinates

            label (int) - nucleus label

            radius (int) - nuclear radius, in pixels

        """

        self.xy = xy.astype(np.uint16)
        self.label = label
        self.radius = radius

        # define binary image mask
        self.circle_mask = disk(self.radius).astype(bool)
        self.build_fill_indices()

    @property
    def num_pixels(self):
        """ Number of pixels in nucleus. """
        return self.circle_mask.sum()

    def distort(self):
        """ Distort contour my manipulating binary mask. """
        pass

    def build_fill_indices(self):
        """ Constructs list of pixel indices spanned by nucleus. """
        xx,yy = np.array(np.meshgrid(*2*(range(-self.radius, self.radius+1),)))
        xx += self.xy[0]
        yy += self.xy[1]
        self.fill_indices = (xx[self.circle_mask].ravel(), yy[self.circle_mask].ravel())

    def _replace_pixels(self, im, values):
        """ Replace existing pixel values in <im> with <values>. """
        im[self.fill_indices] = values

    def draw(self, im):
        """
        Add nucleus label to <im>.

        Args:

            im (np.ndarray[float]) - 2D array of image pixels

            replace (bool) - if True, replace existing pixel values

        """
        labels = np.ones(self.num_pixels, dtype=int) * self.label
        self._replace_pixels(im, values=labels)


class Nucleus(NucleusLabel):
    """
    Class for drawing an indiviudal nucleus on an existing image.

    """

    def __init__(self, xy, mean, std=0.1, radius=6):
        """

        Args:

            xy (np.ndarray[float]) - nucleus position in cartesian coordinates

            mean (float) - mean fluorescence level

            std (float) - standard deviation of log-transformed pixel values

            radius (int) - nuclear radius, in pixels

        """

        self.xy = xy.astype(np.uint16)
        self.radius = radius

        # set mean expression level and measurement noise
        self.mu = np.log(mean)
        self.sigma = std

        # define binary image mask
        self.circle_mask = disk(self.radius).astype(bool)
        self.build_fill_indices()

    def _add_pixels(self, im, values):
        """ Add <values> to <im>. """
        im[self.fill_indices] = im[self.fill_indices] + values

    def draw(self, im, replace=False):
        """
        Sample individual pixel values and add to <im>.

        Args:

            im (np.ndarray[float]) - 2D array of image pixels

            replace (bool) - if True, replace existing pixel values

        """
        sampler = LognormalSampler(self.mu, self.sigma)

        if replace:
            self._replace_pixels(im, values=sampler(self.num_pixels))
        else:
            self._add_pixels(im, values=sampler(self.num_pixels))

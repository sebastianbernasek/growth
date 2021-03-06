from math import floor
import numpy as np
import matplotlib.pyplot as plt


class BatchVisualization:
    """
    Visualization methods for Sweep object.
    """

    @staticmethod
    def ordinal(n):
        """ Returns ordinal representation of <n>. """
        return "%d%s" % (n,"tsnrhtdd"[(floor(n/10)%10!=1)*(n%10<4)*n%10::4])

    def plot_culture_grid(self, size=1, title=False, square=True, **kwargs):
        """
        Plots grid of cell cultures.

        Args:

            size (int) - figure panel size

            title (bool) - if True, add title

            square (bool) - if True, truncate replicates to make a square grid

        Returns:

            fig (matplotlib.figures.Figure)

        """

        # determine figure shape
        ncols = int(np.floor(np.sqrt(self.size)))
        if square:
            nrows = ncols
        else:
            nrows = self.size // ncols
            if self.size % ncols != 0:
                nrows += 1
        npanels = nrows*ncols

        # create figure
        figsize = (ncols*size, nrows*size)
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

        # plot replicates
        for replicate_id in range(self.size):
            if replicate_id >= npanels:
                break

            ax = axes.ravel()[replicate_id]

            # load simulation
            sim = self[replicate_id]

            # plot culture
            sim.plot(ax=ax, **kwargs)

            # format axis
            if title:
                title = '{:s} replicate'.format(self.ordinal(replicate_id))
                ax.set_title(title, fontsize=8)

        for ax in axes.ravel():
            ax.axis('off')

        return fig

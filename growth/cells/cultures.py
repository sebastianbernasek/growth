from copy import deepcopy
import pickle
import numpy as np
from functools import reduce
from operator import add
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from .clones import Clones
from .phylogeny import Phylogeny
from ..spatial.triangulation import LocalTriangulation
from ..fluorescence.fluorescence import Fluorescence
from ..visualization.animation import Animation
from .cells import Cell


class CultureProperties:

    @property
    def cells(self):
        """ Current generation of cells. """
        return self.history[-1]

    @property
    def parents(self):
        """ Parent cells of current generation. """
        return self.history[-2]

    @property
    def size(self):
        """ Culture size. """
        return len(self.cells)

    @property
    def generation(self):
        return len(self.history) - 1

    @property
    def genotypes(self):
        """ Cell genotypes. """
        return np.array([cell.genotype for cell in self.cells])

    @property
    def phenotypes(self):
        """ Sampled cell phenotypes. """
        return self.fluorescence(self.genotypes)

    @property
    def xy_dict(self):
        """ Cell position dictionary keyed by cell index. """
        return {i: cell.xy for i, cell in enumerate(self.cells)}

    @property
    def xy(self):
        """ Cell positions. """
        return np.vstack([cell.xy for cell in self.cells])

    @property
    def triangulation(self):
        """ Delaunay triangulation with edge-length filtering. """
        return LocalTriangulation(*self.xy.T, max_length=0.1)

    @property
    def xy_graph(self):
        """ Graph of locally adjacent cells. """
        return nx.Graph(self.triangulation.edges.tolist())

    @property
    def labeled_graph(self):
        """ Graph of locally adjacent cells including cell genotypes. """
        G = self.xy_graph
        _ = [G.add_nodes_from(self.select(x), genotype=x) for x in range(3)]
        return G

    @property
    def heterogeneity(self):
        """ Returns fraction of edges that connect differing genotypes. """
        G = self.xy_graph
        num_edges = np.not_equal(*self.genotypes[np.array(G.edges)].T).sum()
        return num_edges / self.size

    @property
    def percent_heterozygous(self):
        """ Fraction of population with heterozygous chromosomes. """
        return (self.genotypes==1).sum() / self.size

    @property
    def generations(self):
        """ List of generation numbers. """
        return [cell.generation for cell in self.cells]

    @property
    def lineages(self):
        """ List of cell lineages. """
        return [cell.lineage for cell in self.cells]

    @property
    def dendrogram_edges(self):
        """ Dendrogram edge list. """
        return reduce(add, map(self.predecessor_search, self.lineages))

    @property
    def phylogeny(self):
        """ Phylogeny. """
        return Phylogeny(self.dendrogram_edges)

    @classmethod
    def predecessor_search(cls, lineage):
        """ Returns all predecessors of <lineage>. """
        edges = [(lineage[:-1], lineage)]
        if len(lineage) > 1:
            edges += cls.predecessor_search(lineage[:-1])
        return edges

    @property
    def diversification(self):
        """ Phylogenetic distance from earliest common ancestor. """
        spread = self.size / 2.
        indices = np.argsort(self.lineages)
        return ((indices - spread) / spread)  * self.scaling

    def select(self, genotype):
        """ Returns indices of cells with <genotype>.  """
        return (self.genotypes==genotype).nonzero()[0]

    def parse_clones(self, genotype):
        """ Returns properties for clones of specified <genotype>.  """
        clones = self.xy_graph.subgraph(self.select(genotype))
        return {
            'number': nx.connected.number_connected_components(clones),
            'sizes': [len(c) for c in nx.connected_components(clones)],
            'nodes': [np.array(c) for c in nx.connected_components(clones)]}

    @property
    def clones(self):
        """ Clones instance. """
        data = {genotype: self.parse_clones(genotype) for genotype in range(3)}
        return Clones(data)


class CultureVisualization:

    def animate(self, interval=500, **kwargs):
        """ Returns animation of culture growth. """
        freeze = np.vectorize(self.freeze)
        frames = freeze(np.arange(self.generation+1))
        animation = Animation(frames)
        video = animation.get_video(interval=interval, **kwargs)
        return video

    def plot(self,
             ax=None,
             colorby='genotype',
             tri=False,
             s=30,
             cmap=plt.cm.viridis):
        """
        Scatter cells in space.

        """

        # evaluate marker colors
        if colorby == 'genotype':
            norm = Normalize(0, 2)
            c = cmap(norm(self.genotypes))
        elif colorby == 'phenotype':
            norm = Normalize(0, 1)
            c = cmap(norm(self.phenotypes))
        elif colorby == 'lineage':
            norm = Normalize(-1, 1)
            c = cmap(norm(self.diversification))

        # create and format figure
        if ax is None:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)
            ax.set_aspect(1)
            ax.axis('off')

        # add triangulation
        if tri:
            ax.triplot(self.triangulation, 'r-', lw=1, alpha=1, zorder=0)

        # scatter points
        ax.scatter(*self.xy.T, s=s, lw=0, c=c)


class Culture(CultureProperties, CultureVisualization):

    def __init__(self, starter=None, fluorescence=None, scaling=1):

        # seed with four heterozygous cells
        if starter is None:
            starter = self.inoculate()
        self.history = [starter]

        # set fluorescence model
        if fluorescence is None:
            fluorescence = Fluorescence()
        self.fluorescence = fluorescence

        # set population size scaling
        self.scaling = scaling

    def __add__(self, b):
        return self.__class__(self.cells + b.cells)

    def save(self, filepath, save_history=True):
        """ Save pickled object to <path>. """

        # get object to be saved
        if save_history:
            obj = self
        else:
            obj = self.freeze(-1)

        # save object
        with open(filepath, 'wb') as file:
            pickle.dump(obj, file, protocol=-1)

    @staticmethod
    def load(filepath):
        """ Load pickled instance from <path>. """
        with open(filepath, 'rb') as file:
            instance = pickle.load(file)
        return instance

    def branch(self, t=None):
        """ Returns copy of culture at generation <t> including history. """

        culture = self.__class__()

        if t is None:
            culture.history = self.history[:]
            culture.fluorescence = deepcopy(self.fluorescence)

        else:
            culture.history = self.history[:t+1]
            culture.fluorescence = deepcopy(self.fluorescence)

        return culture

    def freeze(self, t):
        """ Returns snapshot of culture at generation <t>. """
        cells = self.history[t]
        culture = self.__class__(scaling=float(len(cells))/self.size)
        culture.history = [cells]
        culture.fluorescence = deepcopy(self.fluorescence)
        return culture

    @staticmethod
    def inoculate(N=2):
        """ Inoculate with <N> generations of heterozygous cells. """
        return Cell().grow(max_generation=N)

    def move(self, center=None, reference_population=1000):
        """
        Update cell positions.

        Args:

            center (np.ndarray[float]) - center position

            reference_population (int) - number of cells in unit circle

        """

        # fix centerpoint
        if center is None:
           center = np.zeros(2, dtype=float)

        # determine scaling (colony radius)
        radius = np.sqrt(self.size/reference_population)

        # run relaxation
        xy_dict = nx.kamada_kawai_layout(
            self.xy_graph,
            pos=dict(enumerate(self.xy)),
            center=center,
            scale=radius)

        # update cell positions
        _ = [cell.set_xy(xy_dict[i]) for i, cell in enumerate(self.cells)]

    def divide(self, division=0.1, recombination=0.1):

        # select cells for division
        divided = np.random.random(len(self.parents)) < division

        # create next generation
        for index, parent in enumerate(self.parents):

            # if cell divided, pass children to next generation
            if divided[index]:
                children = parent.divide(recombination=recombination)
                self.cells.extend(children)

            # otherwise, pass cell to next generation
            else:
                self.cells.append(parent.copy())

    def update(self,
               division=0.1,
               recombination=0.1,
               reference_population=1000,
               **kwargs):
        self.history.append([])
        self.divide(division, recombination)
        self.move(reference_population=reference_population, **kwargs)

    def grow(self, min_population=10, max_iters=None, **kwargs):
        i = 0
        while self.size < min_population:
            self.update(**kwargs)
            if max_iters is not None:
                i += 1
                if i >= max_iters:
                    break
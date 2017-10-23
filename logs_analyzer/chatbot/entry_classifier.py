from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans
import numpy as np


class EntryClassifier:
    def __init__(self, num_classes):
        self.pca_components = 20  # explains most of variance
        self.num_classes = num_classes
        self.clustering = None
        self.pca = None

    def fit(self, data):
        self.estimate_centroids(self.estimate_pca(data))

    def estimate_pca(self, data):
        self.pca = PCA(n_components=self.pca_components, whiten=True)
        return self.pca.fit_transform(data)

    def estimate_centroids(self, data):
        self.clustering = MiniBatchKMeans(n_clusters=self.num_classes)
        self.clustering.fit(data)

    def transform(self, data):
        data = self.pca.transform(data)
        dists = self.clustering.transform(data)
        return np.argmin(dists, axis=1)

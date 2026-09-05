"""
RFM (Recency, Frequency, Monetary) segmentation via K-Means.

Clusters are unlabeled by K-Means itself — `label_clusters` maps each
cluster to a human-readable segment name by ranking cluster centroids on a
combined RFM score, so "the cluster with the best combined score" becomes
"VIP" etc., rather than an arbitrary cluster index.
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

N_CLUSTERS = 4
SEGMENT_LABELS_BEST_TO_WORST = ["VIP", "Loyal", "New", "At Risk"]


def compute_segments(rfm_matrix: np.ndarray) -> list[str]:
    """
    rfm_matrix columns: [recency_days, frequency, monetary]. Lower recency
    and higher frequency/monetary are "better" — combined into one ranking
    score per cluster centroid to assign labels.
    """
    n_samples = len(rfm_matrix)
    if n_samples < N_CLUSTERS:
        # Too few customers to cluster meaningfully — everyone gets the
        # same neutral label rather than a misleading cluster assignment.
        return ["New"] * n_samples

    scaler = StandardScaler()
    scaled = scaler.fit_transform(rfm_matrix)

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    cluster_ids = kmeans.fit_predict(scaled)

    # Combined score per centroid: -recency (lower is better) + frequency + monetary,
    # all on the standardized scale so no single dimension dominates.
    centroids = kmeans.cluster_centers_
    centroid_scores = -centroids[:, 0] + centroids[:, 1] + centroids[:, 2]
    ranked_cluster_ids = np.argsort(-centroid_scores)  # best score first

    cluster_to_label = {
        cluster_id: SEGMENT_LABELS_BEST_TO_WORST[rank]
        for rank, cluster_id in enumerate(ranked_cluster_ids)
    }

    return [cluster_to_label[cid] for cid in cluster_ids]

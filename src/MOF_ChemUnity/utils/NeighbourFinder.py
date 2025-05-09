import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import matplotlib.pyplot as plt

class NeighbourSearchAgent:
    def __init__(self, desc_df: pd.DataFrame):
        """
        desc_df: DataFrame in long format with columns ['m.refcode', 'descriptor_name', 'descriptor_value']
        """
        self.raw_df = desc_df.copy()
        self._pivot_and_validate()
        self.embedded_df = None

    def _pivot_and_validate(self):
        """Pivot the long-format dataframe (if needed) and fill missing values."""

        cols = set(self.raw_df.columns)
        long_cols = {'m.refcode', 'descriptor_name', 'descriptor_value'}

        if long_cols.issubset(cols):
            print("📐 Detected long-format descriptor data. Pivoting to wide format...")
            df_wide = self.raw_df.pivot(index='m.refcode', columns='descriptor_name', values='descriptor_value')
        elif 'm.refcode' in cols and len(cols) > 10:
            print("📊 Detected wide-format descriptor data. Skipping pivot...")
            df_wide = self.raw_df.set_index('m.refcode') if 'm.refcode' in self.raw_df.columns else self.raw_df
        else:
            raise ValueError("❌ Unrecognized descriptor dataframe format.")

        df_wide = df_wide.apply(pd.to_numeric, errors='coerce')
        df_wide = df_wide.fillna(df_wide.median(numeric_only=True))
        self.desc_wide = df_wide

    def embed_descriptors(self, method: str = 'all'):
        """Compute 2D embeddings using UMAP, PCA, t-SNE, or all."""
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(self.desc_wide)

        if self.embedded_df is None:
            self.embedded_df = self.desc_wide.copy()

        if method in ['umap', 'all']:
            reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, random_state=42)
            umap_embedding = reducer.fit_transform(X_scaled)
            self.embedded_df['UMAP-1'] = umap_embedding[:, 0]
            self.embedded_df['UMAP-2'] = umap_embedding[:, 1]

        if method in ['pca', 'all']:
            pca = PCA(n_components=2)
            pca_embedding = pca.fit_transform(X_scaled)
            self.embedded_df['PCA-1'] = pca_embedding[:, 0]
            self.embedded_df['PCA-2'] = pca_embedding[:, 1]

        if method in ['tsne', 'all']:
            tsne = TSNE(n_components=2, random_state=42)
            tsne_embedding = tsne.fit_transform(X_scaled)
            self.embedded_df['TSNE-1'] = tsne_embedding[:, 0]
            self.embedded_df['TSNE-2'] = tsne_embedding[:, 1]

    def find_neighbours(
            self,
            target_refcode: str,
            k: int = 5,
            method: str = 'umap',
            include_descriptors: bool = False,
            subset: list = None,
            label_df: pd.DataFrame = None,
            label_column: str = 'Water Stability'
        ) -> pd.DataFrame:
        """Return k nearest neighbors with optional label data for few-shot prompts."""

        if self.embedded_df is None:
            raise ValueError("Call embed_descriptors() before finding neighbors.")

        if target_refcode not in self.embedded_df.index:
            raise ValueError(f"MOF refcode '{target_refcode}' not found.")

        coord_cols = {
            'umap': ['UMAP-1', 'UMAP-2'],
            'pca': ['PCA-1', 'PCA-2'],
            'tsne': ['TSNE-1', 'TSNE-2'],
        }

        if method not in coord_cols:
            raise ValueError(f"Unsupported method '{method}'. Use 'umap', 'pca', or 'tsne'.")
        if not all(col in self.embedded_df.columns for col in coord_cols[method]):
            raise ValueError(f"Embedding '{method}' not found. Call embed_descriptors(method='{method}') first.")

        X = self.embedded_df[coord_cols[method]]

        # Subset candidate pool
        if subset is not None:
            candidate_df = self.embedded_df.loc[self.embedded_df.index.isin(subset)].copy()
            if target_refcode in candidate_df.index:
                candidate_df = candidate_df.drop(index=target_refcode)
        else:
            candidate_df = self.embedded_df.drop(index=target_refcode)

        if candidate_df.empty:
            raise ValueError("No candidates found for nearest neighbor search.")

        nn_model = NearestNeighbors(n_neighbors=min(k, len(candidate_df)), metric='euclidean')
        nn_model.fit(candidate_df[coord_cols[method]])

        query_vec = X.loc[[target_refcode]]
        distances, indices = nn_model.kneighbors(query_vec)

        neighbors = candidate_df.iloc[indices[0]].copy()
        neighbors.reset_index(inplace=True)

        distance_col_name = f'Chemical Embedding Distance to \"{target_refcode}\"'
        neighbors[distance_col_name] = distances[0]

        # Select output
        if not include_descriptors:
            neighbors = neighbors[['m.refcode', distance_col_name]]

        # Optionally join label
        if label_df is not None and {'m.refcode', label_column}.issubset(label_df.columns):
            neighbors = neighbors.merge(
                label_df[['m.refcode', label_column]],
                on='m.refcode',
                how='left'
            )

        return neighbors



    
    def plot_embedding(self, methods=['umap'], color=None, figsize=(5, 5)):
        """
        Plot embedding spaces. 
        
        Args:
            methods (list or str): 'umap', 'pca', 'tsne', or 'all'.
            color (str or None): Optional column in embedded_df to color by.
            figsize (tuple): Size of each subplot.
        """
        if isinstance(methods, str):
            methods = [methods]

        if 'all' in methods:
            methods = ['umap', 'pca', 'tsne']

        available_cols = self.embedded_df.columns if self.embedded_df is not None else []
        method_coords = {
            'umap': ('UMAP-1', 'UMAP-2'),
            'pca': ('PCA-1', 'PCA-2'),
            'tsne': ('TSNE-1', 'TSNE-2'),
        }

        num_plots = len(methods)
        fig, axes = plt.subplots(1, num_plots, figsize=(figsize[0] * num_plots, figsize[1]))

        if num_plots == 1:
            axes = [axes]

        for ax, method in zip(axes, methods):
            x_col, y_col = method_coords[method]

            if x_col not in available_cols or y_col not in available_cols:
                print(f"⚠️ Embedding for '{method}' not found. Skipping plot.")
                continue

            plot_df = self.embedded_df.copy()
            scatter = ax.scatter(
                plot_df[x_col],
                plot_df[y_col],
                c=plot_df[color] if color and color in plot_df.columns else 'cyan',
                alpha=0.7,
                edgecolors='k',
                s=30
            )
            ax.set_title(f"{method.upper()} Embedding")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)

            if color and color in plot_df.columns:
                fig.colorbar(scatter, ax=ax, label=color)

        plt.tight_layout()
        plt.show()

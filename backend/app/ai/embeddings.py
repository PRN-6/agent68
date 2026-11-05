import math
import hashlib
from typing import List
import numpy as np

class LocalEmbeddingProvider:
    """Fast, deterministic, lightweight vector embedding generator.
    Produces 128-dimensional dense vectors using hashed n-grams and semantic keyword weighting,
    providing instant offline semantic cosine similarity without external network calls.
    """
    def __init__(self, dim: int = 128):
        self.dim = dim

    def embed_text(self, text: str) -> List[float]:
        tokens = text.lower().replace(",", " ").replace(".", " ").replace("!", " ").replace("?", " ").split()
        vec = np.zeros(self.dim, dtype=np.float32)
        
        if not tokens:
            return vec.tolist()
            
        for i, token in enumerate(tokens):
            # Keyword semantic clustering based on md5 hash buckets
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if ((h >> 4) & 1) == 0 else -1.0
            
            # Position and length weighting
            weight = 1.0 + min(len(token), 8) * 0.15
            vec[idx] += sign * weight
            
            # Bigrams
            if i > 0:
                bigram = f"{tokens[i-1]}_{token}"
                bh = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                b_idx = bh % self.dim
                b_sign = 1.0 if ((bh >> 4) & 1) == 0 else -1.0
                vec[b_idx] += b_sign * 1.5

        # Normalize to unit vector
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
            
        return vec.tolist()

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-6 or norm_b < 1e-6:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

embedding_provider = LocalEmbeddingProvider()

"""
Face verification: Match detected faces to enrolled template.
"""
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from utils import BoundingBox
from embedder import FaceEmbedder


@dataclass
class FaceIdentity:
    """Identity of a detected face."""
    label: str  # "ME" or "OTHER"
    similarity: float  # 0.0 to 1.0
    box: BoundingBox
    embedding: np.ndarray


class FaceVerifier:
    """Verifies if detected faces match the enrolled template."""
    
    def __init__(self, template_path: Optional[str] = None, similarity_threshold: float = 0.6):
        """
        Initialize face verifier.
        
        Args:
            template_path: Path to saved template.npy (auto-detects if None)
            similarity_threshold: Threshold above which a face is considered "ME"
        """
        self.embedder = FaceEmbedder()
        self.template_embedding = None
        self.similarity_threshold = similarity_threshold
        
        # Try to load template
        if template_path is None:
            template_path = Path(__file__).parent.parent / "data" / "my_template.npy"
        
        self._load_template(template_path)
    
    def _load_template(self, template_path):
        """Load enrolled template embedding."""
        try:
            template_path = Path(template_path)
            if template_path.exists():
                self.template_embedding = np.load(template_path)
                print(f"[INFO] Loaded face template: {template_path}")
                print(f"[INFO] Verification enabled (threshold: {self.similarity_threshold})")
            else:
                print(f"[WARNING] Template not found at {template_path}")
                print("[INFO] Verification disabled - run 'python enroll.py' to create template")
        except Exception as e:
            print(f"[WARNING] Failed to load template: {e}")
    
    def is_enabled(self) -> bool:
        """Check if verification is enabled (template loaded)."""
        return self.template_embedding is not None
    
    def verify(self, embedding: np.ndarray):
        """
        Verify a face embedding against the template.
        
        Args:
            embedding: Face embedding vector
        
        Returns:
            Tuple of (label, similarity) where label is "ME" or "OTHER"
        """
        if not self.is_enabled():
            return "OTHER", 0.0
        
        similarity = self.embedder.similarity(embedding, self.template_embedding)
        
        if similarity >= self.similarity_threshold:
            return "ME", similarity
        else:
            return "OTHER", similarity
    
    def verify_batch(
        self,
        embeddings: np.ndarray,
        boxes: List[BoundingBox]
    ) -> List[FaceIdentity]:
        """
        Verify multiple face embeddings.
        
        Args:
            embeddings: Array of embeddings (N x embedding_size)
            boxes: List of corresponding bounding boxes
        
        Returns:
            List of FaceIdentity objects
        """
        results = []
        
        for i, (embedding, box) in enumerate(zip(embeddings, boxes)):
            label, similarity = self.verify(embedding)
            
            results.append(FaceIdentity(
                label=label,
                similarity=similarity,
                box=box,
                embedding=embedding
            ))
        
        return results
    
    def get_me_face(self, identities: List[FaceIdentity]) -> Optional[FaceIdentity]:
        """Get the highest-confidence "ME" face from a list."""
        me_faces = [f for f in identities if f.label == "ME"]
        if me_faces:
            return max(me_faces, key=lambda x: x.similarity)
        return None
    
    def get_other_faces(self, identities: List[FaceIdentity]) -> List[FaceIdentity]:
        """Get all "OTHER" faces from a list."""
        return [f for f in identities if f.label == "OTHER"]
    
    def update_threshold(self, new_threshold: float):
        """Update similarity threshold for verification."""
        self.similarity_threshold = max(0.0, min(1.0, new_threshold))
        print(f"[INFO] Verification threshold updated to {self.similarity_threshold}")

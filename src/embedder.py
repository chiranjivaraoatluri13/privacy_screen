"""
Face embedding computation using lightweight features.
For a production system, replace with ONNX Runtime + pre-trained model.
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import os


class FaceEmbedder:
    """
    Computes face embeddings using OpenCV's DNN with a pre-trained model.
    Falls back to simple feature-based embeddings if model unavailable.
    """
    
    def __init__(self):
        """Initialize face embedder."""
        self.use_dnn = False
        self.net = None
        self.embedding_size = 128
        
        # Try to load a pre-trained embedding model
        self._try_load_dnn_model()
    
    def _try_load_dnn_model(self):
        """Try to load OpenCV DNN embedding model."""
        try:
            # Try loading from local files first
            model_files = [
                ("openface.prototxt", "openface_nn4.small2.v1.t7"),
            ]
            
            for proto, model in model_files:
                if os.path.exists(proto) and os.path.exists(model):
                    try:
                        self.net = cv2.dnn.readNetFromTorch(model)
                        self.use_dnn = True
                        print(f"[INFO] Loaded OpenFace embedding model: {model}")
                        return
                    except:
                        pass
            
            print("[INFO] DNN embedding model not available, using feature-based embeddings")
        except Exception as e:
            print(f"[WARNING] Could not load DNN model: {e}")
    
    def compute_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Compute embedding vector for a face crop.
        
        Args:
            face_crop: Face image (BGR, typically 100x100 or similar)
        
        Returns:
            Embedding vector (float array)
        """
        if face_crop is None or face_crop.size == 0:
            return np.zeros(self.embedding_size, dtype=np.float32)
        
        if self.use_dnn and self.net is not None:
            return self._compute_dnn_embedding(face_crop)
        else:
            return self._compute_feature_embedding(face_crop)
    
    def _compute_dnn_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """Compute embedding using DNN model."""
        try:
            h, w = face_crop.shape[:2]
            
            # Prepare blob (normalize and resize)
            blob = cv2.dnn.blobFromImage(
                face_crop,
                1.0 / 255.0,
                (96, 96),
                mean=[104.0, 177.0, 123.0],
                swapRB=False,
                crop=False
            )
            
            # Forward pass
            self.net.setInput(blob)
            embedding = self.net.forward()
            
            # Flatten and normalize
            embedding = embedding.flatten()
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"[WARNING] DNN embedding failed: {e}, using feature embedding")
            self.use_dnn = False
            return self._compute_feature_embedding(face_crop)
    
    def _compute_feature_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Compute embedding using handcrafted features.
        Uses histogram of oriented gradients (HOG) + color histograms.
        """
        try:
            # Resize to consistent size
            face_resized = cv2.resize(face_crop, (100, 100))
            
            # Convert to grayscale
            gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Compute HOG features
            hog = cv2.HOGDescriptor(
                (_64, 128),  # winSize
                (8, 8),      # blockSize
                (4, 4),      # blockStride
                (8, 8),      # cellSize
                9            # nBins
            )
            hog_features = hog.compute(gray).flatten()
            
            # Compute color histogram
            hsv = cv2.cvtColor(face_resized, cv2.COLOR_BGR2HSV)
            hist_h = cv2.calcHist([hsv], [0], None, [16], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [8], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [8], [0, 256])
            
            color_features = np.concatenate([
                hist_h.flatten(),
                hist_s.flatten(),
                hist_v.flatten()
            ])
            
            # Combine features
            embedding = np.concatenate([
                hog_features[:80],  # Use first 80 HOG features (truncate for size)
                color_features[:48]  # Use first 48 color features
            ])
            
            # Normalize to 128-dim vector
            embedding = embedding[:self.embedding_size]
            if len(embedding) < self.embedding_size:
                embedding = np.pad(
                    embedding,
                    (0, self.embedding_size - len(embedding)),
                    mode='constant'
                )
            
            # L2 normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"[WARNING] Feature embedding computation failed: {e}")
            return np.random.randn(self.embedding_size).astype(np.float32)
    
    def compute_batch_embeddings(self, face_crops: list) -> np.ndarray:
        """
        Compute embeddings for multiple face crops.
        
        Args:
            face_crops: List of face images
        
        Returns:
            Array of embeddings (N x embedding_size)
        """
        embeddings = []
        for crop in face_crops:
            embeddings.append(self.compute_embedding(crop))
        return np.array(embeddings, dtype=np.float32)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1, embedding2: Embedding vectors
        
        Returns:
            Similarity score in [0, 1]
        """
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        
        # L2 normalize
        e1 = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        e2 = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        
        # Cosine similarity
        similarity_score = float(np.dot(e1, e2))
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, (similarity_score + 1.0) / 2.0))

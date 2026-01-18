"""
Anomaly Detection for Sensor Data
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Anomaly detector using Isolation Forest algorithm with model caching.
    """
    
    # In-memory cache for trained models
    _model_cache = {}
    
    def __init__(self, contamination=0.1, random_state=42):
        """
        Initialize the AnomalyDetector.
        
        Args:
            contamination: Expected proportion of anomalies in dataset (0 to 0.5)
            random_state: Random state for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.feature_name = None
    
    def fit(self, data, feature):
        """
        Train the Isolation Forest model on the provided data.
        
        Args:
            data: 2D array-like of shape (n_samples, n_features) or 1D array
            feature: Sensor type/name for caching purposes
        
        Returns:
            self: Returns the instance for method chaining
        """
        self.feature_name = feature
        
        # Convert to numpy array and reshape if necessary
        data = np.array(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        # Create and train the model
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state
        )
        self.model.fit(data)
        
        # Cache the trained model
        self._model_cache[feature] = self.model
        
        return self
    
    def predict(self, data):
        """
        Predict anomalies in the data.
        
        Args:
            data: 2D array-like of shape (n_samples, n_features) or 1D array
        
        Returns:
            Array of predictions: -1 for anomalies, 1 for normal
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        data = np.array(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        return self.model.predict(data)
    
    def predict_proba(self, data):
        """
        Get anomaly scores for the data (lower = more anomalous).
        
        Args:
            data: 2D array-like of shape (n_samples, n_features) or 1D array
        
        Returns:
            Array of anomaly scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        data = np.array(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        return self.model.score_samples(data)
    
    @classmethod
    def get_cached_model(cls, feature):
        """
        Retrieve a cached model for a specific feature.
        
        Args:
            feature: Sensor type/name
        
        Returns:
            IsolationForest model or None if not cached
        """
        return cls._model_cache.get(feature)
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached models."""
        cls._model_cache.clear()


def detect_anomaly(data, feature):
    """
    Check if sensor data contains anomalies using cached models.
    
    Args:
        data: List of sensor readings
        feature: Sensor type (temperature, humidity, etc.)
    
    Returns:
        Boolean: True if anomaly detected
    """
    # Try to get cached model
    model = AnomalyDetector.get_cached_model(feature)
    
    if model is None:
        # If no cached model, train a new one
        detector = AnomalyDetector()
        detector.fit(data, feature)
        model = detector.model
    
    # Make prediction on latest data point
    data_array = np.array(data).reshape(-1, 1)
    predictions = model.predict(data_array)
    
    # Return True if last prediction is anomaly (-1)
    return predictions[-1] == -1
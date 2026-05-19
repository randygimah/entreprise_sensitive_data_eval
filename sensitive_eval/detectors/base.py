"""
Abstract interface for detection.
Defines a contract that every detector must follow.
Every detector answer the same question: Given a DatasetSample, return a DetectorResult.
Every subclass must consume the base class method to prevent raising an error when instantiated
This keeps regex, NER, LLM, and hybrid detectors interchangeable.
"""

from abc import ABC, abstractmethod

from sensitive_eval.core.models import DatasetSample, DetectorResult


class BaseDetector(ABC):
    """Abstract base class for sensitive-content detectors."""

    name: str

    @abstractmethod
    def detect(self, sample: DatasetSample) -> DetectorResult:
        """Detect sensitive spans in dataset sample"""
        raise NotImplementedError

# 🎯 VARIANT SCORERS - TINY FOCUSED MODULES
# Each scorer handles one mechanism - no giant overwhelming files!

from .base_scorer import BaseScorer
from .collagen_scorer import CollagenScorer
from .general_scorer import GeneralScorer

__all__ = [
    'BaseScorer',
    'CollagenScorer', 
    'GeneralScorer'
]

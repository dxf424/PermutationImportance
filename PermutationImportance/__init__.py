"""These are methods for computing variable importance through various different
methods. In addition, we provide some helpful metrics and other tools for 
implementing your own methods

@author G. Eli Jergensen <gelijergensen@ou.edu>"""

from .abstract_runner import abstract_variable_importance
from . import metrics
from .permutation_importance import *
from .sequential_selection import *
from .result import ImportanceResult
from . import sklearn_api

__version__ = '1.2.0.5'
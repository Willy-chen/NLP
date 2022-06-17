from . import predict
from . import upload
from . import STT

from .predict import *
from .upload import *
from .STT import *

__all__ = [*predict.__all__,
           *upload.__all__, 
           ]
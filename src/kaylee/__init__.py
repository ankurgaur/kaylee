# -*- coding: utf-8 --*
"""
    kaylee
    ~~~~~~

    Kaylee is distributed computing framework.

    It implements all the functionality required to distribute computation
    among nodes and collect the results. Kaylee aims to let a user
    completely focus on project's business logic and handle all other
    stuff automatically.

    :copyright: (c) 2012 by Zaur Nasibov.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '0.1'

from .loader import load, LazySettings, LazyKaylee

settings = LazySettings()
kl = LazyKaylee()

from .app import Kaylee, Applications
from .node import Node, NodeID, NodesRegistry
from .storage import (ControllerResultsStorage,
                      ProjectResultsStorage )
from .controller import Controller
from .project import Project, Task
from .errors import KayleeError

def setup():
    settings._setup()
    kl._setup()

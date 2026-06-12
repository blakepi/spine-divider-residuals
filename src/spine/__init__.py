"""SPINE dendritic-spine modeling platform scaffold.

Phase 00 intentionally exposes configuration and unit helpers only. The
simulation engine is specified but not implemented until Phase 01.
"""

from spine.config import load_config

__all__ = ["load_config"]
__version__ = "0.0.0"

"""The delves, one module each. A design module defines KEY, NAME, STRUCTURE, POOLS, FEATURES and pieces();
see DESIGN.md ("Design module contract")."""
import importlib
import os

KEYS = ['camp', 'seam', 'post', 'cistern', 'hermit', 'grotto', 'ossuary', 'forge']


def modules(only=None):
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for key in KEYS:
        if only and key not in only: continue
        if os.path.exists(os.path.join(here, key + '.py')):
            out.append(importlib.import_module(f'designs.{key}'))
    return out

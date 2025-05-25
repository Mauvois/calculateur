# views/__init__.py
"""Module contenant les vues de l'application"""

from .previsions import render_previsions_tab
from .resultats import render_resultats_tab
from .export import render_export_tab

__all__ = ['render_previsions_tab', 'render_resultats_tab', 'render_export_tab']

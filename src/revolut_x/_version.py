"""Single source of truth for the package version.

Both ``revolut_x.__version__`` and the default ``User-Agent`` in
:mod:`revolut_x._http` read from here, and ``pyproject.toml`` resolves its
``version`` field to this attribute.  Bump it in this one place only — the
three used to be maintained by hand and had drifted apart (0.0.6 / 0.0.8 /
0.1.0 simultaneously).
"""

__version__ = "0.1.0"

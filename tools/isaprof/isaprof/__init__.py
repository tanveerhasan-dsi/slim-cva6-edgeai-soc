"""isaprof — RISC-V instruction-coverage measurement for the CARVE-V project.

Two passes, answering two different questions:

* ``static``  — which instructions can *possibly* execute, from a linear sweep
  of every allocated executable region of an ELF.
* ``dynamic`` — which instructions *did* execute, and how often, from a
  simulator trace.

Keeping them distinct is the whole point of the instrument. See
``docs/04-methodology-requirements.md`` for why the project treats them as
answering non-interchangeable questions.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]

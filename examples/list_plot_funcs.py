#!/usr/bin/env python3
"""List available plot functions in PyOpenMagnetics."""
import PyOpenMagnetics

funcs = [f for f in dir(PyOpenMagnetics) if 'plot' in f.lower()]
print("Available plotting functions:")
for f in funcs:
    print(f"  - {f}")
    # Try to get signature
    try:
        func = getattr(PyOpenMagnetics, f)
        print(f"      {func.__doc__[:100] if func.__doc__ else 'No docstring'}...")
    except:
        pass

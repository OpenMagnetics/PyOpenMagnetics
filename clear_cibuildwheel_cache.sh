#!/bin/bash
# Clear all caches for cibuildwheel

# Clear cibuildwheel cache
rm -rf ~/.cache/cibuildwheel

# Clear Docker build cache (optional, be careful)
# docker system prune -f

# Clear local build directories
rm -rf build
rm -rf wheelhouse/*.whl

echo "Cache cleared. Now run: cibuildwheel . --only cp310-manylinux_x86_64"

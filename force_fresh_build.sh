#!/bin/bash
# Force fresh PyMKF build with no caching

echo "Cleaning all caches..."

# Clean PyMKF build directories
rm -rf /home/alf/OpenMagnetics/PyMKF/build
rm -rf /home/alf/OpenMagnetics/PyMKF/wheelhouse/*.whl

# Clean cibuildwheel cache
rm -rf ~/.cache/cibuildwheel

# Clean CMake FetchContent cache (global)
rm -rf ~/.cmake/packages/MAS* 2>/dev/null
rm -rf ~/.cmake/packages/MKF* 2>/dev/null

# If using Docker, you might also need:
# docker system prune -f

echo "Cache cleared!"
echo ""
echo "Now run cibuildwheel with:"
echo "  cd /home/alf/OpenMagnetics/PyMKF"
echo "  cibuildwheel . --only cp310-manylinux_x86_64"
echo ""
echo "Or to debug the build, run:"
echo "  cd /home/alf/OpenMagnetics/PyMKF"
echo "  rm -rf build && python -m pip install . --no-deps -v 2>&1 | tail -100"
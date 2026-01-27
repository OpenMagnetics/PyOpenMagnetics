#!/usr/bin/env python3
"""
Check compatibility between POWDER_CORE_MATERIALS in knowledge.py
and the PyOpenMagnetics material database.

This script identifies:
1. Materials in knowledge.py NOT in PyOpenMagnetics (supplementary data)
2. Materials in PyOpenMagnetics that could be added to knowledge.py
3. Overlapping materials with comparison of Steinmetz parameters

Run: python scripts/check_material_database.py
"""

import sys
import json


def main():
    try:
        import PyOpenMagnetics
    except ImportError:
        print("ERROR: PyOpenMagnetics not installed. Install with: pip install .")
        sys.exit(1)

    # Import knowledge base
    try:
        from api.expert.knowledge import POWDER_CORE_MATERIALS
    except ImportError:
        print("ERROR: Cannot import POWDER_CORE_MATERIALS from api.expert.knowledge")
        sys.exit(1)

    print("=" * 70)
    print("MATERIAL DATABASE COMPATIBILITY CHECK")
    print("=" * 70)

    # Get PyOpenMagnetics materials
    pom_material_names = PyOpenMagnetics.get_core_material_names()
    pom_materials_lower = {name.lower(): name for name in pom_material_names}

    print(f"\nPyOpenMagnetics database: {len(pom_material_names)} materials")
    print(f"Knowledge.py database: {len(POWDER_CORE_MATERIALS)} materials")

    # Categorize knowledge.py materials
    in_pom = []  # Materials that exist in PyOpenMagnetics
    not_in_pom = []  # Materials NOT in PyOpenMagnetics (supplementary)

    print("\n" + "-" * 70)
    print("ANALYSIS OF POWDER_CORE_MATERIALS entries:")
    print("-" * 70)

    for key, mat in POWDER_CORE_MATERIALS.items():
        name = mat.get("name", key)
        family = mat.get("family", "Unknown")

        # Try to match with PyOpenMagnetics (case-insensitive)
        name_lower = name.lower()
        matched_pom_name = None

        # Check exact match
        if name_lower in pom_materials_lower:
            matched_pom_name = pom_materials_lower[name_lower]
        else:
            # Check partial matches (e.g., "MPP 60" in "CSC MPP 60u")
            for pom_lower, pom_name in pom_materials_lower.items():
                if any(word in pom_lower for word in name_lower.split()):
                    matched_pom_name = pom_name
                    break

        if matched_pom_name:
            in_pom.append((key, name, family, matched_pom_name))
        else:
            not_in_pom.append((key, name, family))

    # Report materials NOT in PyOpenMagnetics
    print(f"\n[NOT IN PyOpenMagnetics - {len(not_in_pom)} materials]")
    print("These are SUPPLEMENTARY materials (provide unique value):\n")

    families_not_in = {}
    for key, name, family in not_in_pom:
        if family not in families_not_in:
            families_not_in[family] = []
        families_not_in[family].append((key, name))

    for family, materials in sorted(families_not_in.items()):
        print(f"  {family}:")
        for key, name in materials:
            steinmetz = POWDER_CORE_MATERIALS[key].get("steinmetz", {})
            print(f"    - {key}: k={steinmetz.get('k', 'N/A')}, "
                  f"alpha={steinmetz.get('alpha', 'N/A')}, "
                  f"beta={steinmetz.get('beta', 'N/A')}")

    # Report materials that ARE in PyOpenMagnetics (potential duplicates)
    print(f"\n[ALSO IN PyOpenMagnetics - {len(in_pom)} materials]")
    print("These MAY be redundant (check if data differs):\n")

    for key, name, family, pom_name in in_pom:
        # Get PyOpenMagnetics data
        try:
            pom_mat = PyOpenMagnetics.find_core_material_by_name(pom_name)
            # Try to get Steinmetz at 100kHz for comparison
            try:
                pom_steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients(pom_name, 100000.0)
            except:
                pom_steinmetz = {}
        except:
            pom_mat = {}
            pom_steinmetz = {}

        knowledge_steinmetz = POWDER_CORE_MATERIALS[key].get("steinmetz", {})

        print(f"  {key} <-> {pom_name}")
        print(f"    Knowledge.py: k={knowledge_steinmetz.get('k', 'N/A')}, "
              f"alpha={knowledge_steinmetz.get('alpha', 'N/A')}, "
              f"beta={knowledge_steinmetz.get('beta', 'N/A')}")
        print(f"    PyOpenMagnetics: k={pom_steinmetz.get('k', 'N/A')}, "
              f"alpha={pom_steinmetz.get('alpha', 'N/A')}, "
              f"beta={pom_steinmetz.get('beta', 'N/A')}")
        print()

    # Check for powder core materials in PyOpenMagnetics NOT in knowledge.py
    print("\n" + "-" * 70)
    print("PyOpenMagnetics materials potentially missing from knowledge.py:")
    print("-" * 70)

    powder_keywords = ['mpp', 'high flux', 'highflux', 'kool', 'sendust',
                       'xflux', 'mega', 'powder', 'iron', 'alloy']

    pom_powder_materials = []
    for name in pom_material_names:
        name_lower = name.lower()
        if any(kw in name_lower for kw in powder_keywords):
            pom_powder_materials.append(name)

    # Check which aren't in knowledge.py
    knowledge_names_lower = {mat.get("name", "").lower() for mat in POWDER_CORE_MATERIALS.values()}

    missing_from_knowledge = []
    for pom_name in pom_powder_materials:
        if pom_name.lower() not in knowledge_names_lower:
            # Check partial match
            matched = False
            for kn in knowledge_names_lower:
                if pom_name.lower() in kn or kn in pom_name.lower():
                    matched = True
                    break
            if not matched:
                missing_from_knowledge.append(pom_name)

    if missing_from_knowledge:
        print(f"\nPotential powder core materials in PyOpenMagnetics to consider adding:")
        for name in missing_from_knowledge[:20]:  # Limit output
            print(f"  - {name}")
        if len(missing_from_knowledge) > 20:
            print(f"  ... and {len(missing_from_knowledge) - 20} more")
    else:
        print("\nNo obvious powder core materials missing from knowledge.py")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
Total materials in knowledge.py: {len(POWDER_CORE_MATERIALS)}
  - Supplementary (NOT in PyOpenMagnetics): {len(not_in_pom)}
  - Potentially redundant (IN PyOpenMagnetics): {len(in_pom)}

RECOMMENDATION:
- KEEP materials NOT in PyOpenMagnetics (they add value)
- REVIEW overlapping materials - remove if PyOpenMagnetics data is better
- Consider updating permeability_curve data which PyOpenMagnetics may not have
""")


if __name__ == "__main__":
    main()

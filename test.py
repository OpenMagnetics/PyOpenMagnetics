import PyOpenMagnetics


def get_area_product(core):
    return core["processedDescription"]["columns"][0]["area"] * core["processedDescription"]["windingWindows"][0]["area"]


cores = PyOpenMagnetics.get_available_cores()
print(len(cores))

target_area_product_cm4 = 70
tolerance = 0.05
shape_names = []

for core in cores:
    area_product = get_area_product(core)
    area_product_cm4 = area_product * 100000000
    if target_area_product_cm4 * (1 - tolerance) < area_product_cm4 < target_area_product_cm4 * (1 + tolerance):
        # print(core["manufacturerInfo"]["reference"])
        if core["manufacturerInfo"]["reference"] not in shape_names:
            shape_names.append(core["manufacturerInfo"]["reference"])
        # print(core["functionalDescription"]["shape"]["name"])
print(shape_names)

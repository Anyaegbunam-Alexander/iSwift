import re


def object_kebab_case(obj):
    name = obj.__class__.__name__
    name = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()
    name = re.sub(r"i-swift", "iswift", name)
    return name

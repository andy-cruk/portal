
def my_import(name):
    """Dynamically import a module based on its path"""
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
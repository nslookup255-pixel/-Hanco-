import importlib

_REGISTRY = {
    "랜덤": ".random_std",
    "시간": ".time_std",
    "파일": ".file_std",
}


class _LazySTDLIB:
    def __init__(self):
        self._cache = {}

    def __contains__(self, name):
        return name in _REGISTRY

    def __getitem__(self, name):
        if name not in self._cache:
            module = importlib.import_module(_REGISTRY[name], package=__package__)
            self._cache[name] = module.STDLIB[name]
        return self._cache[name]


STDLIB = _LazySTDLIB()

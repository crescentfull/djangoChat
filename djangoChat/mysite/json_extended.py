# 집합 변환 커스텀
# {'a', 'b', 'c'} => {'__set__': True, ('a', 'b', 'c')}

import json

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return {"__set__": True, "values": tuple(obj)}
        return super().default(obj)

class ExtendedDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs.setdefault("object_hook", self._object_hook)
        super().__init__(**kwargs)

    def _object_hook(self, dct):
        if "__set__" in dct:
            return set(dct["values"])
        return dct
import json

# JSON 인코더를 확장하여 사용자 정의 객체를 처리할 수 있도록 함
class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 객체가 set 타입인 경우
        if isinstance(obj, set):
            # set을 JSON으로 변환할 수 있도록 딕셔너리 형식으로 반환
            # "__set__": True는 이 객체가 set임을 나타내고,
            # "values"는 set의 요소들을 튜플로 저장하여 JSON으로 직렬화 가능하게 함
            return {"__set__": True, "values": tuple(obj)}
        # set이 아닌 객체는 기본 JSON 인코딩 방식으로 처리되지 않음
        # JSONEncoder의 기본 동작을 사용하지 않고, 그대로 반환
        return obj

# JSON 디코더를 확장하여 사용자 정의 객체를 처리할 수 있도록 함
class ExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        # object_hook을 _object_hook 메서드로 설정하여
        # JSON 객체를 Python 객체로 변환할 때 호출되도록 함
        kwargs.setdefault("object_hook", self._object_hook)
        super().__init__(**kwargs)

    @staticmethod
    def _object_hook(dct):
        # JSON 객체에 '__set__' 키가 있는 경우
        if '__set__' in dct:
            # "values" 키의 튜플을 set으로 변환하여 반환
            return set(dct['values'])
        # 그렇지 않으면 원래의 딕셔너리 반환
        return dct
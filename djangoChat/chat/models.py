from django.db import models

class Room(models.Model):
    # 한글 채팅방 이름 필드로서 사용하려함
    # name 필드에서는 유일성 체크를 하지 않으므로
    # 같은 이름의 채팅방도 만들 수 있다.
    name = models.CharField(max_length=100)
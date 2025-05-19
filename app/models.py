from django.db import models

class StatusEnum(models.IntegerChoices):
    ACTIVE = 0, 'Active'
    DELETED = 1, 'Deleted'
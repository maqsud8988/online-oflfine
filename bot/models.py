from django.db import models


class TgUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=128)
    status = models.CharField(max_length=50, default='waiting')
    last_message = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Admin(models.Model):
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('busy', 'Boshqasi bilan gaplashvoti'),
    ]
    user_id = models.BigIntegerField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    current_user = models.ForeignKey('TgUser', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="assigned_admin")
    def __str__(self):
        return f"Admin {self.user_id}"

    # def __str__(self):
    #     return str(self.user_id) + ";Busy: " + str(self.is_busy)
    #

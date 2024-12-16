from django.contrib.auth.models import User
from django.db import models


class Friendship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_of")

    class Meta:
        unique_together = ("user", "friend")  # Prevent duplicate friendships

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"

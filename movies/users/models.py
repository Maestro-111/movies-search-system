from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

class Friendship(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_of")

    class Meta:
        unique_together = ("user", "friend")  # Prevent duplicate friendships

    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def get_absolute_url(self):
        print("YES!")
        return reverse("users:show_user", kwargs={"username": self.user.username})

    def __str__(self):
        return self.user.username
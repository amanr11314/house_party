from api.models import Room
from django.db import models

class SpotifyToken(models.Model):
    user = models.CharField(max_length=50,unique=True)
    created=  models.DateTimeField(auto_now_add=True)
    refresh_token=  models.CharField(max_length=200)
    access_token=  models.CharField(max_length=250)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)

class Vote(models.Model):
    user = models.CharField(max_length=50,unique=True)
    created=  models.DateTimeField(auto_now_add=True)
    song_id = models.CharField(max_length=50)
    # delete vote if room gets deleted 
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
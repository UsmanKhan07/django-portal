from asyncio.windows_events import NULL
from multiprocessing.connection import answer_challenge
from django.db import models

# makemigrations - create changes and store in a file 
# migrate - apply the pending changes created by makemigrations

# Create your models here.
class Contact(models.Model):
    #name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    #phone = models.CharField(max_length=12)
    answer = models.TextField()
    #date = models.DateField()

    def __str__(self):
        if self.email==NULL:
            self.email="email not provided by this person"
            return self.email
        elif self.email=="":
            self.email="email not provided by this person"
            return self.email
        else:
            return self.email
    
from multiprocessing.connection import answer_challenge
from django.db import models

# makemigrations - create changes and store in a file 
# migrate - apply the pending changes created by makemigrations

# Create your models here.
class Contact(models.Model):
    #name = models.CharField(max_length=122)

    t_id = models.TextField()
    q_id = models.IntegerField()
    obtained_marks = models.FloatField()
    total_marks = models.FloatField()
    email = models.CharField(max_length=122)
    solution = models.TextField()
    def __str__(self):
        return self.email+"_"+str(self.t_id)+"_"+str(self.q_id)

class Questions(models.Model):
    t_id = models.TextField()
    q_id = models.IntegerField()
    statement = models.TextField()
    groundtruths = models.TextField()
    score = models.FloatField()
    def __str__(self):
        return str(self.t_id)+"_"+str(self.q_id)
    

class Test(models.Model):
    t_id = models.TextField()
    is_open = models.BooleanField()
    def __str__(self):
        return str(self.t_id)
    
    
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Sentencepair(models.Model):
	sentID = models.CharField(max_length=50)
	sent1 = models.TextField()
	sent2 = models.TextField()
	lang = models.CharField(max_length=50, default="en")

	def __str__(self):
		return self.sentID

class Annotation(models.Model):
	sentencepair = models.ForeignKey(Sentencepair, on_delete=models.CASCADE)
	category = models.IntegerField()
	name = models.CharField(max_length=50)
	date = models.DateTimeField(auto_now_add=True)

class Annotator(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	sentencepair = models.ForeignKey(Sentencepair, null=True, blank=True, on_delete=models.CASCADE)
	lastedit = models.IntegerField(default=0)
	lang = models.CharField(max_length=50, default="en")

class Application(models.Model):
	name = models.CharField(max_length=200)
	email = models.EmailField(max_length=200)



from django.db import models

class StudentInfo(models.Model):
    name = models.CharField(max_length=100, blank=True, default="")
    address = models.CharField(max_length=250, blank=True, default="")
    email = models.EmailField(max_length=100, blank=True, default="")
    gender = models.CharField(
        max_length=10,
        default="",
        choices=[
            ('Male', 'male'),
            ('Female', 'female')
        ]
    )
    age = models.IntegerField(default=0, blank=True)
    interest = models.CharField(max_length=200, blank=True, default="")
    course = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.name
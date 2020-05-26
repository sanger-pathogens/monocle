from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=256, primary_key=True)
    country = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()


class User(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    affiliations = models.ManyToManyField(
        Institution, through="Affiliation", related_name="affiliated_members"
    )

    # customise django user model
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


class Affiliation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class Sample(models.Model):
    lane_id = models.CharField(max_length=256, primary_key=True)
    sample_id = models.CharField(max_length=256, unique=True)
    public_name = models.CharField(max_length=256, unique=True)
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

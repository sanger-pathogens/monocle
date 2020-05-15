from django.db import models


class Institution(models.Model):
    name = models.CharField(256, primary_key=True)
    country = models.CharField(256)


class User(models.Model):
    email = models.EmailField(primary_key=True)
    first_name = models.CharField(256)
    last_name = models.CharField(256)
    affiliations = models.ManyToManyField(
        Institution, related_name="affiliated_members"
    )


class Sample(models.Model):
    lane_id = models.CharField(256, primary_key=True)
    sample_id = models.CharField(256, unique=True)
    public_name = models.CharField(256, unique=True)
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

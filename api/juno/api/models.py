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
    class Serotype(models.TextChoices):
        IA = "Ia"
        IB = "Ib"
        II = "II"
        III = "III"
        IV = "IV"
        V = "V"
        VI = "VI"
        VII = "VII"
        VIII = "VIII"
        IX = "IX"
        NT = "NT"
        UNKNOWN = "unknown"

    class HostStatus(models.TextChoices):
        CARRIAGE = "carriage"
        SEPSIS = "sepsis"
        BACTERAEMIA = "bacteraemia"
        MENINGITIS = "meningitis"
        PNEUMONIA = "pneumonia"
        URINARY_TRACT_INFECTION = "urinary tract infection"
        SKIN_AND_SOFT_TISSUE_INFECTION = "skin and soft-tissue infection"
        OSTEOMYELITIS = "osteomyelitis"
        ENDOCARDITIS = "endocarditis"
        SEPTIC_ARTHRITIS = "septic arthritis"
        CHORIOAMNIONITIS = "chorioamnionitis"
        PERITONITIS = "peritonitis"
        EMPYEMA = "empyema"
        SURGICAL_SITE_INFECTION = "surgical site infection"
        UROSEPSIS = "urosepsis"
        ENDOMETRITIS = "endometritis"
        MASTITIS = "mastitis"
        DISEASE_OTHER = "disease other"

    lane_id = models.CharField(max_length=256, primary_key=True)
    sample_id = models.CharField(max_length=256, unique=True)
    public_name = models.CharField(max_length=256, unique=True)
    host_status = models.CharField(max_length=256, choices=HostStatus.choices)
    serotype = models.CharField(max_length=7, choices=Serotype.choices)
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

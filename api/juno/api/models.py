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
    sample_id = models.CharField(max_length=256, primary_key=True)
    lane_id = models.CharField(max_length=256, default='', null=True)
    supplier_sample_name = models.CharField(max_length=256, default='')
    public_name = models.CharField(max_length=256, default='')
    host_status = models.CharField(max_length=256, default='')
    study_name = models.CharField(max_length=600, default='')
    study_ref = models.CharField(max_length=400, default='')
    selection_random = models.CharField(max_length=10, default='')
    country = models.CharField(max_length=90, default='')
    county_state = models.CharField(max_length=200, default='')
    city = models.CharField(max_length=200, default='')
    collection_year = models.CharField(max_length=10, default='')
    collection_month = models.CharField(max_length=10, default='')
    collection_day = models.CharField(max_length=10, default='')
    host_species = models.CharField(max_length=100, default='')
    gender = models.CharField(max_length=10, default='')
    age_group = models.CharField(max_length=30, default='')
    age_years = models.CharField(max_length=10, default='')
    age_months = models.CharField(max_length=10, default='')
    age_weeks = models.CharField(max_length=10, default='')
    age_days = models.CharField(max_length=10, default='')
    disease_type = models.CharField(max_length=100, default='')
    disease_onset = models.CharField(max_length=10, default='')
    isolation_source = models.CharField(max_length=100, default='')
    serotype = models.CharField(max_length=7, default='')
    serotype_method = models.CharField(max_length=100, default='')
    infection_during_pregnancy = models.CharField(max_length=10, default='')
    maternal_infection_type = models.CharField(max_length=100, default='')
    gestational_age_weeks = models.CharField(max_length=10, default='')
    birthweight_gram = models.CharField(max_length=10, default='')
    apgar_score = models.CharField(max_length=10, default='')
    ceftizoxime = models.CharField(max_length=30, default='')
    ceftizoxime_method = models.CharField(max_length=60, default='')
    cefoxitin = models.CharField(max_length=30, default='')
    cefoxitin_method = models.CharField(max_length=60, default='')
    cefotaxime = models.CharField(max_length=30, default='')
    cefotaxime_method = models.CharField(max_length=60, default='')
    cefazolin = models.CharField(max_length=30, default='')
    cefazolin_method = models.CharField(max_length=60, default='')
    ampicillin = models.CharField(max_length=30, default='')
    ampicillin_method = models.CharField(max_length=60, default='')
    penicillin = models.CharField(max_length=30, default='')
    penicillin_method = models.CharField(max_length=60, default='')
    erythromycin = models.CharField(max_length=30, default='')
    erythromycin_method = models.CharField(max_length=60, default='')
    clindamycin = models.CharField(max_length=30, default='')
    clindamycin_method = models.CharField(max_length=60, default='')
    tetracycline = models.CharField(max_length=30, default='')
    tetracycline_method = models.CharField(max_length=60, default='')
    levofloxacin = models.CharField(max_length=30, default='')
    levofloxacin_method = models.CharField(max_length=60, default='')
    ciprofloxacin = models.CharField(max_length=30, default='')
    ciprofloxacin_method = models.CharField(max_length=60, default='')
    daptomycin = models.CharField(max_length=30, default='')
    daptomycin_method = models.CharField(max_length=60, default='')
    vancomycin = models.CharField(max_length=30, default='')
    vancomycin_method = models.CharField(max_length=60, default='')
    linezolid = models.CharField(max_length=30, default='')
    linezolid_method = models.CharField(max_length=60, default='')
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

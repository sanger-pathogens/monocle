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
    host_status = models.CharField(max_length=256, default='', blank=True, null=True)
    study_name = models.CharField(max_length=600, default='', blank=True, null=True)
    study_ref = models.CharField(max_length=400, default='', blank=True, null=True)
    selection_random = models.CharField(max_length=10, default='', blank=True, null=True)
    country = models.CharField(max_length=90, default='', blank=True, null=True)
    county_state = models.CharField(max_length=200, default='', blank=True, null=True)
    city = models.CharField(max_length=200, default='', blank=True, null=True)
    collection_year = models.SmallIntegerField(default=None, blank=True, null=True)
    collection_month = models.SmallIntegerField(default=None, blank=True, null=True)
    collection_day = models.SmallIntegerField(default=None, blank=True, null=True)
    host_species = models.CharField(max_length=100, default='', blank=True, null=True)
    gender = models.CharField(max_length=10, default='', blank=True, null=True)
    age_group = models.CharField(max_length=30, default='', blank=True, null=True)
    age_years = models.IntegerField(default=None, blank=True, null=True)
    age_months = models.IntegerField(default=None, blank=True, null=True)
    age_weeks = models.IntegerField(default=None, blank=True, null=True)
    age_days = models.IntegerField(default=None, blank=True, null=True)
    disease_type = models.CharField(max_length=100, default='', blank=True, null=True)
    disease_onset = models.CharField(max_length=10, default='', blank=True, null=True)
    isolation_source = models.CharField(max_length=100, default='', blank=True, null=True)
    serotype = models.CharField(max_length=7, default='', blank=True, null=True)
    serotype_method = models.CharField(max_length=100, default='', blank=True, null=True)
    infection_during_pregnancy = models.CharField(max_length=10, default='', blank=True, null=True)
    maternal_infection_type = models.CharField(max_length=100, default='', blank=True, null=True)
    gestational_age_weeks = models.SmallIntegerField(default=None, blank=True, null=True)
    birthweight_gram = models.IntegerField(default=None, blank=True, null=True)
    apgar_score = models.SmallIntegerField(default=None, blank=True, null=True)
    ceftizoxime = models.CharField(max_length=30, default='', blank=True, null=True)
    ceftizoxime_method = models.CharField(max_length=60, default='', blank=True, null=True)
    cefoxitin = models.CharField(max_length=30, default='', blank=True, null=True)
    cefoxitin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    cefotaxime = models.CharField(max_length=30, default='', blank=True, null=True)
    cefotaxime_method = models.CharField(max_length=60, default='', blank=True, null=True)
    cefazolin = models.CharField(max_length=30, default='', blank=True, null=True)
    cefazolin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    ampicillin = models.CharField(max_length=30, default='', blank=True, null=True)
    ampicillin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    penicillin = models.CharField(max_length=30, default='', blank=True, null=True)
    penicillin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    erythromycin = models.CharField(max_length=30, default='', blank=True, null=True)
    erythromycin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    clindamycin = models.CharField(max_length=30, default='', blank=True, null=True)
    clindamycin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    tetracycline = models.CharField(max_length=30, default='', blank=True, null=True)
    tetracycline_method = models.CharField(max_length=60, default='', blank=True, null=True)
    levofloxacin = models.CharField(max_length=30, default='', blank=True, null=True)
    levofloxacin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=30, default='', blank=True, null=True)
    ciprofloxacin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    daptomycin = models.CharField(max_length=30, default='', blank=True, null=True)
    daptomycin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    vancomycin = models.CharField(max_length=30, default='', blank=True, null=True)
    vancomycin_method = models.CharField(max_length=60, default='', blank=True, null=True)
    linezolid = models.CharField(max_length=30, default='', blank=True, null=True)
    linezolid_method = models.CharField(max_length=60, default='', blank=True, null=True)
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

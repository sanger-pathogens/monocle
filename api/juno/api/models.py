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
        INVASIVE = "invasive"

    sample_id = models.CharField(max_length=256, primary_key=True)
    lane_id = models.CharField(max_length=256, unique=True, null=True)
    supplier_sample_name = models.CharField(max_length=256, default='')
    public_name = models.CharField(max_length=256, unique=True)
    host_status = models.CharField(max_length=256, choices=HostStatus.choices)
    study_name = models.CharField(max_length=256, null=True)
    study_ref = models.CharField(max_length=256, null=True)
    selection_random = models.CharField(max_length=256, null=True)
    country = models.CharField(max_length=256, null=True)
    country_state = models.CharField(max_length=256, null=True)
    city = models.CharField(max_length=256, null=True)
    collection_year = models.CharField(max_length=256, null=True)
    collection_month = models.CharField(max_length=256, null=True)
    collection_day = models.CharField(max_length=256, null=True)
    host_species = models.CharField(max_length=256, null=True)
    gender = models.CharField(max_length=256, null=True)
    age_group = models.CharField(max_length=256, null=True)
    age_years = models.CharField(max_length=256, null=True)
    age_months = models.CharField(max_length=256, null=True)
    age_weeks = models.CharField(max_length=256, null=True)
    age_days = models.CharField(max_length=256, null=True)
    disease_type = models.CharField(max_length=256, null=True)
    disease_onset = models.CharField(max_length=256, null=True)
    isolation_source = models.CharField(max_length=256, null=True)
    serotype = models.CharField(max_length=7, null=False)
    serotype_method = models.CharField(max_length=256, null=True)
    infection_during_pregnancy = models.CharField(max_length=256, null=True)
    maternal_infection_type = models.CharField(max_length=256, null=True)
    gestational_age_weeks = models.CharField(max_length=256, null=True)
    birthweight_gram = models.CharField(max_length=256, null=True)
    apgar_score = models.CharField(max_length=256, null=True)
    ceftizoxime = models.CharField(max_length=256, null=True)
    ceftizoxime_method = models.CharField(max_length=256, null=True)
    cefoxitin = models.CharField(max_length=256, null=True)
    cefoxitin_method = models.CharField(max_length=256, null=True)
    cefotaxime = models.CharField(max_length=256, null=True)
    cefotaxime_method = models.CharField(max_length=256, null=True)
    cefazolin = models.CharField(max_length=256, null=True)
    cefazolin_method = models.CharField(max_length=256, null=True)
    ampicillin = models.CharField(max_length=256, null=True)
    ampicillin_method = models.CharField(max_length=256, null=True)
    penicillin = models.CharField(max_length=256, null=True)
    penicillin_method = models.CharField(max_length=256, null=True)
    erythromycin = models.CharField(max_length=256, null=True)
    erythromycin_method = models.CharField(max_length=256, null=True)
    clindamycin = models.CharField(max_length=256, null=True)
    clindamycin_method = models.CharField(max_length=256, null=True)
    tetracycline = models.CharField(max_length=256, null=True)
    tetracycline_method = models.CharField(max_length=256, null=True)
    levofloxacin = models.CharField(max_length=256, null=True)
    levofloxacin_method = models.CharField(max_length=256, null=True)
    ciprofloxacin = models.CharField(max_length=256, null=True)
    ciprofloxacin_method = models.CharField(max_length=256, null=True)
    daptomycin = models.CharField(max_length=256, null=True)
    daptomycin_method = models.CharField(max_length=256, null=True)
    vancomycin = models.CharField(max_length=256, null=True)
    vancomycin_method = models.CharField(max_length=256, null=True)
    linezolid = models.CharField(max_length=256, null=True)
    linezolid_method = models.CharField(max_length=256, null=True)
    additional_metadata = models.CharField(max_length=256, null=True)
    submitting_institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="samples"
    )

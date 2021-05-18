# Generated manually using Django 3.1 on 2021-05-05 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210319_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='host_status',
            field=models.CharField(max_length=256, null=False),
        ),
        migrations.AddField(
            model_name='sample',
            name='age_days',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='age_group',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='age_months',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='age_weeks',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='age_years',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ampicillin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ampicillin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='apgar_score',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='birthweight_gram',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefazolin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefazolin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefotaxime',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefotaxime_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefoxitin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='cefoxitin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ceftizoxime',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ceftizoxime_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ciprofloxacin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='ciprofloxacin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='city',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='clindamycin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='clindamycin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='collection_day',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='collection_month',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='collection_year',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='country',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='county_state',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='daptomycin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='daptomycin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='disease_onset',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='disease_type',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='erythromycin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='erythromycin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='gender',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='gestational_age_weeks',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='host_species',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='infection_during_pregnancy',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='isolation_source',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='levofloxacin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='levofloxacin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='linezolid',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='linezolid_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='maternal_infection_type',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='penicillin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='penicillin_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='selection_random',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='serotype_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='study_name',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='study_ref',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='supplier_sample_name',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='sample',
            name='tetracycline',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='tetracycline_method',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='vancomycin',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='vancomycin_method',
            field=models.CharField(max_length=256, null=True),
        ),
    ]

# Generated by Django 2.1.5 on 2020-12-28 09:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=3)),
                ('name', models.CharField(max_length=128)),
                ('dueDate', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required', models.BooleanField(default=False)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=3)),
                ('marks', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=100)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentComponentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assessmentComponent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.AssessmentComponent')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submissionDate', models.DateTimeField(blank=True, null=True)),
                ('lateStatus', models.CharField(blank=True, choices=[('1', '1 Band'), ('2', '2 Bands')], max_length=1)),
                ('noDetriment', models.BooleanField(default=False)),
                ('goodCause', models.BooleanField(default=False)),
                ('goodCauseAction', models.CharField(blank=True, choices=[('Resit', 'Resit Exam'), ('CA', 'Credit Awarded')], max_length=5)),
                ('markedGrade', models.DecimalField(decimal_places=2, max_digits=5)),
                ('finalGrade', models.DecimalField(decimal_places=2, max_digits=5)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128, unique=True)),
                ('creditsWorth', models.IntegerField(validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(5)])),
                ('name', models.CharField(max_length=200)),
                ('shortHand', models.CharField(max_length=50)),
                ('year', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('academicYearTaught', models.CharField(max_length=50)),
                ('semester', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(max_length=2000)),
                ('comments', models.TextField(blank=True, max_length=500)),
                ('minimumPassGrade', models.CharField(max_length=2)),
                ('minimumRequirementsForCredit', models.DecimalField(decimal_places=2, max_digits=3)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(decimal_places=2, max_digits=5)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=128)),
                ('lastName', models.CharField(max_length=128)),
                ('myCampusName', models.CharField(max_length=128)),
                ('studentID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)])),
                ('anonID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)])),
                ('academicPlan', models.CharField(max_length=128)),
                ('currentYear', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('graduationDate', models.DateField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, max_length=500)),
                ('courses', models.ManyToManyField(to='chemapp.Course')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.AddField(
            model_name='coursegrade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Student'),
        ),
        migrations.AddField(
            model_name='assessmentgrade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Student'),
        ),
        migrations.AddField(
            model_name='assessmentcomponentgrade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Student'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Course'),
        ),
        migrations.AlterUniqueTogether(
            name='coursegrade',
            unique_together={('course', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='assessmentgrade',
            unique_together={('assessment', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='assessmentcomponentgrade',
            unique_together={('assessmentComponent', 'student')},
        ),
    ]

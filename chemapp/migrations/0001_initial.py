# Generated by Django 2.1.5 on 2021-01-25 10:56

import colorfield.fields
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
                ('weight', models.DecimalField(decimal_places=2, help_text='eg.0.50', max_digits=3)),
                ('totalMarks', models.PositiveIntegerField(help_text='eg.50', verbose_name='Total Marks Available')),
                ('assessmentName', models.CharField(help_text='eg.Lab 1', max_length=200)),
                ('dueDate', models.DateTimeField(help_text='eg.11/10/2021 at 0800', verbose_name='Due Date and Time')),
                ('slug', models.SlugField()),
                ('componentsAdded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required', models.BooleanField(default=False)),
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
                ('assessmentComponent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.AssessmentComponent', verbose_name='Assessment Component')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submissionDate', models.DateTimeField(verbose_name='Submission Date and Time')),
                ('lateStatus', models.CharField(blank=True, choices=[('1', '1 Band'), ('2', '2 Bands')], max_length=1, verbose_name='Late Status')),
                ('noDetriment', models.BooleanField(default=False, verbose_name='No Detriment Policy')),
                ('goodCause', models.BooleanField(default=False, verbose_name='Good Cause')),
                ('goodCauseAction', models.CharField(blank=True, choices=[('Resit', 'Resit Exam'), ('CA', 'Credit Awarded')], max_length=5, verbose_name='Good Cause Action')),
                ('markedGrade', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Marked Grade')),
                ('finalGrade', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Final Grade')),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='eg. CHEM1005', max_length=30)),
                ('creditsWorth', models.IntegerField(help_text='5-20 Credits', validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(5)], verbose_name='Credits Worth')),
                ('name', models.CharField(help_text='eg.Biological Chemistry 3', max_length=200)),
                ('shortHand', models.CharField(help_text='eg.BIOCHEM3', max_length=30)),
                ('year', models.IntegerField(help_text='1-5', validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('academicYearTaught', models.CharField(help_text='eg.2019-2020', max_length=9, verbose_name='Academic Year Taught')),
                ('semester', models.IntegerField(help_text='1-2', validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(max_length=2000)),
                ('comments', models.TextField(blank=True, help_text='Anything worth mentioning', max_length=2000)),
                ('minimumPassGrade', models.CharField(help_text='eg.B3', max_length=2, verbose_name='Minimum Pass Grade')),
                ('minimumRequirementsForCredit', models.DecimalField(decimal_places=2, help_text='eg.0.60', max_digits=3, verbose_name='Minimum Requirements For Credit')),
                ('slug', models.SlugField(unique=True)),
                ('courseColor', colorfield.fields.ColorField(choices=[('#FFFFFF', 'white'), ('#000000', 'black')], default='#FFFFFF', max_length=18)),
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
            name='Degree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degreeCode', models.CharField(help_text='eg.4H-CMC', max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=128, verbose_name='First Name')),
                ('lastName', models.CharField(max_length=128, verbose_name='Last Name')),
                ('myCampusName', models.CharField(max_length=128, verbose_name='myCampus Name')),
                ('studentID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Student ID')),
                ('anonID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Anonymous ID')),
                ('academicPlan', models.CharField(max_length=128, verbose_name='Academic Plan')),
                ('currentYear', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)], verbose_name='Current Year')),
                ('graduationDate', models.DateField(blank=True, null=True, verbose_name='Graduation Date')),
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
            model_name='course',
            name='degree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Degree'),
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
            name='course',
            unique_together={('code', 'degree')},
        ),
        migrations.AlterUniqueTogether(
            name='assessmentgrade',
            unique_together={('assessment', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='assessmentcomponentgrade',
            unique_together={('assessmentComponent', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='assessmentcomponent',
            unique_together={('description', 'assessment')},
        ),
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together={('assessmentName', 'course')},
        ),
    ]

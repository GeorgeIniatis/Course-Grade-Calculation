# Generated by Django 2.1.5 on 2021-02-03 12:03

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
                ('totalMarks', models.PositiveIntegerField(help_text='eg.50', verbose_name='Total Marks')),
                ('assessmentName', models.CharField(help_text='eg.Lab 1', max_length=200, verbose_name='Assessment Name')),
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
                ('status', models.CharField(max_length=20)),
                ('marks', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=100)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Assessment')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentComponentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
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
                ('level', models.CharField(choices=[('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Level 3'), ('3-M', 'Level 3 MSci'), ('3-CS', 'Level 3 Chemical Studies'), ('4-M', 'Level 4 MSci'), ('4-H-CHEM', 'Level 4 Variation 1'), ('4-H-CMC', 'Level 4 Variation 2'), ('4-H-C&M', 'Level 4 Variation 3'), ('5-M', 'Level 5 Variation 1'), ('5-M-CHEM', 'Level 5 Variation 2'), ('5-M-CMC', 'Level 5 Variation 3'), ('5-M-C&M', 'Level 5 Variation 4'), ('5-M-CP', 'Level 5 Variation 5')], max_length=20)),
                ('year', models.PositiveIntegerField()),
                ('academicYearTaught', models.CharField(help_text='eg.19-20', max_length=5, verbose_name='Academic Year Taught')),
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
                ('numberOfCourses', models.PositiveIntegerField(default=0, verbose_name='Number of Courses')),
                ('numberOfStudents', models.PositiveIntegerField(default=0, verbose_name='Number of Students')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Student ID')),
                ('anonID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Anonymous ID')),
                ('firstName', models.CharField(max_length=128, verbose_name='First Name')),
                ('lastName', models.CharField(max_length=128, verbose_name='Last Name')),
                ('level', models.CharField(choices=[('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Level 3'), ('3-M', 'Level 3 MSci'), ('3-CS', 'Level 3 Chemical Studies'), ('4-M', 'Level 4 MSci'), ('4-H-CHEM', 'Level 4 Variation 1'), ('4-H-CMC', 'Level 4 Variation 2'), ('4-H-C&M', 'Level 4 Variation 3'), ('5-M', 'Level 5 Variation 1'), ('5-M-CHEM', 'Level 5 Variation 2'), ('5-M-CMC', 'Level 5 Variation 3'), ('5-M-C&M', 'Level 5 Variation 4'), ('5-M-CP', 'Level 5 Variation 5')], max_length=20)),
                ('graduationDate', models.DateField(blank=True, verbose_name='Graduation Date')),
                ('comments', models.TextField(blank=True, max_length=2000)),
                ('gapYear', models.BooleanField(default=False)),
                ('academicPlan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.Degree', verbose_name='Academic Plan/Degree')),
                ('courses', models.ManyToManyField(blank=True, to='chemapp.Course')),
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

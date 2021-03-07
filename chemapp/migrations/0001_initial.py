# Generated by Django 3.1.6 on 2021-03-07 16:04

import colorfield.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=5, help_text='eg.0.50', max_digits=6)),
                ('totalMarks', models.PositiveIntegerField(help_text='eg.50', verbose_name='Total Marks')),
                ('assessmentName', models.CharField(help_text='eg.Lab 1', max_length=200, verbose_name='Assessment Name')),
                ('dueDate', models.DateTimeField(help_text='eg.11/10/2021 at 0800', verbose_name='Due Date and Time')),
                ('slug', models.SlugField()),
                ('componentNumberNeeded', models.PositiveIntegerField(default=0, help_text='Includes required and optional components', verbose_name='Component Number Needed')),
                ('map', models.TextField(blank=True, null=True, verbose_name='22 Scale Map')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='eg. CHEM1005', max_length=30)),
                ('creditsWorth', models.IntegerField(help_text='5-120 Credits', validators=[django.core.validators.MaxValueValidator(120), django.core.validators.MinValueValidator(5)], verbose_name='Credits Worth')),
                ('name', models.CharField(help_text='eg.Biological Chemistry 3', max_length=200)),
                ('shortHand', models.CharField(help_text='eg.BIOCHEM3', max_length=30)),
                ('level', models.CharField(choices=[('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Honours'), ('4', 'Postgraduate')], max_length=20)),
                ('academicYearTaught', models.CharField(help_text='eg.19-20', max_length=5, verbose_name='Academic Year Taught')),
                ('semester', models.CharField(choices=[('1', 'Semester 1'), ('2', 'Semester 2'), ('Both', 'Both')], max_length=20)),
                ('description', models.TextField(max_length=2000)),
                ('comments', models.TextField(blank=True, help_text='Anything worth mentioning', max_length=2000)),
                ('minimumPassGrade', models.CharField(help_text='eg.B3', max_length=2, verbose_name='Minimum Pass Grade')),
                ('minimumPassGrade22Scale', models.PositiveIntegerField()),
                ('minimumRequirementsForCredit', models.DecimalField(decimal_places=2, help_text='eg.0.60', max_digits=3, verbose_name='Minimum Requirements For Credit')),
                ('numberOfStudents', models.PositiveIntegerField(default=0, verbose_name='Number of Students')),
                ('slug', models.SlugField(unique=True)),
                ('courseColor', colorfield.fields.ColorField(default='#FF0000', max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degreeCode', models.CharField(help_text='eg.4H-CMC', max_length=30, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('numberOfCourses', models.PositiveIntegerField(default=0, verbose_name='Number of Courses')),
                ('numberOfStudents', models.PositiveIntegerField(default=0, verbose_name='Number of Students')),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staffID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Staff ID')),
                ('title', models.CharField(choices=[('Dr', 'Dr'), ('Mr', 'Mr'), ('Miss', 'Miss'), ('Mrs', 'Mrs')], max_length=20, verbose_name='Title')),
                ('firstName', models.CharField(max_length=128, verbose_name='First Name')),
                ('lastName', models.CharField(max_length=128, verbose_name='Last Name')),
                ('username', models.CharField(max_length=128)),
                ('comments', models.TextField(blank=True, help_text='Anything worth mentioning', max_length=2000)),
            ],
            options={
                'verbose_name_plural': 'Staff',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentID', models.PositiveIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Student ID')),
                ('anonID', models.BigIntegerField(unique=True, validators=[django.core.validators.MaxValueValidator(9999999)], verbose_name='Anonymous ID')),
                ('firstName', models.CharField(max_length=128, verbose_name='First Name')),
                ('lastName', models.CharField(max_length=128, verbose_name='Last Name')),
                ('level', models.CharField(choices=[('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Honours Level 3'), ('4', 'Honours Level 4'), ('5', 'Honours Level 5'), ('6', 'Postgraduate')], max_length=20)),
                ('graduationDate', models.DateField(blank=True, verbose_name='Graduation Date')),
                ('comments', models.TextField(blank=True, max_length=2000)),
                ('gapYear', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=20)),
                ('academicPlan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.degree', verbose_name='Academic Plan/Degree')),
                ('courses', models.ManyToManyField(blank=True, to='chemapp.Course')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='degree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.degree'),
        ),
        migrations.AddField(
            model_name='course',
            name='lecturers',
            field=models.ManyToManyField(to='chemapp.Staff', verbose_name='Course Lecturers'),
        ),
        migrations.CreateModel(
            name='AssessmentComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=20)),
                ('marks', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.assessment')),
                ('lecturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.staff')),
            ],
            options={
                'unique_together': {('description', 'assessment')},
            },
        ),
        migrations.AddField(
            model_name='assessment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.course'),
        ),
        migrations.CreateModel(
            name='CourseGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveIntegerField()),
                ('band', models.CharField(max_length=2)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.student')),
            ],
            options={
                'unique_together': {('course', 'student')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('code', 'degree')},
        ),
        migrations.CreateModel(
            name='AssessmentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submissionDate', models.DateTimeField(verbose_name='Submission Date and Time')),
                ('noDetriment', models.BooleanField(default=False, verbose_name='No Detriment Policy')),
                ('goodCause', models.BooleanField(default=False, verbose_name='Good Cause')),
                ('markedGrade', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Marked Grade')),
                ('finalGrade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Final Grade')),
                ('finalGradePercentage', models.PositiveIntegerField(blank=True, null=True, verbose_name='Final Grade Percentage')),
                ('finalGrade22Scale', models.PositiveIntegerField(blank=True, null=True, verbose_name='Final Grade Out of 22')),
                ('band', models.CharField(blank=True, max_length=2, null=True)),
                ('componentNumberAnswered', models.PositiveIntegerField(default=0, help_text='Includes required and optional components', verbose_name='Component Number Answered')),
                ('late', models.BooleanField(default=False, verbose_name='Late')),
                ('componentNumberMatch', models.BooleanField(default=False, verbose_name='Component Numbers Match')),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.assessment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.student')),
            ],
            options={
                'unique_together': {('assessment', 'student')},
            },
        ),
        migrations.CreateModel(
            name='AssessmentComponentGrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('assessmentComponent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.assessmentcomponent', verbose_name='Assessment Component')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemapp.student')),
            ],
            options={
                'unique_together': {('assessmentComponent', 'student')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together={('assessmentName', 'course')},
        ),
    ]

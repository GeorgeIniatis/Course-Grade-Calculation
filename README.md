# Team Project H 2020 Group CS35
 Welcome to our Team Project. This projects aim is to provide a grading hub for the School of Chemistry at UofG.

### Running project locally

First clone the repository

 `$ git clone https://stgit.dcs.gla.ac.uk/tp3-2020-CS35/cs35-main.git`

 Once cloned, we create a virtual Enviroment and install Dependencies

 `$ pip install -r requirements.txt`

 When you have the required Depenencies for the enviroment we can run

 `$ python manage.py makemigrations chemapp`

 This will create the database needed to run our project.

 `$ python manage.py runserver`

 This will start our project. The site will be bare as this will be a fresh database file. We have provided some simple populations scripts.

    -   populate_user.py (creates some admin and staff acounts for testing not production)


 To run, stop the server and run the command below:

 `$ python populate_user.py`

 You will see a print out on the console of all the data used to populate the database, such as username and passwords for the temporary accounts. NOT FOR PRODUCTION.




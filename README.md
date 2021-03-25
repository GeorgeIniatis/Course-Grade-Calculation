# Team Project H 2020 Group CS35
 Welcome to our Team Project. This projects aim is to provide a grading hub for the School of Chemistry at UofG.

 Data Entry Flow:

Degrees -> Courses ->

### Running project locally

First clone the repository

 `$ git clone https://stgit.dcs.gla.ac.uk/tp3-2020-CS35/cs35-main.git`

Install Dependencies e.g. on Virtual Machine/server

 `$ pip install -r requirements.txt`

 When you have the required Depenencies for the enviroment we can run

 `$ python manage.py makemigrations chemapp`

 `$ python manage.py migrate`

The CMD below will generate some default admin and user accounts. NOT for production!
You will see a print out on the console of all the data used to populate the database, such as username and passwords for the temporary accounts.

  `$ python populate_user.py`

Run CMD below to start the WebApp.

 `$ python manage.py runserver`

 This will start our project. The site will be bare as this will be a fresh database file.

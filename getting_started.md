<h1> Getting Started for Developers </h1>

This document deals with the requisite knowledge for developing the data layer of tmdb (the model layer). Contributors who are simply interested in designing the web-based interface (contributing and designing static HTML/CSS for viewing database contents) however are not required to follow it.

<h2> Requisite Knowledge </h2>
tmdb primarily makes use of Django, which is a Python framework for creating web applications (a database which exists on the server and HTML views to interact with the database). However, it is very simple to get started with Django - the introductory tutorial is a great place to start, and very easy to understand, and it can accessed here: https://docs.djangoproject.com/en/1.8/intro/tutorial01/

The tutorial teaches how the database is structured using Django's built-in Object-Relational Mapper, how changes to the database can be managed via migrations, how to use the controller interface which Django automatically creates when you develop the ORM, and how to use its built-in templating interface for dynamically generating views.

The application also utilizes a PostgreSQL database backend. Knowledge of PostgreSQL is not required. Developers will have the option of either installing and configuring PostgreSQL to use the preconfigured credentials in settings.py, or they can reconfigure their development environment to use an alternative database implementation which is compatible with Django instead, such as SQLite. Using SQLite, for example, will probably be easier than using PostgreSQL, but there is a very small chance that modifications which work in one database are not compatible with another.

The application is written using Python 3.x. Developers should take care to ensure that they are using this version of Python and not 2.x.

<h1> First Steps</h1>
<h2> Installing the Requisite Software </h2> 
<h3> Installing Python (Required) </h3>
Most Linux distributions provide Python by default, but not all provide Python 3, so take care to ensure that's the version you're using.

This tutorial will provide most instructions in Bash, so Cygwin is recommended for Windows developers, but not at all necessary for those who feel comfortable configuring their Python and database environment. Instructions on how to install Cygwin are not provided here, but again, all developers must take care to ensure that they are using Python 3.

Creating a Python Virtualenv (Recommended)
A virtualenv is recommended, but not required, as doing so keeps tmdb development and dependencies separate from the root Python installation. virtualenv is generally not provided with Python by default, but can be installed as follows:

```easy_install virtualenv``` 

Root privileges may be required for this command to work.

Then to create a virtualenv, run:

```virtualenv -p $(which python3) tmdb_local/```
This will create a copy of your Python installation into a directory called tmdb_local/ (you are free to change this to any directory you like, of course). Having a copy of your Python installation will allow you to install Python dependencies into a location that's specific to tmdb development. It is only required to execute this command once. Then every time you wish to start Python development, you must execute:

```source tmdb_local/bin/activate ``` 
for all active terminal sessions.

** Make sure that you have the right version of python running. You can do 
```python --version``` 
to figure out what version you are running. 
mkvirtualenv -p /usr/local/bin/python3.5 ectc
source ectc/bin/activate

<h3> Installing PostgreSQL (Required if using PostgreSQL) </h3>
If you are using PostgreSQL, then it is recommended to install the latest version (currently 9.5.x). Django's implementation of the PostgreSQL database backend requires pelican and psycopg2, so install them by executing as follows:

```pip3 install psycopg2 pelican```

If you have not already done so, be sure to include postgresql-devel (or libpq-dev in Ubuntu)

To install postgres, you should do;
```sudo apt-get install postgresql postgresql-contrib```

<h2> Credential Setup </h2>

Establishing the correct credentials for the PostgreSQL database is fairly complex and dependent upon how PostgreSQL was installed, so it will not be covered here in detail. However, at a minimum, it is necessary to create a username and database for the tmdb user, and configure the tmdb user to connect locally. In order to run unit tests, it will also be necessary to grant permission to create and delete databases as the tmdb user.


Run the following commands:

```createuser tmdb -d
createdb tmdb``` 
And add the following to pg_hba.conf:
```
# IPv4 local connections:
host    all             tmdb            127.0.0.1/32            trust
# IPv6 local connections:
host    all             tmdb            ::1/128                 trust
```
The location of the pg_hba.conf varies machine to machine, but mine was located at: /etc/postgresql/9.3/main

After doing that, reload the pg_hba. Restart postgres 
```/etc/init.d/postgresql restart```

<h2> Installing Django (Required) </h2>
Install Django into your Python environment:

`pip3 install django`

Note the version of Django is going to be important to the installation of this program. For now, use Django 1.8 or if you installed a later version, you can use django-enumfield 1.3b2 by doing `pip3 install --pre django-enumfield==1.3b2`

<h1> Running the Unit Tests </h1>
Once the database is configured, navigate to where the source code was checked out and run the following command to test the models and database configuration:

```python3 manage.py test tests``` 

<h1> Downloading the ectc-registration folder </h1>
Be sure to check out the other repo [https://github.com/ashish-b10/ectc_registration] in a separate folder and run 
```
python -m ectc_registration.gdocs_downloader -c /home/user/desktop/tournament_manager_credentials.json -u (INSERT THE APPROPRIATE spreadsheet link)
```
to make sure it works properly. The `tournament_manager_credentials.json` should be downloaded from the Google account or can be requested by the owners of this repo. This json file should be saved in the same folder as everything else in this repo.

This key wil include the `private_key` as well as various auth tokens that will be necessary for downloading the files directly from the Google spreadsheet.


<h2> Run Server </h2>
To make model migrations: 
```python manage.py makemigrations tmdb``` 

To run the server locally,
```python manage.py runserver```

If there are ever any changes to the models.py file, you will have to reset the database. You can do this by doing either: 
```rm -r tmdb/migrations ; dropdb tmdb && createdb tmdb && python manage.py makemigrations tmdb && python manage.py migrate && python manage.py add_test_data``` or simply run `bash ./reset_db.sh`.

<h2> Possible problems that may occur</h2>
- Make sure to install libffi-dev if there is a version error. You can solve this by doing `sudo apt-get install libffi-dev`

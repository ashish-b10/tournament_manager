# Getting Started

This document details how to set up and run an instance of the ECTC Tournament Manager. It is not (yet) a user interface guide.

## Recommended Knowledge
`tmdb` primarily makes use of Django, which is a Python framework for creating web applications (a database which exists on the server and HTML views to interact with the database). Users do not need to have a complete understanding of Django to use the software (though it certainly does not hurt!).

For developers, it is very simple to get started with Django - the introductory tutorial is a great place to start, and very easy to understand - it can accessed [here](https://docs.djangoproject.com/en/2.2/intro/tutorial01/). It conveys most of the information users need to hack on the site.

## Setting up your Environment

Let's start by creating a directory where we can store all of our files:

```
mkdir -p ~/dev/tournament_manager && cd ~/dev/tournament_manager
```

In this directory, we will clone the project, create our virtual environments, and store our data (assuming we are using SQLite).

Start by cloning the project:

```
git clone git@github.com:ashish-b10/tournament_manager.git
```

This will create a directory called `tournament_manager` where the *code* will be stored.

Next, create a virtual environment:

```
python3 -m venv tmdb_venv
```

**Take care to use `python3` and NOT `python`.**

Source the virtual environment:

```
source tmdb_venv/bin/activate
```

And install the dependencies into it:

```
pip3 install -r tournament_manager/requirements.txt
```

Next, the database must be set up. It is recommended that users use PostgreSQL for development, to more closely simulate the production environment, but we'll set SQLite up for now as it is much easier. The database configuration is in `tournament_manager/ectc_tm_server/db_settings.py`,

```
cd tournament_manager/ectc_tm_server
```

but since the configuration cannot be stored in version control, a few sample files (`db_settings_sqlite.py` and `db_settings_postgresql.py`) are provided. To select the SQLite setup:

```
cp db_settings_sqlite.py db_settings.py
```

The `.gitignore` file in this directory has an entry for `db_settings.py`, so it will not be added to version control.

Additionally, run `generate_custom_settings.py` to generate some more variables which are sensitive and should also not be stored in production:

```
python3 generate_custom_settings.py
```

The most important value in this file is `SECRET_KEY` - the value this is set to on the production server must not be made public. The script will write them out to a file called `custom_settings.py` which, once again, is in this directory's `.gitignore` file.

Now we can write the schema to the database:

```
cd ../ # cd to the root of the project repository (ie. tournament_manager/)
python3 manage.py migrate
```

The `migrate` command scans the project for database migrations and writes them into the database. When any database model is added, changed or deleted, it is necessary to generate a migration for the change and re-run this command.

At last, we are ready to view the web application! First, start the development server:

```
python3 manage.py runserver
```

And then open the following link in a webbrowser: http://localhost:8000

You should be greeted with a page that says "No tournaments have yet been created."

There is one last task we should run. In order to perform any operations on the website, it is necessary to create a user. Cancel the development server and run:

```
python3 manage.py create_headtable_user -u USERNAME -p PASSWORD
```

Replace USERNAME and PASSWORD as desired. Now restart the server and attempt to log in. It should be possible to create new seasons, tournaments and schools in the database.

## Database Backend

The tutorial thus far has assumed using SQLite - SQLite is nice for an easy development setup, but it is not usable on production (one reason being that it does not support multiple concurrent connections which is crucial for handling several requests simultaneously).

Setting up PostgreSQL instead is not difficult from a Django configuration perspective - simply replace `db_settings.py` with the contents of `db_settings_postgresql.py`. However, setting PostgreSQL itself can be non-trivial, and is outside the scope of this guide as there are too many possible setups to document.

Nevertheless, developers who are going to do a significant amount of manipulation of database models should attempt to use PostgreSQL so the development environment most closely resembles production.

## Loading Sample Data

Django has functionality to export and reload data. To dump data from an existing database:

```
python3 manage.py dumpdata
```

And to load it back:

```
python3 manage.py loaddata /path/to/dumpfile
```

Note that the `dumpdata` command will dump some files that should not be transferred from one database to another - doing so will cause integrity errors because the contents are created when `manage.py migrate` is executed. Thus, it may be necessary to open a database shell

```
python3 manage.py dbshell
```

And clear out the problematic tables - usually `django_content_type` and `auth_permisison`:

```
sqlite> DELETE FROM django_content_type;
```

Then the `loaddata` command should be successful.

## Channels Backend

### Background

Django was written during a time when web services were simple: clients initiate transmissions (usually either GET or POST requests) to a server and the server would respond. For better or for worse (and in Ashish's opinion, significantly worse), novel web applications also utilize opposite operations: server-initiated transmissions for data that is updated in between client requests. An example of this feature in `tournament_manager` is in the list of sparring matches. Updates from the server are pushed to the client without any user interaction.

Django supports this transactional model using an extension called `channels`. `channels` is a package that implements websocket support in Django applications. Websocket connections are stateful, persistent connections where either the client or the server can initiate a request. The idea is:

1. The client makes a request for a webpage

2. The server responds with an HTML document with some Javascript that sets up one or more websocket connections.

3. The client parses the page and initiates the websocket connections to the server. The server has special URLs for handling these types of requests.

4. Once the connection is established, the server can push new information to the client. The client as well can transmit information over the websocket connection, rather than having to make a new HTTP request.

For more information, see the [channels documentation](https://channels.readthedocs.io/en/latest/).

### Setup

Before jumping in, it is worth noting that it is not necessary to set this up unless a websocket-enabled view is being modified. Currently, only the updates for the matches requires this functionality.

For Django and the `tournament_manager` application, setting up the websocket connections is not too involved. Developers must have a working `redis` server available for their use. The easiest way to do this is to install `redis` via a package manager; alternately, it can also be downloaded and installed from [here](https://redis.io/).

Once it is installed and running, take care to edit `REDIS_HOST` in `db_settings.py` if the server is not available on `localhost`. The port number is also set in `ectc_tm_server/settings.py` in the `CHANNEL_LAYERS` variable.

## Database Model Visualization

It can be very helpful to visualize the database models and the relationships between them. Here is an example of the model visualization taken from commit [5ba2458d79](https://github.com/ashish-b10/tournament_manager/commit/5ba2458d7988975f9895e93a4587b72a66e6ecd8):

![database model visualization](model.png)

It shows a clear definition of which columns are in which table and the types of those columns. It also shows relationships between the tables (ie. each SparringTeam has a foreign key reference to the School that it is affiliated with). This diagram makes writing database queries much easier, and it is also useful for planning new model relationships.

To set this up for yourself, first install graphviz using your operating system's package manager. For example:

```
sudo xbps-install graphviz
```

Then install `pygraphviz` into the virtual environment:

```
pip install pygraphviz
```

Because `pygraphviz` is a C-based library, it requires the graphviz development headers to build and install. Either install the headers or alternately, install `pydot` which does not have this requirement:

```
pip install pydot
```

Then generate them image like so:

```
python3 manage.py graph_models --pydot -a -g -o tmdb.png
```

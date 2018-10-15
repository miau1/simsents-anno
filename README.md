# simsents-anno

Simsents-anno is an online tool for annotating paraphrases.

# Deployment documentation

This documentation shows step by step how to deploy simsents-anno Django-application on Ubuntu 16.04 using an Apache server. The tool can be set up as a private version, where each user has to login with their account credentials, or a public version, where the tool is open for anyone to use and the users are tracked by their IP address.

## Tools and services used

- [cPouta](https://research.csc.fi/pouta-user-guide) (optional), virtual machine
- [Python3](https://docs.python.org/3/)
- [Django](https://docs.djangoproject.com/en/1.11/), web framework for Python
- [Apache2](https://httpd.apache.org/), web server
- [WSGI](https://modwsgi.readthedocs.io/en/develop/), Apache mod to host a Python app
- [PostgreSQL](https://www.postgresql.org), database
- [Psycopg2](http://initd.org/psycopg/), PostgreSQL adapter for Python
- [Let's encrypt](https://letsencrypt.org/), SSl certificate provider

## [cPouta](https://research.csc.fi/pouta-getting-started)

If you plan to use cPouta, prepare SSH keys and security groups, launch an instance (standard-tiny flavor should be enough, boot from image and choose Ubuntu 16.04) and assign a floating ip for the instance.

## [Install Pip for Python3, Apache server and WSGI mod](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04)

Pip package management system is used to install packages. Apache is a web server. WSGI is an Apache module that allows Apache to host a Python application. Installation:

```
sudo apt-get update
sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
```

## Configure and enable firewall on Ubuntu

Allow SSH connections and connections to ports 80(http) and 443(https)

```
sudo ufw allow 'OpenSSH'
sudo ufw allow 'Apache Full'
sudo ufw enable
```

## Virtual environment and Django

Install Django within a virtual environment. 

Install virualenv with pip:

```
sudo pip3 install virtualenv
```

Create a virtual environment:

```
mkdir ~/myproject
cd ~/myproject
virtualenv myprojectenv
```

Activate the virtual environment:

```
source myprojectenv/bin/activate
```

Install Django with the virtual environment activated:

```
pip3 install django
```

Download code for Simsents app:

```
git clone https://github.com/miau1/simsents-anno.git
```

Create a file "secret.txt" containing [a Django secret key](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY) (generate one here for example: https://www.miniwebtool.com/django-secret-key-generator/).

In simsents/settings.py:

- Update path to "secret.txt".
- Update ALLOWED_HOSTS (see your hostname at: www.displaymyhostname.com)
- Update 'DIRS' in TEMPLATES

## Update Apache configuration file

Include the following lines in /etc/apache2/sites-available/000-default.conf (update paths):

Set path to static files and grant access:
```
Alias /static/ /path/to/myproject/simsents-anno/static/

<Directory /path/to/myproject/simsents-anno/static>
	Require all granted
</Directory>

```

Prepare WSGI daemon process and set paths to the Django application, virtual environment and wsgi.py file, and grant access:
```
WSGIDaemonProcess simsents python-path=/path/to/myproject/simsents-anno python-home=/path/to/myproject/myprojectenv
WSGIProcessGroup simsents
WSGIScriptAlias / /path/to/myproject/simsents-anno/simsents/wsgi.py

<Directory /path/to/myproject/simsents-anno/simsents>
<Files wsgi.py>
	Require all granted
</Files>
</Directory>
```

## [PostgreSQL](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04)

PostgreSQL is used as our database.

Install PostgreSQL:

```
sudo apt-get update
sudo apt-get install libpq-dev postgresql postgresql-contrib
```

EITHER 1: create a new empty database OR 2: create a database from a dump file.

1: Create new a database:

```
sudo su - postgres
psql
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'password';
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
\q
exit
```

2: Create a database from a dump file:

```
sudo su - postgres
psql
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
\q
psql myproject -c "GRANT ALL ON ALL TABLES IN SCHEMA public to myprojectuser;"
psql myproject -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to myprojectuser;"
psql myproject -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to myprojectuser;"
exit
sudo -u postgres psql newproject < database.dump
```

Create files "dbusr.txt", "dbpw.txt" and "db.txt", for postgresql username, password and database name. In the above example, username is "myprojectuser", password is "password" and database name is "myproject".

In simsents/settings.py, update paths to dbusr.txt, dbpw.txt and db.txt.

Psycopg2 allows us to use PostgresSQL database with a Python application. Installation:

```
pip3 install psycopg2
```

Migrate data structures to the database:

```
python3 manage.py makemigrations
python3 manage.py migrate
```

Create a superuser:
```
python3 manage.py createsuperuser
```

You can now deactivate the virtual environment:

```
deactivate
```

## [Configure SSH connection with Let's encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-14-04)

Install certbot and generate certificate files:

```
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-apache
sudo certbot --apache -d yourhostname.com
```

Inlcude the following changes to /etc/apache2/sites-available/000-default.conf:

Port 443 is used to allow secure HTTPS connection:
```
<VirtualHost *:443>
```

Set SSL engine on and set paths to the certificate keyfiles. The keyfiles should be located at /etc/letsencrypt/live. Replace "yourhostname.com" with your actual hostname:
```
SSLEngine ON
SSLCertificateFile /etc/letsencrypt/live/yourhostname.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/yourhostname.com/privkey.pem
```

Your /etc/apache2/sites-available/000-default.conf should now look like this (with different paths):

```
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        Alias /static/ /path/to/myproject/simsents-anno/static/

        <Directory /path/to/myproject/simsents-anno/static>
        	Require all granted
        </Directory>

        WSGIDaemonProcess simsents python-path=/path/to/myproject/simsents-anno python-home=/path/to/myproject/myprojectenv
        WSGIProcessGroup simsents
        WSGIScriptAlias / /path/to/myproject/simsents-anno/siments/wsgi.py

        <Directory /path/to/myproject/simsents-anno/simsents>
        <Files wsgi.py>
			Require all granted
        </Files>
        </Directory>

        SSLEngine ON
        SSLCertificateFile /etc/letsencrypt/live/yourhostname.com/fullchain.pem
        SSLCertificateKeyFile /etc/letsencrypt/live/yourhostname.com/privkey.pem
</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

Start Apache server

```
sudo systemctl start apache2
```

The web site now works at https://yourhostname.com.

The first thing you need to do is associate the superuser to an annotator object. The web site doesn't work for users, who are not paired with annotator objects:

- Go to https://yourhostname.com/admin
- Login with superuser credentials
- Click "Add" on Annotators row
- Select the superuser name and save

## Public version of the tool

By default, the tool required all users to login with credentials. To convert the tool to be open to everyone, rename `views.py` something else and rename `views-pub.py` `views.py`. For example:

```
cd annotate
mv views.py views-pri.py
mv views-pub.py views.py
```

Restart the apache server:

`sudo systemctl restart apache2`

To convert the tool back to private version, rename `views.py` something else and rename `views-pri.py` `views.py`

## Add sentence pairs to database

If you created an empty database, you can use sents_to_db.py to add test sentences into the database. With you virtual environment activated, run:

```
python3 manage.py shell < testsentences/sents_to_db.py
```

To add your own sentence pair data, replace the contents of `testsentences/*.txt` with your data.

## Adding users

- Go to admin site ("/admin" or click "Admin site" on your user page), and login with your superuser account
- On the Users row, click "Add"
- Give the user a username and a password (you can generate a password here for example: https://passwordsgenerator.net/) and save
- On the admin site, click "Add" on Annotators row
- Select the user you just created and save

## Backups
Create a dump file from the database

```
sudo -u postgres pg_dump myproject > outfile.dump
```

## Restore database from a dump file

```
sudo su - postgres
psql
CREATE DATABASE newproject;
GRANT ALL PRIVILEGES ON DATABASE newproject TO myprojectuser;
\q
psql newproject -c "GRANT ALL ON ALL TABLES IN SCHEMA public to myprojectuser;"
psql newproject -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to myprojectuser;"
psql newproject -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to myprojectuser;"
exit

sudo -u postgres psql newproject < outfile.dump
```

Remember to update the database name in your "db.txt" file.


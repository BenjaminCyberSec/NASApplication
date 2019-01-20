


## System Requirements

- Ubuntu 18.04 LTS (Or other Debian based Linux distro that supports Python version 3.6)
- Python 3.6


## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/BenjaminCyberSec/NASApplication
cd NASApplication
```

Install the requirements:

```bash
pip install -r requirements.txt
pip install --upgrade git+https://github.com/blockstack/secret-sharing

```
(The newest package of that library has not been pushed on the pip repository yet)

Set the servers's secret salt as environement variable
e.g. with bash_profile

```bash

export DEFF_FILE_SALT="FILE_SALT"
export DEFF_KEY_SALT="KEY_SALT"
export DEFF_KEY_PASSWORD="KEY_PASSWORD"
```

e.g. with Powershell

```bash
setx DEFF_FILE_SALT "FILE_SALT"
setx DEFF_KEY_SALT "KEY_SALT"
setx DEFF_KEY_PASSWORD "KEY_PASSWORD"
```

**Restart the terminal or powershell to apply the change**

Apply the migrations:


```bash

python manage.py migrate --run-syncdb
```

Create an admin account (you will use it to confirm users)

```bash
python manage.py createsuperuser
```


Finally, run the development server:

```bash
python manage.py runserver
```

**The application access parameters:**


Localhost: http://127.0.0.1:8000/ (access user pages only)


Admin url: http://127.0.0.1:8000/admin/ (Default django admin interface)

Note1:
As long as a user has not been validated, the connection page will output the credentials are invalid.

Note2:
When the project runs locally, Django will print email text (used to activate user and to transmit keys of shared files) to the console. In production the settings file may be edited to provide the host, the port, the credentials as well as TLS and SSL.

In production, the value of “SECRET_KEY” in the file settings.py should be changed. Its usage is made mandatory by Django as it uses it to secure signed data.



## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/BenjaminCyberSec/NASApplication
```

Install the requirements:

```bash
pip install -r requirements.txt
pip install --upgrade git+https://github.com/blockstack/secret-sharing

```
(The newest package of that library has not been pushed on the pip repository yet)

```bash
cd NASApplication
```

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

Localhost: http://127.0.0.1:8000/ (access user pages only)


Admin url: http://127.0.0.1:8000/admin/registration_validation/ (access admin pages only - default django option have been set unavaible)

Note1:
As long as the user has not been validated, the connection page will output the credentials are unvalid. Superuser account cannot use the website, their credentials only workin for admin section.


Note2:
When the project is run locally, django will print mails (use to transmit keys of shared files) on the console.
In production the settings file has to be edited to provide the host, the port, the credentials as well as tls and ssl like explained in the rapport

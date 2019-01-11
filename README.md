

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/BenjaminCyberSec/NASApplication
```

Install the requirements:

```bash
pip install -r requirements.txt

pip install git+https://github.com/blockstack/secret-sharing
```
(The newest package of that library has not been pushed on the pip repository yet)

```bash
cd NASApplication/example
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


Finally, run the development server:

```bash
python manage.py runserver
```

Note:
When the project is run locally, django will print mails (use to transmit keys of shared files) on the console.
In production the settings file has to be edited to provide the host, the port, the credentials as well as tls and ssl like explained in the rapport

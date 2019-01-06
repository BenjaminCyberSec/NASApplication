

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/BenjaminCyberSec/NASApplication
```

Install the requirements:

```bash
pip install -r requirements.txt
```

```bash
cd NASApplication/example
```

Set the servers's secret salt as environement variable
e.g. with bash_profile

```bash

export DEFF_FILE_SALT = "FILE_SALT"
export DEFF_KEY_SALT = "KEY_SALT"
```

e.g. with Powershell

```bash
setx DEFF_FILE_SALT "FILE_SALT"
setx DEFF_KEY_SALT "KEY_SALT"
```

Restart the terminal or powershell to apply the change

Apply the migrations:


```bash

python manage.py migrate --run-syncdb
```


Finally, run the development server:

```bash
python manage.py runserver
```

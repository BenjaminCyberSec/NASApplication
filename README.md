

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/niweiwang/NASApplication
```

Install the requirements:

```bash
pip install -r requirements.txt
```

```bash
cd NASApplication/example
```

Apply the migrations:

```bash

python manage.py migrate
```

Finally, run the development server:

```bash
python manage.py runserver
```

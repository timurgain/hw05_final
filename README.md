# Yatube blog final version

## Description 
 
Yatube is a blog of publications with images and communities, a subscription to authors and a feed of their posts is implemented.

The project consists of three applications: posts, users, about.

Models implemented in the project: Post, Group, Comment, Follow, Contact.

The project is covered with tests, in particular models, forms, urls, views.

## Technologies

- Python 3;
- Django 2.2;
- Django template language;
- Django Unittest;
- SQLlite;
- HTML and CSS.

## Installation and launch

Clone repository and navigate to folder on command line::

```
git clone ...
```

```
cd yatube_blog_final
```

Create and activate virtual environment:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from requirements.txt file:

```
pip install -r requirements.txt
```

Run migrations:

```
python3 manage.py migrate
```

Launch the project:

```
python3 manage.py runserver
```

## How to run the tests

Run all project tests

```
python3 manage.py test
```

Run tests in one application only
```
python3 manage.py test your_app
```
Run tests in certain app and file
```
python3 manage.py test posts.tests.test_urls
```

Go to [Django documentation](https://docs.djangoproject.com/en/3.2/topics/testing/overview/) for more info about tests.
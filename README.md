﻿# Dream Land
> Pet project

Django project for sharing dreams with others, check your dream statistic and look for dream of other users.

## Check it out!

[Dream project deployed to Render](https://dream-land-4k1a.onrender.com/)


## Installation

Python3 must be installed:

```shell
git clone https://github.com/MasakDirt/dream-land.git
cd dream_land
python -m venv env
source env/bin/activate  # For Windows: `env\Scripts\activate`
pip install -r requirements.txt
```

Then you need to migrate db:
```shell
python manage.py makemigrations
python manage.py migrate
```
And finally create superuser and start server
```shell
python manage.py createsuperuser
python manage.py runserver
```


## Features

* Creations user
* Adding profile pictures
* Create your own dream description with different symbols and emotions
* Check your dreams statistic
* Check other users dreams, like/dislike and comment it


## User credentials for testing

| login | password  |
|-------|-----------|
| user  | user12345 |


## Demo
![Project diagram](demo.png)

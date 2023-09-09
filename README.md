
# My EMS Narrative


### About The Project

This project is the source code for the website <a href="https://www.myemsnarrative.com">www.myemsnarrative.com</a>. 

This website was created to help EMS providers write custom narratives for their patient care reports. Users are given pre-written narrative templates and phrase templates to construct a narrative fast. Users also have the ability to create and customize any templates available to them on the site.


### Built With

* Javascript/JQuery
* HTML
* CSS
* Python3
* Django Framework
* MySQL (for deployment)
* Apache 2 (for deployment)
* Linode (for deployment)


## Getting Started

Follow the instructions below to clone this project to your local server.


### Prerequisites


1. (Optional, but recommended) Create a virtual environment for the project's dependencies.
```sh
 python3 -m venv venv
```

2. Activate your new virtual environment.
```sh
 source venv/bin/activate
```

3. Download the required dependencies.
```sh
 pip install django
 ```
```sh
 pip install mysqlclient
```

### Open Project


1. Clone down the project from github.
```sh
 git clone git@github.com:raffenmb/myemsnarrative.git
```

2. Move into the project's directory.
```sh
 cd myemsnarrative
```

3. Start the development server.
```sh
 python manage.py runserver
```

4. Open any browser and go to http://127.0.0.1:8000/. This will take you to a local developmental version of the actual website. 
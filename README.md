
# My EMS Narrative


## About The Project

This project is the source code for the website <a href="https://www.myemsnarrative.com">www.myemsnarrative.com</a>. 

This website was created to help EMS providers write custom narratives for their patient care reports. Users are given pre-written narrative templates and phrase templates to construct narratives from. Users are able to edit and save these templates, as well as create their own, in order to write narratives faster while on the job.

![narrative_page](https://github.com/raffenmb/myemsnarrative/assets/27787317/1729acf9-2969-497b-892d-d3f3d636a4ce)

### Built With

* Python3
* Django Framework
* JavaScript/JQuery
* Ajax
* HTML
* CSS

## Installation

1. Clone the repo.
<!-- tsk --> 
    git clone git@github.com:raffenmb/myemsnarrative.git
3. Go to the local repo folder, create a virtual environment, and activate it.
<!-- tsk --> 
    python3 -m venv venv
<!-- tsk --> 
    source venv/bin/activate
3. Pip install the project's requirements.
<!-- tsk --> 
    pip install -r requirements.txt

## Usage

To use this project locally, you need to start Django's development server. While still in the main repo folder containing manage.py, run the following:
<!-- tsk --> 
    python manage.py runserver

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) from any browser to begin using the project.

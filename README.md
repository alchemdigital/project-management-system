# PROJECT MANAGEMENT SYSTEM

**Alchem Digital's project management system**

## Web version

* Visit https://pms.alchemdigital.com and choose **Register as admin** to use it

## Requirements

* python3
* pip
* mysql or any other database
* virtualenv (Recommended)

## Setup Instruction

* create a virtualenv
* clone the repository and navigate to the project root directory
* run **pip install -r requirements.txt**
* Put **settings.py** inside **manager/** directory
* Create a database with the name in the **settings.py** file
* run **python manage.py makemigrations**
* run **python manage.py migrate**
* run **python manage.py runserver**
* Now open **http://127.0.0.1:8000** in the browser to see the app up and running
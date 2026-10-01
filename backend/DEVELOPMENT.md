# Django backend

## Development

### Requirements

* Python 3.10+
* Visual Studio Code
  * Extension: "Python" (ms-python.python)

### Instructions

To run the project:

* Open this folder in Visual Studio code
* F1 -> "Python: Create Environment" -> "Venv" -> ... "requirements.txt"
* F1 -> "Python: Select Interpreter" -> ".venv"
* "Run and Debug"
  * `manage.py makemigrations`
  * `manage.py migrate`
  * `manage.py createsuperuser`
  * `manage.py seeddata`
  * `manage.py runserver`
  * `manage.py runserver (debug logs)`
* Open <http://localhost:8000> in the web browser.


### Example accounts:

* testadmin: testpass
* testuser: testpass


### Creating a staff account

* Open <http://localhost:8000/admin> in the web browser.
* Login with these credentials:
  * Username: admin
  * Password: admin
* Create a new "User" object
  * Enable "Staff status"
* Create a new "User Profile" object
  * Set "User" to be the user you just made
* Logout
* Open <http://localhost:8000/login>
* Login with the staff user's credentials


## Source Template

This project was created from:

```
django-admin startproject mysite .
django-admin startapp myapp
```

## Reference

<https://docs.djangoproject.com/en/5.2/>
<https://docs.djangoproject.com/en/5.2/intro/overview/>
<https://code.visualstudio.com/docs/python/tutorial-django>
<https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django>
<https://www.w3schools.com/django/>
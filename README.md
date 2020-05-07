# Bachelor for the Department of Health Sciences in Gjøvik

To what extent can a camera system help increase the skills of the students by opening up collaborative learning for the Nurse Education at NTNU Gjøvik, and can this system be used as a basis for giving assessment in the subject? And how can it help sensors grade students?

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Windows 10 or Linux based OS (Ubuntu, Fedora, Zorin OS.. etc)
Python 3.6 or above
OBS Studio 25.0.8 or above
obs-websocket - Remote-control OBS Studio from WebSockets
```

### Installing

To run this program should be installed as a single file on a SD card.
But if you want to run it on another server you need to install Flask, Requests, asyncio, mfrc522, sqlite3.

Each of these can be installed by running this command in windows 10
```
pip install flask requests asyncio mfrc522
```

or if you are on a linux based OS.
```
sudo pip3 install flask requests asyncio mfrc522
```

For sqlite you install it with
```
sudo apt-get install sqlite3
```

Check requirements.txt for detailed info about required files and software.

**Web-server**  
This program should be run with uWSGI and Nginx for optimal performance and load balancing.

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

To check if the user actually exists, we do a simple comparison against our database record, and if he or she doesn't exists, we redirect them to our registration page.

```Python
def user_exist(x):
    def check_if_user_exists(user):
        db = Database()
        usr = db.student_exists(user)
        return usr
    res = check_if_user_exists(x)
    return res
```

### And coding style tests

The code is made to be simple and expanded upon as time goes on. 
This basic setup is what we use to check if as user exists based on input made to our index page.
There is no sanitization, as most people wont have access to this website at all.
```Python
exists = user_exist(saved)
session['account'] = form_data['studentID']
session.permanent = True

if exists is True:
    session['f_name'] = Database().get_user_f_name(session['account'])
```

## Deployment
Install on a SD card for use in Raspberry Pi 3 or above.  
Write the ISO file to SD card, and it should work.



## Built With

* [Flask](https://www.palletsprojects.com/p/flask/) - The web framework used
* [Nginx](https://www.nginx.com/) - Open Source Web server
* [uWSGI](https://flask.palletsprojects.com/en/1.1.x/deploying/uwsgi/) - Application servers
* [Python 3.6+](https://www.python.org/) - Programming language

## Authors

* **André Tølen Lønvik** - *Backend developer* - [Burning-Panda](https://github.com/Burning-Panda)
* **Kay André Smådal** - *Frontend designer*
* **Christian Ringlund** - *Technician and Frontend developer*

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is a bachelor project, and has limited access. Please don't distibute these files.
License after 02.06.2020 CC BY-NC-SA 4.0

## Acknowledgments

* "Department of Health Sciences in Gjøvik" for bringing us this assignment.
* NTNU i Gjøvik
* Veileder Kjell Are


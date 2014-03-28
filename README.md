Customer Hunter
===============

What do we do? We find customers on Twitter. 
Why? Because money and things. 
How? That's proprietary. 
When? Also proprietary. 
Where? Proprietary. 

### Dependencies

Things you'll need in the order that you'll need them:

* [Git](http://git-scm.com/downloads)
* [Python 2.7 (preferably 2.7.6)](http://python.org/downloads/windows)
* [MySQL Database](http://dev.mysql.com/downloads/mysql/)
* [Scikit-learn](http://scikit-learn.org/stable/install.html#windows-installer)
* [Python-twitter](https://github.com/bear/python-twitter)
* [Peewee Python ORM](https://github.com/coleifer/peewee)

### Contributing

If you are planning on contributing code to this project, please fork the project and do all of your work in the development branch. After you feel like you're finished and you're ready for your code to join the master codebase, please submit a pull-request and tag the relevant issue(s) in your pull-request.

Note: for ALL code we're using 4-space tabs. Please do not commit any code with any other type of tabs (tab char, etc)

### Installation

#### Installing Git

Run through the graphical installer wizard nonsense that Windows wants you to do. Use the default install location and click next.

Select components:

Windows Explorer integration
- Simple Context Menu
	- Git Bash Here
	- Git GUI Here
- Associate .git...
- Associate .sh....

Click next. Next again. Select run Git from the windows command prompt.

Click next. Click next. Click finish.

#### Installing Python 2.7.6

Run through graphical installer nonsense again. Click next.

Next. Next. Finish.

#### Installing MySQL Database 5.6

KEY POINT: IF YOU KNOW YOUR COMPUTER IS 64-BIT THEN USE THE 64-BIT INSTALLER. OTHERWISE USE 32-BIT.

Once you click on the link and you click download it'll take you to another page. Select the download button that says Windows (x86, 32-bit), MSI Installer. And in parentheses below it says (mysql-installer-web-comunity-5.16.0.msi).

After that, your download will start. The installer will run and you will click Install Mysql Products.

Accept the license. Click execute. Wait. Then click next. Leave it on developer default. Click next. Click execute. It will download some shit that you need here like connectors and what-not.

Once that's done, click next. Click next again. UNCHECK Open Firewall port for network access. CHECK the advanced configuration option. Click next.

It'll ask you for MySQL Root Password. Write it down. Type it in, type it in the box below to confirm. You'll need to know this to run this app.

It'd probably be prudent to add your own user account, so click the Add User button and name it whatever you want. Leave the fields default and enter in a password of your choosing. Also write this down. Once finished with that menu, click next, leave those as default (this will start up MySQL on your computer startup, probably preferable). Click next.

Leave the logging stuff default. Click next.

Click next. Click next. Finish up the install, you can start MySQL workbench if you want, that's just the GUI for using the database. You probably won't use it a bunch.

#### Installing Scikit

You'll need the scipy stack. [here](www.lfd.uci.edu/~gohlke/pythonlibs/#scipy) click on Scipy-stack-14.2.16.win32-py2.7.exe

Then download scikit. [here](www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn) click on scikit-learn-0.14.1.win32-py2.7.exe

The installers for these should be really easy. Just keep clicking through until they're done.

#### Installing Easy-install

Install ez_setup.py: https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

Save that in your documents or wherever, just remember where you saved it. Once it's downloaded, go to it and double click on it. This should execute the file with Python. It should download a setuptools.zip folder. 

Extract that and then go inside of the folder and double click on the setup file. This should install it.


#### Installing Pip

After that you need to navigate to your Python scripts folder. Open up a command prompt in Windows and type in these commands:

```

cd C:\Python27\Scripts

easy_install pip

```

Keep your command prompt up, you'll need it right there again.

#### Installing Python-twitter

Start up your git gui, it should be in your start menu now. Click on 'clone an existing repository'.

Source location is https://github.com/bear/python-twitter
Target location is C:\Python27\Scripts\python-twitter

You should still have your command prompt ready. At this point do these commands:

```

dir

# It should say C:\Python27\Scripts, if so, do the following commands, if not do cd C:\Python27\Scripts

pip install -r python-twitter\requirements.txt

cd python-twitter

setup.py build

setup.py install

cd ..
```

This should mean that python-twitter is installed by now (it'll error out if not). If it's not you're a little screwed up and you need to let me know. 

Keep command prompt up.

#### Installing Peewee

Start up the git gui again and click on clone existing repo.

Source location: https://github.com/coleifer/peewee
Target location: C:\Python27\Scripts\peewee

From the command prompt, do these commands:

```

dir

# It should still say C:\Python27\Scripts, if so do the following commands, if not do cd C:\Python27\Scripts

cd peewee
setup.py install
```

You can close your command prompt.

#### Installing customer-hunter

Finally, if everything has gone well, which I hope it has, then you're ready to install our app. Crack open the git gui again and click on clone existing repo.

Source location: http://github.com/pshahid/customer-hunter

The target location is your desktop this time.
Target location: C:\Path\To\Your\Desktop  

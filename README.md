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
* [MySQL Database Connector](http://dev.mysql.com/downloads/connector/python/)
* [Scikit-learn](http://scikit-learn.org/stable/install.html#windows-installer)
* [Python-twitter](https://github.com/bear/python-twitter)
* [Peewee Python ORM](https://github.com/coleifer/peewee)

### Installation

#### Installing Git

Run through the graphical installer wizard nonsense that Windows wants you to do. Use the default install location and click next.

Select components:

Windows Explorer integration
- Simple Context Menu
	- Git Bash Here
	- Git GUI Here

Associate .git...
Associate .sh....

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

#### Installing Python-twitter

Start up your git gui, it should be in your start menu now. Click on 'clone an existing repository'.

Source location is 'https://github.com/bear/python-twitter'
Target location is


Once you've installed Git, Python, MySQL, and Scikit, you'll need to install both Python-twitter and Peewee from Github. This is relatively simple, but 
you'll be on Windows, so I'm not sure exactly 
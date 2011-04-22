Thanks for downloading TinyGraph.

The installation is not yet stable. This document will be finalised when the 
project is.

The project is not yet easily distributable and as such this installation 
guide vaguely explains how to get things running, it is more of a check list
for starting development rather than a guide for installation.

Non-Python Requirements
=======================

beanstalkd
----------

This is what prepares visualisations between page requests, so graphs are 
ready to view when you need them. See the following link for installation 
procedures for your operating system:

http://kr.github.com/beanstalkd/download.html

Python Requirements
===================

See [requirements.txt][1] if you want to view the full list, however all you 
need to do is (using pip) install these dependencies to your python path (I 
recommend installing to a virtual environment if you know how to do that.)

    pip install -r requirements.txt

[1]: https://github.com/marcuswhybrow/tinygraph/blob/master/requirements.txt

Configure TinyGraph
===================

This is always changing right now so if you have cloned the repo, then just
wait until Django throughs an exception, see what it is and then fill it out 
in `settings.py`. There are zero of these at the moment, but there may be in 
the future.

Run TinyGraph
=============

First we need to setup TinyGraph's database, which is currently handled via
Django's `syncdb` command and various helpful fixtures:

    python manage.py syncdb

**Start the Message Queue:**

    beanstalkd -d -l 127.0.0.1 -p 11300

And then start the consumer:

    python manage.py consumer start


**Start the Server:**

At the moment the simplest way to run tinygraph is using the Django 
development server:

    python manage.py runserver 0.0.0.0:8000

You could run in under Apache (which is fiddly) but on the TO-DO list is a 
self contained production server within the project which you just start as a 
daemon.

**Start the Poller:**

The poller is a separate daemon which will one day have an init script so it 
starts up automatically when the OS does etc. For now just start it using a
handle Django management command I have written:

    python manage.py tinygraphd start|stop|restart

**Go to page:**

    http://localhost:8000/
identifier
=============
sudo apt-get install python-dev ghostscript libxml2-dev libxslt-dev



Configure the celery daemon:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copy the required files from the extras directory:

    $ sudo cp ~/src/hid/hid/extras/celeryd/etc/init.d/celeryd /etc/init.d/celeryd

    $ sudo cp ~/src/hid/hid/extras/celeryd/etc/default/celeryd /etc/default/celeryd

Open /etc/default/celeryd and update the path to your formhub install directory, if you directory structure is identical to what is described above, you only need to update your username.

Start the celery daemon

    $ sudo /etc/init.d/celeryd start

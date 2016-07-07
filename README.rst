======
Matriz
======

.. image:: https://badge.fury.io/py/matriz.png
    :target: http://badge.fury.io/py/matriz

.. image:: https://badge.fury.io/py/matriz.svg
        :target: https://badge.fury.io/py/matriz


Matriz is a `Networked Music Performance <https://en.wikipedia.org/wiki/Networked_music_performance>`_ software.
The intended use is allowing real time musical performance of artists in different locations through computer networks.
The name "matriz" is portuguese for "matrix" and is inspired on the light and sound matrixes used in music and theater settings.


Why?
----

* Tools like `jacktrip <https://ccrma.stanford.edu/groups/soundwire/software/jacktrip/>`_ are built
  to work in high bandwidth academic networks like the internet2 or GEANT networks.
  Matriz is built to offer the lowest latencies possible, while using the lest bandwidth possible.
  This allows musician to have low latency high quality music streaming using regular network connections.
* For fun.

Features
--------

* Low latency (using OPUS codec)
* Easy to use and extend
* Tested in live performances
* Documentation: https://matriz.readthedocs.org.


What?
-----

The software is composed of two components, the client and the configuration server.
The client connects to the server over websockets and receives a list of all connected clients.
After starting it's own RTSP stream with audio from the sound card, it spawns an RTSP client for all connected clients, forming a P2P streaming network.
For all connection or disconnection events, the client list is broadcasted to all connected clients, which open or close new RTSP clients as necessary.
Audio is encoded with the OPUS codec, which allows for low bandwidth use and high quality sound, while keeping the latency to a minimum.

The system was used several times in live peformances, with three three groups of musicians.
Distances between groups ranged from tens of meters (same building) to 150 to 400 km in the final performance.
The hardware used was a Raspberry pi 2 with a Focusrite Scarlet 2i2 USB sound card.
The resulting streams where broadcasted live at http://stress.fm.
More information, including recordings of the performances, can be obtained at the project website: http://matriz.stress.fm.
For any inquiries concerning the software or the project, contact us at info@stress.fm.

Installation
------------

Prerequisites
.............

In both cases external dependencies must be installed for the program to work. For the client:

* Jack
* GStreamer, including the gst-rtsp-server package and Pyhton bindings
* Python bindings for gobject-introspection libraries

These can be installed in Debian or Rapsbian whith the following command::

    $ echo "deb http://matriz.stress.fm/deb_repo jessie main" | sudo tee /etc/apt/sources.list.d/matriz.list
    $ curl http://matriz.stress.fm/deb_repo/matriz_deb.gpg.asc | sudo apt-key add -
    $ sudo apt-get update

    $ sudo apt-get install -y python-pip\
                         jackd2 \
                         python-gst-1.0 \
                         python-gi \
                         libgstrtspserver-1.0-0 \
                         gstreamer1.0-plugins-bad \
                         libgstreamer-plugins-bad1.0 \
                         gir1.2-gst-rtsp-server-1.0 \
                         python-dev \
                         libffi-dev

    # For the PI

    $ curl https://raw.githubusercontent.com/stressfm/matriz/master/config/etc-dbus-1-system.d-matriz-jackd.conf | sudo tee /etc/dbus-1/system.d/matriz_jackd.conf >/dev/null
    $ curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-config.txt | sudo tee /boot/config.txt > /dev/null
    $ curl https://raw.githubusercontent.com/stressfm/matriz/master/config/boot-cmdline.txt | sudo tee /boot/cmdline.txt >/dev/null
    $ curl https://raw.githubusercontent.com/stressfm/matriz/master/config/supervisord.conf | sudo tee /etc/supervisord.conf >/dev/null
    $ for cpu in /sys/devices/system/cpu/cpu[0-9]*; do echo -n performance | sudo tee $cpu/cpufreq/scaling_governor; done
    $ sudo pip install supervisor
    $ sed -i "$(wc -l /etc/rc.local | cut -d' ' -f1)i supervisord -c /etc/supervisord.conf" /etc/rc.local
    $ sudo reboot


For the server, if you want to stream the performance, you might want to install and configure:

* liquidsoap (to receive and combine client streams)
* icecast2 (to stream the combined audio from all clients)
* GStreamer (to decode client streams)

Using PyPi
..........
To install the program just to use the client::

    $ pip install matriz

In the machine where the server will run, server dependencies must be explicitly installed::

    $ pip install matriz[server]

Install Script for Raspberry Pi
...............................

Or simply run the following command which performs all the steps above (Raspberry Pi specific *DO NOT* use on other OS)::

    curl https://raw.githubusercontent.com/stressfm/matriz/master/scripts/install.sh | sudo bash -

Usage
-----


Client
......

To use the client open a shell and just type::

    $ matriz

without arguments, to start the client. The program will try to read configuration options from a file
called client.json in the same directory where the program was invoked.
If you want to use another filename, just give that as an argumento to the program::

    $ matriz <filename>

An example configuration file is in config/client.json:

.. code-block:: json

    {
        "key": "key1",
        "name": "porto",
        "url": "ws://localhost:5000/config",
        "interface": "eth0",
        "port": 8554,
        "client_pem": "fake_client.pem",
        "client_crt": "fake_client.crt",
        "ca_crt": "fake_ca.crt"
    }

`key:` supposed to be unique id for client
`name:` some label  identifying the client
`url:` the configuration server url
`interface:` network card to start de emitter on
`port:` port for emitter to listen on
`client_pem:` openssl key for secure websockets
`client_crt:` openssl client certificate
`ca_crt:` openssl server certificate

To get a list of command line arguments type::

  $ matriz -h

Server
......
The configuration server is just a single file Flask app (matriz/config_server.py). For deployment instructions consult the Flask documentation at http://flask.pocoo.org. The server will try to read configuration options from the file given in the
MATRIZ_CONFIG_FILE environment variable or, if not set, from a file called clients.json in the same directory
where the program was invoked. An example configuration file can be found in config/clients.json:

.. code-block:: json

	{
	  "client_keys": [
		{"name": "porto", "key": "key1"},
		{"name": "montemor", "key": "key2"},
		{"name": "lisboa", "key": "key3"},
		{"name": "marte", "key": "key666"}
	  ],
	  "monitor_key": {"name": "monitor", "key": "monitorkey"}
	}

Misc
....

For the software to work ports 8554 (TCP) and 8600-8700 (UDP) must be able accept incoming connections. This means you have to configure the gateways if you intend to use the software across the internet.

Partners
--------
* Oficinas do Convento
* Sonoscopia
* Osso
* Trienal de Arquitectura de Lisboa
* Digitópia - Casa da Música
* Câmara Municipal de Montemor-o-Novo.

Funding
-------
* Direção Geral das Artes.

======
Matriz
======

.. image:: https://badge.fury.io/py/matriz.png
    :target: http://badge.fury.io/py/matriz

.. image:: https://travis-ci.org/stressfm/matriz.png?branch=master
        :target: https://travis-ci.org/stressfm/matriz

.. image:: https://badge.fury.io/py/matriz.svg
        :target: https://badge.fury.io/py/matriz


Matriz is a 
.. _Networked Music Performance: https://en.wikipedia.org/wiki/Networked_music_performance 
software.  

The intended use is allowing real time musical performance of artists in different locations through computer networks.

The name "matriz" is portuguese for "matrix".


Why?
----

Tools like 
.. _jacktrip: https://ccrma.stanford.edu/groups/soundwire/software/jacktrip/
are built to work in high bandwidth academic networks like the internet2 or GEANT networks. 
Matriz is built to offer the lowest latencies possible, while using the lest bandwidth possible. 
This allows musician to have low latency high quality music streaming using domestic network connections.
This is made possible through the use of the OPUS codec.
  

Features
--------

* Low latency (using OPUS codec)
* Easy to use and extend 
* Documentation: https://matriz.readthedocs.org.


What?
-----

The software is composed of two components, the client and the configuration server.
The client captures audio and 

Installation
------------

Using PyPi
..........
To install the program just to use the client

.. code-block:: bash

  pip install matriz

In the machine where the server will run, server dependencies must be explicitly installed

.. code-block:: bash

  pip install matriz[server]

In both cases external dependencies must be installed for the program to work. For the client:

* Jack
* GStreamer, including the gst-rtsp-server package

For the server, if you want to stream the performance, you must install and configure:

* liquidsoap
* icecast2
* GStreamer

Using ansible
.............
A set of ansible playbooks is supplied in the ansible directory. These where used to install the clients in Raspberry Pi 2 machines
and the server in a Linode instance, all running Debian Jessie. All dependencies are installed and supervisord 
is used to run the programs. Be aware that these might need heavy modifications to work in another setup. 


Usage
-----

Client
......

To use the client open a shell and just type

.. code-block:: bash

  matriz

without arguments, to start the client. The program will try to read configuration options from a file 
called client.json in the same directory where the program was invoked.
If you want to use another filename, just give that as an argumento to the program:

.. code-block:: bash

  matriz <filename>

An example configuration file is in config/client.json:

.. code-block:: json
{
    "key": "key1",
    "name": "porto",
    "url": "ws://localhost:5000/config",
    "interface": "eth0",
    "port": 8554
    "client_pem": "fake_client.pem",
    "client_crt": "fake_client.crt",
    "ca_crt": "fake_ca.crt"
}
```

`key:` supposed to be unique id for client  
`name:` some label  identifying the client  
`url:` the configuration server url  
`interface:` network card to start de emitter on  
`port:` port for emitter to listen on  
`client_pem:` openssl key for secure websockets  
`client_crt:` openssl client certificate  
`ca_crt:` openssl server certificate  

To get a list of command line arguments type:

.. code-block:: bash

  matriz -h

Server
......
The server is just a Flask app. The server will try to read configuration options from the file given in the
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

# matriz
Networked Music Performance software system. 
Configure client by editing test_client.json:

```javascript
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

Start client:

```bash
$ python client.py test_client.json
```


## README ##
# Requirements #
libssl-dev: compile uwsgi with ssl and websockets  
python-dev: compile programs with python headers



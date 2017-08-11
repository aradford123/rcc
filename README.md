# Script for learning RESTCONF  (RESTCONF Console - RCC)

## Introduction

This repository presents:

* Python scripts using the ncclient library (`0.5.2` or greater as of writing) to talk to RESTCONF-enabled devices.


## Python Dependencies

The package dependencies for the scripts  are listed in ```requirements.txt```, which may be used to install the dependencies thus (note the upgrade to pip; must be running **```pip >= 8.1.2```** to successfully install some dependencies):

```
$ virtualenv env
New python executable in env/bin/python2.7
Also creating executable in env/bin/python
Installing setuptools, pip, wheel...done.
$ . env/bin/activate
$ pip install --upgrade pip
Requirement already up-to-date: pip in ./env/lib/python2.7/site-packages
$ pip install -r requirements.txt
```

This example shows using the virtualenv tool to isolate packages from your global python install. This is recommended. Note that the versiojn of pip installed in the test environment was up to date, and so it did not need upgraded.


## Python Scripts

```rcc.py``` is the main script.

### List capabilities
The first thing you can do is find a list of all of the modules supported by the device
```buildoutcfg
$ ./rcc.py --host adam-csr --user cisco --password cisco --capabilities | grep ietf
cisco-xe-ietf-ip-deviation,2016-08-10
cisco-xe-ietf-ospf-deviation,2015-09-11
cisco-xe-ietf-routing-deviation,2016-07-09
ietf-diffserv-action,2015-04-07
ietf-diffserv-classifier,2015-04-07
ietf-diffserv-policy,2015-04-07
ietf-diffserv-target,2015-04-07
ietf-inet-types,2013-07-15
ietf-interfaces,2014-05-08
ietf-interfaces-ext,
ietf-ip,2014-06-16
ietf-ipv4-unicast-routing,2015-05-25
ietf-ipv6-unicast-routing,2015-05-25
ietf-key-chain,2015-02-24
ietf-netconf-monitoring,2010-10-04
ietf-netconf-notifications,2012-02-06
ietf-ospf,2015-03-09
<SNIP>

```

### Explore a model
I can take a specfic model and download and explore the RESTCONF endpoints

````buildoutcfg
$ ./rcc/rcc.py --host adam-csr --user cisco --password cisco --explore --download ietf-interfaces,2014-05-08
rw /ietf-interfaces:interfaces
rw /ietf-interfaces:interfaces/interface=[name]
ro /ietf-interfaces:interfaces-state
ro /ietf-interfaces:interfaces-state/interface=[name]
ro /ietf-interfaces:interfaces-state/interface=[name]/higher-layer-if/higher-layer-if
ro /ietf-interfaces:interfaces-state/interface=[name]/lower-layer-if/lower-layer-if
ro /ietf-interfaces:interfaces-state/interface=[name]
````

### Make a request
The response will be JSON by default.
```buildoutcfg
$ ./rcc.py --host adam-csr --url /restconf/data/interfaces
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "GigabitEthernet1", 
        "ietf-ip:ipv6": {}, 
        "enabled": true, 
        "type": "iana-if-type:ethernetCsmacd", 
        "ietf-ip:ipv4": {
          "address": [
            {
              "ip": "10.10.20.90", 
              "netmask": "255.255.255.192"
            }
          ]
        }
      },
      {
"name": "GigabitEthernet2",
        "ietf-ip:ipv4": {
          "address": [
            {
              "ip": "10.10.10.115", 
              "netmask": "255.255.255.0"
            }
          ]
        }, 
        "ietf-ip:ipv6": {}, 
        "description": "link to internal gateway", 
        "enabled": true, 
        "type": "iana-if-type:ethernetCsmacd" 
      }, 
<SNIP>

```

### Yaml format
There is also the ```--yaml``` option to get YAML returned.
```buildoutcfg
$ ./rcc.py --host adam-csr --url /restconf/data/interfaces  --yaml
ietf-interfaces:interfaces:
  interface:
  - enabled: true
    ietf-ip:ipv4:
      address:
      - ip: 10.10.20.90
        netmask: 255.255.255.192
    ietf-ip:ipv6: {}
    name: GigabitEthernet1
    type: iana-if-type:ethernetCsmacd
  - description: link to internal gateway
    enabled: true
    ietf-ip:ipv4:
      address:
      - ip: 10.10.10.115
        netmask: 255.255.255.0
    ietf-ip:ipv6: {}
    name: GigabitEthernet2
    type: iana-if-type:ethernetCsmacd
<snip>

```

### Environment Variables
The username and password can be stored in environent variables, so you no longer need the ```--user```
and ```--password``` flags

Paste the following lines in your shell
```buildoutcfg
export RCC_USERNAME=user
export RCC_PASSWORD=password
```

## TODO
- PUT/PATCH
- implement --explore-all  combine all models, then filter on a path
- snippets for POST/PUT/PATCH
- Logging
- Python3


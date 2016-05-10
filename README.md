# Cisco UCS VLAN Management

A web interface built on Flask and the Cisco UCS Python SDK that has the
following basic functionality:

- Connect to a UCS domain
- View and Add VLANs
- Add a VLAN to a vNIC

The web UI currently has little to none error handling in place so proceed
accordingly.

## Instructions

- Run `python cisco_ucs_vlan_web_interface.py`
- Access the web interface at {{local_machine_ip_address}}:5000

## Requirements:

- [Flask](http://flask.pocoo.org/)
- [Cisco UCS Python SDK](https://communities.cisco.com/docs/DOC-37174)



## Screenshots:

![Connect to UCS Manager](https://cloud.githubusercontent.com/assets/8610203/15125356/0f1d4bfc-15f2-11e6-99c8-554b66adac2d.png)
![Cisco UCS VLANs](https://cloud.githubusercontent.com/assets/8610203/15125358/0f2b1444-15f2-11e6-8200-61bb7e947a24.png)
![Cisco UCS vNICS](https://cloud.githubusercontent.com/assets/8610203/15125357/0f26ad3c-15f2-11e6-90c4-70a21ab0a725.png)

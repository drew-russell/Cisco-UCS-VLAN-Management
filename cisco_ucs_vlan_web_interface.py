"""
A web interface built on Flask and the Cisco UCS Python SDK that has the
following basic functionality:

- Connect to a UCSM domain
- View and Add VLANs
- Add a VLAN to a vNIC

The web UI currently has little to none error handling in place so proceed
accordingly.

"""

from flask import Flask, render_template, request, redirect, url_for
from UcsSdk import UcsHandle
from UcsSdk import UcsUtils
from UcsSdk.MoMeta.FabricVlan import FabricVlan
from UcsSdk.MoMeta.VnicLanConnTempl import VnicLanConnTempl
from UcsSdk.MoMeta.OrgOrg import OrgOrg
import sys
import warnings

'''
Supress the following warning message which does not affect funcationality:

/Library/Python/2.7/site-packages/UcsSdk/UcsBase.py:1064: UserWarning: [Warning]: AddManagedObject [Description]:Expected Naming Property Name for ClassId VnicLanConnTempl not found
  warnings.warn(string)

'''
warnings.filterwarnings("ignore")


def ssl_workaround():
    """ Workaround for SSL certification error that prevents proper
    UCS domain login when using Python 2.7 or higher. Credit to user Rahul Gupta
    (ragupta4) on the Cisco UCS Communities """
    is_verify_certificate = False
    if not sys.version_info < (2, 6):
        from functools import partial
        import ssl

        ssl.wrap_socket = partial(
            ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1)
        if not sys.version_info < (2, 7, 9) and not is_verify_certificate:
            ssl._create_default_https_context = ssl._create_unverified_context

ssl_workaround()

app = Flask(__name__)

HANDLE = UcsHandle()


def connect():
    """ Establish a connection to the UCS Domain """

    try:
        HANDLE.Login(index.ip_address, index.username, index.password)
        index.error = "False"
    except Exception, err:
        index.error = "True"


def logout():
    """ Disconnect from the session created when connect() is called """
    HANDLE.Logout()


def current_vlans():
    """ Get a list of all current VLANs """

    connect()

    current_vlans.list = {}

    # Get the UCS VLAN object

    obj = HANDLE.GetManagedObject(None, FabricVlan.ClassId())

    # Interate through the VLAN object and return the name and ID properties

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Name":
                    vlan_name = mo.getattr(prop)

                if str(prop) == "Id":
                    vlan_id = mo.getattr(prop)

            current_vlans.list.update({vlan_name: vlan_id})

    logout()

    return current_vlans.list


def add_vlans():
    """ Create new VLANs on UCS. """

    obj = HANDLE.GetManagedObject(None, None, {"Dn": "fabric/lan"})
    HANDLE.AddManagedObject(obj, "fabricVlan", {"DefaultNet": "no", "PubNwName": "", "Dn": "fabric/lan/net-{}".format(add_vlans.name), "PolicyOwner": "local",
                                                "CompressionType": "included", "Name": "{}".format(add_vlans.name), "Sharing": "none", "McastPolicyName": "", "Id": "{}".format(add_vlans.id)})


def current_vnic_templates():
    """ Get a list of current vNICs in UCS """

    connect()

    current_vnic_templates.list = []

    # Get the UCS vNIC object

    obj = HANDLE.GetManagedObject(None, VnicLanConnTempl.ClassId())

    # Interate through the vNIC object and return the name property

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Name":
                    vnic_template_name = mo.getattr(prop)

            current_vnic_templates.list.append(vnic_template_name)

    return current_vnic_templates.list

    logout()


def current_orgs():
    """ Get a list of the current organizations in UCS which will be used in
    add_vlan_to_vnic """

    current_orgs.list = []

    obj = HANDLE.GetManagedObject(None, OrgOrg.ClassId())

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Dn":
                    org_name = mo.getattr(prop)

            current_orgs.list.append(org_name)

    current_orgs.list.remove('org-root')


def add_vlan_to_vnic():
    """ Add a VLAN to a vNIC template """

    organization = ""
    add_vlan_to_vnic.success = ""

    # Get the UCS vNIC object based on the vNIC name provided by the user

    obj = HANDLE.GetManagedObject(None, VnicLanConnTempl.ClassId(), {
                                  VnicLanConnTempl.RN: "lan-conn-templ-{}".format(add_vlan_to_vnic.vnic_name)})

    # Get the relevant vNIC object properties required to modify the vNIC

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Dn":
                    dn = mo.getattr(prop)
                    for org in current_orgs.list:
                        if org in mo.getattr(prop):
                            organization = org
                        else:
                            organization = "org-root"

                if str(prop) == "IdentPoolName":
                    ident_pool_name = mo.getattr(prop)
                if str(prop) == "QosPolicyName":
                    qos_policy_name = mo.getattr(prop)
                if str(prop) == "Descr":
                    descr = mo.getattr(prop)
                if str(prop) == "PolicyOwner":
                    policy_owner = mo.getattr(prop)
                if str(prop) == "NwCtrlPolicyName":
                    nw_ctrl_policy_name = mo.getattr(prop)
                if str(prop) == "TemplType":
                    templ_type = mo.getattr(prop)
                if str(prop) == "StatsPolicyName":
                    stats_policy_name = mo.getattr(prop)
                if str(prop) == "Mtu":
                    mtu = mo.getattr(prop)
                if str(prop) == "PinToGroupName":
                    pin_to_group_name = mo.getattr(prop)
                if str(prop) == "SwitchId":
                    switch_id = mo.getattr(prop)

    HANDLE.StartTransaction()

    # Get the current UCS organization to work with

    vnic_obj = HANDLE.GetManagedObject(
        None, None, {"Dn": "{}".format(organization)})

    # Get the relevant vNIC object

    mo = HANDLE.AddManagedObject(vnic_obj, "vnicLanConnTempl",
                                 {"IdentPoolName": "{}".format(ident_pool_name),
                                  "Dn": "{}".format(dn),
                                  "QosPolicyName": "{}".format(qos_policy_name),
                                  "Descr": "{}".format(descr),
                                  "PolicyOwner": "{}".format(policy_owner),
                                  "NwCtrlPolicyName": "{}".format(nw_ctrl_policy_name),
                                  "TemplType": "{}".format(templ_type),
                                  "StatsPolicyName": "{}".format(stats_policy_name),
                                  "Mtu": "{}".format(mtu),
                                  "PinToGroupName": "{}".format(pin_to_group_name),
                                  "SwitchId": "{}".format(switch_id)}, True)

    # Add the correct VLAN to the vNIC template

    mo_1 = HANDLE.AddManagedObject(mo, "vnicEtherIf", {
                                   "DefaultNet": "no",
                                   "Name": "{}".format(add_vlan_to_vnic.vlan_name),
                                   "Dn": "{}/if-{}".format(dn, add_vlan_to_vnic.vlan_name)}, True)

    HANDLE.CompleteTransaction()


@app.route('/', methods=['GET', 'POST'])
def index():

    index.ip_address = ""
    index.username = ""
    index.password = ""

    index.error = ""

    if request.method == "POST":

        index.ip_address = request.form["ip_address"]
        index.username = request.form["username"]
        index.password = request.form["password"]

        return redirect(url_for('vlans'))

    return render_template('index.html', page_title='Connect to UCS Manager', error=index.error, ip=index.ip_address, username=index.username, password=index.password)


@app.route('/vlans', methods=['GET', 'POST'])
def vlans():

    new_vlan_name = ""

    if request.method == "POST":

        add_vlans.name = request.form["vlan-name"]
        add_vlans.id = request.form["vlan-id"]

        connect()
        add_vlans()
        logout()

        new_vlan_name = add_vlans.name

    return render_template('vlans.html', vlan=current_vlans(), ip=index.ip_address, new_vlan_name=new_vlan_name)


@app.route('/vnics', methods=['GET', 'POST'])
def vnics():

    add_vlan_to_vnic.succes = ""
    add_vlan_to_vnic.vnic_name = ""
    add_vlan_to_vnic.vlan_name = ""

    if request.method == "POST":

        add_vlan_to_vnic.vnic_name = request.form["vnic-name"]
        add_vlan_to_vnic.vlan_name = request.form["vlan-name"]

        connect()

        current_orgs()
        add_vlan_to_vnic()

        add_vlan_to_vnic.succes = "True"
        logout()

    return render_template('vnics.html', vnic=current_vnic_templates(), ip=index.ip_address, vlan=current_vlans(), success=add_vlan_to_vnic.succes, vnic_name=add_vlan_to_vnic.vnic_name, vlan_name=add_vlan_to_vnic.vlan_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

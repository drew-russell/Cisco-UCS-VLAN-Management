"""
A Python CLI interface that utilizes the Cisco UCS SDK to:

- Connect to a UCSM domain
- View and Add VLANs
- Add a VLAN to a vNIC

Please note that there is very little error handling present so
proceed accordingly.

"""


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


def connect():
    """ Establish a connection to the UCS Domain """

    HANDLE.Login(IP_ADDRESS, USERNAME, PASSWORD)


def current_vlans():
    """ Get a list of all current VLANs """

    current_vlans.list = {}

    obj = HANDLE.GetManagedObject(None, FabricVlan.ClassId())

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Name":
                    vlan_name = mo.getattr(prop)

                if str(prop) == "Id":
                    vlan_id = mo.getattr(prop)

            current_vlans.list.update({vlan_name: vlan_id})


def add_vlans():
    """ Create new VLANs on UCS. """

    print ''
    add_vlans.confirm_new_vlan = raw_input(
        'Would you like to add a new VLAN? (yes/no): ')
    while add_vlans.confirm_new_vlan not in ['yes', 'y', 'no', 'n']:
        print ''
        print '*** Error: Please enter either "yes" or "no". ***'
        print ''
        add_vlans.confirm_new_vlan = raw_input(
            'Would you like to add a new VLAN? (yes/no): ')

    if add_vlans.confirm_new_vlan not in ['no' or 'n']:

        print
        add_vlans.vlan_name = raw_input('Enter the VLAN Name: ')
        vlan_id = raw_input('Enter the VLAN ID: ')

        obj = HANDLE.GetManagedObject(None, None, {"Dn": "fabric/lan"})
        HANDLE.AddManagedObject(obj, "fabricVlan", {"DefaultNet": "no", "PubNwName": "", "Dn": "fabric/lan/net-{}".format(add_vlans.vlan_name), "PolicyOwner": "local",
                                                    "CompressionType": "included", "Name": "{}".format(add_vlans.vlan_name), "Sharing": "none", "McastPolicyName": "", "Id": "{}".format(vlan_id)})

        current_vlans()
        for key, value in current_vlans.list.items():
            if add_vlans.vlan_name in str(key):
                print ''
                print 'The following VLAN has been created: '
                print ''
                print '- ' + key + ' (' + value + ')'


def current_vnic_templates():
    """ Get a list of current vNICs in UCS """

    current_vnic_templates.list = []

    obj = HANDLE.GetManagedObject(None, VnicLanConnTempl.ClassId())

    if obj != None:
        for mo in obj:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if str(prop) == "Name":
                    vnic_template_name = mo.getattr(prop)

            current_vnic_templates.list.append(vnic_template_name)


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

    print
    add_vlan_to_vnic.vnic_name = raw_input('vNIC Template Name: ')

    print ''
    obj = HANDLE.GetManagedObject(None, VnicLanConnTempl.ClassId(), {
                                  VnicLanConnTempl.RN: "lan-conn-templ-{}".format(add_vlan_to_vnic.vnic_name)})

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

    vnic_obj = HANDLE.GetManagedObject(
        None, None, {"Dn": "{}".format(organization)})

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

    mo_1 = HANDLE.AddManagedObject(mo, "vnicEtherIf", {
                                   "DefaultNet": "no",
                                   "Name": "{}".format(add_vlans.vlan_name),
                                   "Dn": "{}/if-{}".format(dn, add_vlans.vlan_name)}, True)

    HANDLE.CompleteTransaction()


ssl_workaround()

IP_ADDRESS = ""
USERNAME = ""
PASSWORD = ""


HANDLE = UcsHandle()


HANDLE = UcsHandle()


connect()


print ''
print "Cisco UCS Manager VLAN Management"
print ''


print 'Current VLANs:'
current_vlans()
print ''
for name, ID in current_vlans.list.iteritems():
    print '- ' + name + ' (' + ID + ')'

add_vlans()

if add_vlans.confirm_new_vlan not in ['no' or 'n']:

    print ''
    print 'Current vNIC Templates: '
    print ''
    current_vnic_templates()
    for name in current_vnic_templates.list:
        print '- ' + name

    print ''
    confirm_add_vlan = raw_input(
        "Would you like to add the " + '"' + add_vlans.vlan_name + '"' + " VLAN to a vNIC template? (yes/no): ")
    while confirm_add_vlan not in ['yes', 'y', 'no', 'n']:
        print ''
        print '*** Error: Please enter either "yes" or "no". ***'
        print ''
        cconfirm_add_vlan = raw_input(
            "Would you like to add the " + '"' + add_vlans.vlan_name + '"' + " VLAN to a vNIC template? (yes/no): ")

    if confirm_add_vlan not in ['no' or 'n']:

        current_orgs()
        add_vlan_to_vnic()
        print ("The " + '"' + add_vlans.vlan_name + '"' + " VLAN has been added to " '"' +
               add_vlan_to_vnic.vnic_name + '"' + " vNIC template.")
        print
    else:
        print


HANDLE.Logout()

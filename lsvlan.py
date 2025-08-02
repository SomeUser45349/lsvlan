import scapy.all as s
import argparse
import concurrent.futures

#Set Scapy verbosity to 0
s.conf.verb = 0

#Define Arguments
parser = argparse.ArgumentParser(description="Finds all available VLANs via DHCP. Example: sudo python3 lsvlan.py -i eth0",prog='lsvlan.py')
parser.add_argument('-i','--interface',help='interface to send the traffic on', required=True)
parser.add_argument('-t','--timeout',help='DHCP request timeout value, default - 1 second',default=1)
parser.add_argument('-s','--start_vlan',help='define VLAN from which to start the scan',default=1)
parser.add_argument('-e','--end_vlan',help='define VLAN to which to end the scan',default=4094)
parser.add_argument('--threads',help='define the amount of threads to be used, default - 10',default=10)
parser.add_argument('--only_untagged',help='only send a DHCP request on the untagged VLAN',action='store_true')
parser.add_argument('--dump_options',help='print all received DHCP options',action='store_true')
args = parser.parse_args()


#Sanity checks
try:
    start_vlan = int(args.start_vlan)
    end_vlan = int(args.end_vlan)
    timeout_value = int(args.timeout)
    threads = int(args.threads)
except:
    print("Given VLAN, thread or timeout value must be an integer")
    exit()



def check_interface(interface):
    valid_interfaces = s.get_if_list()

    if args.interface in valid_interfaces:
        return
    else:
        print(f"Interface {interface} not found. Valid interfaces:\n{valid_interfaces}")
        exit()


def parse_dhcp_response(received):
    print(f"Offered address: {received[s.BOOTP].yiaddr}")

    #Parse the DHCP options
    for x in range (0,len(received[s.DHCP].options)):
        match received[s.DHCP].options[x][0]:
            case "server_id":
                print(f"DHCP server: {received[s.DHCP].options[x][1]}")
            case "subnet_mask":
                print(f"Subnet mask: {received[s.DHCP].options[x][1]}")
            case "router":
                print(f"Router: {received[s.DHCP].options[x][1]}")
            case "name_server":
                print(f"DNS: {received[s.DHCP].options[x][1]}")
    
    if args.dump_options:
        print(f"All of the received options: {received[s.DHCP].options}")
    print("\n")


def send_dhcp_request(vlan_id):
    ans, unans = s.srp(s.Ether(dst="ff:ff:ff:ff:ff:ff")/s.Dot1Q(vlan=vlan_id)/s.IP(src="0.0.0.0",dst="255.255.255.255")/s.UDP(sport=68,dport=67)/s.BOOTP()/s.DHCP(options=[("message-type","discover"),"end"]),iface = args.interface,timeout=timeout_value)
    if len(ans) != 0:
        print(f"VLAN - {vlan_id}")
        for sent, received in ans:
            parse_dhcp_response(received)


def find_vlans(interface):
    print("[[VLANS FOUND]]")
    s.conf.checkIPaddr = False 

    #Check untagged VLAN
    ans, unans = s.srp(s.Ether(dst="ff:ff:ff:ff:ff:ff")/s.IP(src="0.0.0.0",dst="255.255.255.255")/s.UDP(sport=68,dport=67)/s.BOOTP()/s.DHCP(options=[("message-type","discover"),"end"]),iface = interface,timeout=timeout_value) 
    if len(ans) != 0:
        print("VLAN - UNTAGGED")
        for sent, received in ans:
            parse_dhcp_response(received)

    #Check tagged VLANs
    if args.only_untagged:
        exit()    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(send_dhcp_request, x) for x in range(start_vlan, end_vlan+1)]
    


#Sanity checks
if start_vlan < 1 or start_vlan > 4094 or end_vlan < 1 or end_vlan > 4094:
    print("Invalid VLAN range. Valid VLAN range 1 - 4094")
    exit()

if threads < 1 or threads > 16:
    print("Invalid thread count. Valid thread count 1 - 16")
    exit()


check_interface(args.interface)
find_vlans(args.interface)

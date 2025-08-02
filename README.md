# lsvlan
A small tool written in Python to enumerate available VLANs and IP ranges via DHCP requests.

usage: lsvlan [-h] -i INTERFACE [-t TIMEOUT] [-s START_VLAN] [-e END_VLAN] [--threads THREADS] [--only_untagged] [--dump_options]

Finds all available VLANs via DHCP. Example: sudo python3 lsvlan -i eth0

options:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        interface to send the traffic on
  -t TIMEOUT, --timeout TIMEOUT
                        DHCP request timeout value, default - 1 second
  -s START_VLAN, --start_vlan START_VLAN
                        define VLAN from which to start the scan
  -e END_VLAN, --end_vlan END_VLAN
                        define VLAN to which to end the scan
  --threads THREADS     define the amount of threads to be used, default - 10
  --only_untagged       only send a DHCP request on the untagged VLAN
  --dump_options        print all received DHCP options

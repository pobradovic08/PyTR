**Still under development and not functional!**

# PyTR — Python DNS PTR updater [![Build Status](https://travis-ci.org/pobradovic08/dns-update.svg?branch=master)](https://travis-ci.org/pobradovic08/dns-update) [![cc](https://codeclimate.com/github/pobradovic08/dns-update/badges/coverage.svg)](https://codeclimate.com/github/pobradovic08/dns-update/coverage)

>This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
>
>This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
>
>You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


PyTR collects interface (IP address, IF-MIB::ifName)
details for a given list of devices, checks and updates PTR RR for those
IP addresses. PyTR features [_Connectors_](#connectors) for importing and exporting list of
devices or existing PTR lists from/to 3rd party data sources. Currently
implemented connectors:
- Observium (requires MySQL database access)
- Local SQLite database

It features flexible JSON configuration file for simple implementation
of rules for:
- Ignoring devices or/and interfaces (regexp matching of hostname or `ifName`)
- Ignoring IP addresses (matching prefixes in CIDR notation — `192.0.2.0/24`)
- Default and per host community strings (regexp matching of hostname)
- List of name servers to query
- List of name servers to update
- List of domain names to build FQDN with
- Connector configuration

Resulting PTR has a form of:

`hostname-ifname.domain.example`

## Device PTR check
`device_ptr_check` is a Python script that displays info about specific device.
It shows a list of interfaces that have IP addresses configured, existing
PTR, IP address and a current status of PTR.
~~~~
╒═══════════════════════════════════════════════════════════════════════════════════════════════╕
│ Device:       r-sc-3.domain.example                                                           │
│ Interfaces:   10                                                                              │
│ IP addresses: 10                                                                              │
╞═══════════════════════════════════════════════════════════════════════════════════════════════╡
│ifName                     PTR                                          IP address             │
╞═══════════════════════════════════════════════════════════════════════════════════════════════╡
│MgmtEth0/RSP0/CPU0/0     ┌ r-sc-3.oobm.domain.example                   192.0.2.210            │
│                         └─► r-sc-3-mg0-0-0-0..domain.example                                  │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI439                   ┌ r-sc-2-vl410.domain.example                  192.0.2.177            │
│                         └─► r-sc-3-bvi439.domain.example                                      │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI63                    i r-sc-3-bvi63.domain.example                  172.28.0.1             │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI64                    ┌ dynamic-192-0-2-1.domain.example             192.0.2.1              │
│                         └─► r-sc-3-bvi64.domain.example                                       │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI65                    i r-sc-3-bvi65.domain.example                  10.137.148.1           │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│Loopback0                ● r-sc-3.domain.example                        192.0.2.249            │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI67                    i r-sc-3-bvi67.domain.example                  172.28.16.1            │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI68                    ■ r-sc-3-bvi68.domain.example                  192.0.2.193            │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│BVI69                    i r-sc-3-bvi69..domain.example                 10.137.47.1            │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│Bundle-Ether1.230        ┌ r-sc-4-gi0-0-230.domain.example              192.0.2.121            │
│                         └─► r-sc-3-bu1-230.domain.example                                     │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
╘═══════════════════════════════════════════════════════════════════════════════════════════════╛
~~~~

## Batch PTR update
`dns-update.py` is a Python script that loads devices and PTRs from external sources
(via Connectors). It merges the list of PTRs loaded through Connectors with
the PTR list it obtained from each device.
~~~~
Loaded connectors: ObserviumConnector
Loaded 10 device(s) from 1 connector(s)
Fetching data from devices:
│▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌│ 100%
╒═════════════════════════════════════╤══════╤════════╤════════╤══════════╤══════════╤══════════╕
│Device                               │ OK   │ UPDATE │ CREATE │ NO AUTH  │ IGNORED  │ UNKNOWN  │
╞═════════════════════════════════════╪══════╪════════╪════════╪══════════╪══════════╪══════════╡
│dhcp.domain.example                  │ 1    │ 0      │ 0      │ 0        │ 1        │ 0        │
│imap.different-domain.example        │ 0    │ 2      │ 1      │ 0        │ 1        │ 0        │
│mtik-pb-2.domain.example             │ 1    │ 2      │ 0      │ 0        │ 0        │ 0        │
│edge-nv-1.domain.example             │ 5    │ 0      │ 0      │ 1        │ 1        │ 0        │
│cns2.domain.example                  │ 1    │ 1      │ 0      │ 0        │ 1        │ 0        │
│olt-sc-1.domain.example              │ 2    │ 0      │ 0      │ 0        │ 0        │ 0        │
│r-kp-1.domain.example                │ 11   │ 1      │ 1      │ 0        │ 0        │ 0        │
│asa-bg-1.domain.example              │ 2    │ 0      │ 0      │ 0        │ 0        │ 0        │
│avas.domain.example                  │ 1    │ 0      │ 0      │ 0        │ 1        │ 0        │
│asa-bo-2.domain.example              │ 2    │ 0      │ 0      │ 0        │ 0        │ 0        │
╘═════════════════════════════════════╧══════╧════════╧════════╧══════════╧══════════╧══════════╛
~~~~

## General information
### Code structure
Basic structure looks like this:
~~~~
├── classes
│   ├── connectors
│   └── output
└── test
    ├── configuration_examples
    ├── connectors
    ├── output
    └── system
    
~~~~

- `classes/` - main program classes
- `classes/connectors/` - Autoloaded Connector modules
- `classes/output/` - Output classes
- `test` - Unit tests
- `test/configuration_examples` - Config files for unit tests
- `test/connectors` - Connectors unit tests
- `test/output` - Output modules unit tests
- `test/system` - System configuration files used for testing (snmpd, named)

### PTR statuses
|Status|Value|Description|
|------|:-----:|-----------|
|`STATUS_UNKNOWN` | `0` | PTR status not checked yet |
|`STATUS_OK` | `1` | PTR exists and is equal to generated PTR
|`STATUS_NOT_UPDATED` | `2` | PTR exists but differs from generated PTR
|`STATUS_NOT_CREATED` | `3` | PTR doesn't exists
|`STATUS_NOT_AUTHORITATIVE` | `4` | None of the configured DNS servers are authoritative for this PTR zone
|`STATUS_IGNORED` | `5` | Not checked. Device, interface or IP address are on ignore list

## Connectors
Each connector has it's own subdirectory in `classes/connectors/`. Directory, file and class naming should follow
simple rules to make autoloading connectors easier.
Autoloader will go through all directories in `classes/connectors/` and try to find a file with 
a filename of `{dir_name}_connector.py` that has class `{Dir_name}Connector` defined in it.

For connector named `example` structure would look like:
 ~~~~
├── classes
│   └── connectors
│       └── example
│           ├── __init__.py
│           └── example_connector.py
└── test
    └── connectors
        └── example
            └── test_example_connector.py
~~~~
with a class named `ExampleConnector`.

### Connector methods
All connectors should be instances of `BaseConnector` class and override all it's methods, needed or not.
Those methods are:
- `load_devices` - Returns a list of device hostnames
- `load_ptrs` - Returns a dictionary of Ptr objects - `{ 'ip_address': Ptr, ... }` 
- `save_ptr` - Save a single Ptr object
- `save_ptrs` - Save a dictionary of Ptr objects

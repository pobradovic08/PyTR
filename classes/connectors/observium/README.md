# PyTR — Observium connector

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

`ObserviumConnector` uses direct access to Observium database
to fetch hostnames of devices that are not disabled.

## Configuration
You are required to provide connection parameters for Observium MySQL database
in configuration for `ObserviumConnector`

```json
{
  "observium": {
    "enabled": true,
    "mysql": {
        "host": "<hostname>",
        "user": "<username>",
        "passwd": "<password>",
        "db": "observium"
    }
  }
}
```

`ObserviumConnector` is enabled by default.

## `load_devices` method
Devices are selected from `devices` table using following query:

```sql
SELECT `hostname` FROM `devices` WHERE `disabled` = 0
```

## Other methods
Other methods are not required and are not used.

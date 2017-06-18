# PyTR — SQLite connector

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

`SqliteConnector` uses SQLite database for storing and retreiving PTRs.

## Configuration
You are required to provide database filename in configuration for `SqliteConnector`

```json
{
  "sqlite": {
    "db": "sqlite.sql",
    "enabled": true
  }
}
```

`SqliteConnector` is enabled by default.

## Database structure


| Field name | Type | Null | Key | Comment |
| ---: | ---: | :---: | :---: | ---- |
| `ip_address`| INTEGER | **No** | Primary | IP address stored as long integer |
| `hostname` | VARCHAR | Yes | | FQDN of a device|
| `if_name` | VARCHAR | Yes | | Interface name |
| `ptr` | VARCHAR | Yes | | PTR |
| `ptr_zone` | VARCHAR | **No** | | `in-addr.arpa` zone | 
| `status` | INTEGER | **No** | | PTR status |
| `insert_time` | INTEGER | Yes | | Record insert/update time |

## Implemented methods
Connector has `load_ptrs`, `save_ptr`, `save_ptrs` methods implemented.
Other methods are not used.
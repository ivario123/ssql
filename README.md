
# SSql

A simple SQL wrapper for python that allows you to connect to a database using ssh tunneling.

## Installation

```bash
# From the folder
pip install .
```
# Usage

```python
from ssql import SSql

ssh_cfg = {
    "host": "ssh.example.com",
    "port": 22,
    "username": "user",
    "password": "password",
    # or these two
    "key_file": "/path/to/key",
    "key_pass": "key_pass"
}

mysql_cfg = {
    "host": "localhost",
    "port": 3306,
    "user": "user
    "password": "password",
}


# Create a new SSql object
# Automatically creates a tunnel and connects to the database
ssql = SSql(ssh_cfg, mysql_cfg)
# Get the connection and create a cursor
with sql as (conn, cursor):
    cursor.execute("SELECT * FROM table")
    print(cursor.fetchall())
    # Cursor is dropped here
# Close connection
ssql.close()
```

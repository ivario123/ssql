# SSql

A simple SQL wrapper for python that allows you to connect to a database using ssh tunneling.

## Installation

```bash
pip install GIT+https://github.com/ivario123/ssql
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
    "user": "user",
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

## Decorator

```python
# This assumes a corectly configured ssql object
from ssql_builder import SSqlBuilder as ssql_builder

@ssql_builder.select(ssql, table_name="PRODUCT", select_fields=["ProductName", "ProductDescription", "Price", "Inventory", "Image", "SN"])
def get_item_by_name(ProductName, sql_query=None, connection=None, cursor=None):
    """
    Get an item by name
    """
    cursor.execute(
        sql_query, (ProductName,))
    result = cursor.fetchall()
    print(result)
```

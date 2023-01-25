"""
Exports the SSql class

## Classes
### SSql
Wraps the mysql.connector and sshtunnel libraries to provide a simple interface for connecting to a mysql database through an ssh tunnel.
"""
import sshtunnel
import mysql.connector
from configparser import ConfigParser


# Set up mysql parameters
def get_tunnel(ssh_cfg, mysql_cfg) -> sshtunnel.SSHTunnelForwarder:
    """
    Returns an sshtunnel.SSHTunnelForwarder object
    """
    if "key_file" in ssh_cfg and "pass" in ssh_cfg:
        raise ValueError(
            "The ssh_cfg dictionary can't contain both a key_file and a pass")

    if "key_file" in ssh_cfg:
        return sshtunnel.SSHTunnelForwarder(
            (ssh_cfg["host"], ssh_cfg["port"]),
            ssh_username=ssh_cfg["user"],
            ssh_pkey=ssh_cfg["key_file"],
            ssh_private_key_password=ssh_cfg["key_pass"] if "key_pass" in ssh_cfg else None,
            remote_bind_address=(mysql_cfg["host"], mysql_cfg["port"])
        )

    return sshtunnel.SSHTunnelForwarder(
        (ssh_cfg["host"], ssh_cfg["port"]),
        ssh_username=ssh_cfg["user"],
        ssh_password=ssh_cfg["pass"],
        remote_bind_address=(mysql_cfg["host"], mysql_cfg["port"])
    )


def connect(tunnel: sshtunnel.SSHTunnelForwarder, mysql_cfg):
    """
    Returns a mysql.connector.connect object
    """
    return mysql.connector.connect(
        user=mysql_cfg["user"],
        password=mysql_cfg["pass"],
        host=mysql_cfg["host"],
        port=tunnel.local_bind_port,
        database=mysql_cfg["database"]
    )


class SSql:
    """
    # A class to handle ssh tunneling and mysql connections
    ## Parameters
    ### ssh_cfg : dict
        A dictionary containing the ssh parameters
        - host: The ssh host
        - user: The ssh user name
        - pass, optional, mutually exclusive with key_file: The ssh password ,needed if the key_file is not passed
        - port: The ssh port
        - key_file, optional, mutually exclusive with pass: The ssh key file
        - key_pass, optional: The ssh key password, needed if the key_file is passed

    ### mysql_cfg : dict
        A dictionary containing the mysql parameters
        - host: The mysql host
        - user: The mysql user name
        - pass: The mysql password
        - port: The mysql port
        - database: The mysql database to connect to
    """

    def __init__(self, ssh_cfg, mysql_cfg):
        """
        Creates a new SSql object
        """
        # Set up ssh tunnel
        self.tunnel = get_tunnel(ssh_cfg, mysql_cfg)
        self.tunnel.start()
        # Connect to mysql
        self.conn = connect(self.tunnel, mysql_cfg)

    def commit(self):
        """
        Commits the current transaction
        """

        self.conn.commit()

    def __enter__(self):
        """
        Returns a sql cursor
        """

        self.cursor = self.conn.cursor()
        return (self.conn, self.cursor)

    def __exit__(self, exc, *_):
        """
        Closes the sql cursor
        """

        if exc:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()

        self.cursor = None

    def stop(self):
        """
        Closes the ssh tunnel
        """
        self.conn.close()
        self.tunnel.stop()
        self.cursor = None
        self.tunnel = None
        self.conn = None


if __name__ == "__main__":
    # Read cfg files
    cfg = ConfigParser()
    cfg.read("cfg/config.cfg")

    secrets = ConfigParser()
    secrets.read("secrets/keys.cfg")

    # Set up ssh parameters
    ssh_cfg = {
        "host": cfg["mysql"]["ssh_host"],
        "user": secrets["ssh"]["user_name"],
        "pass": secrets["ssh"]["password"],
        "port": int(cfg["mysql"]["ssh_port"])
    }

    mysql_cfg = {
        "host": cfg["mysql"]["mysql_host"],
        "user": secrets["mysql"]["user_name"],
        "pass": secrets["mysql"]["password"],
        "port": int(cfg["mysql"]["mysql_port"])
    }
    ssql = SSql(ssh_cfg, mysql_cfg)
    with ssql as (conn, curs):
        curs.execute('SHOW DATABASES')
        print(curs.fetchall())
    ssql.stop()

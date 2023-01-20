
import sshtunnel
import mysql.connector
from configparser import ConfigParser

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

# Set up mysql parameters


def get_tunnel(ssh_cfg, mysql_cfg) -> sshtunnel.SSHTunnelForwarder:
    return sshtunnel.SSHTunnelForwarder(
        (ssh_cfg["host"], ssh_cfg["port"]),
        ssh_username=ssh_cfg["user"],
        ssh_password=ssh_cfg["pass"],
        remote_bind_address=(mysql_cfg["host"], mysql_cfg["port"])
    )


def connect(tunnel: sshtunnel.SSHTunnelForwarder, mysql_cfg):
    return mysql.connector.connect(
        user=mysql_cfg["user"],
        password=mysql_cfg["pass"],
        host=mysql_cfg["host"],
        port=tunnel.local_bind_port,
    )


class SSql:
    def __init__(self, ssh_cfg, mysql_cfg):
        """
        A valid ssh cfg contains a 
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

    def __exit__(self, *_):
        """
        Closes the sql cursor
        """
        # Commit the transaction before closing cursor
        self.conn.commit()
        self.cursor.close()

    def stop(self):
        self.conn.close()
        self.tunnel.stop()


ssql = SSql(ssh_cfg, mysql_cfg)
with ssql as (conn, curs):
    curs.execute('SHOW DATABASES')
    print(curs.fetchall())

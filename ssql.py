
import sshtunnel
import mysql.connector
from configparser import ConfigParser

# Read cfg files
cfg = ConfigParser()
cfg.read("cfg/config.cfg")

secrets = ConfigParser()
secrets.read("secrets/keys.cfg")


# Set up ssh parameters
ssh_host = cfg["mysql"]["ssh_host"]
ssh_user = secrets["ssh"]
ssh_password = secrets["ssh"]["password"]
ssh_port = int(cfg["mysql"]["ssh_port"])

# Set up mysql parameters
mysql_host = cfg["mysql"]["mysql_host"]
mysql_user = secrets["mysql"]["user_name"]
mysql_password = secrets["mysql"]["password"]
mysql_port = int(cfg["mysql"]["mysql_port"])

# Set up ssh tunnel
with sshtunnel.SSHTunnelForwarder(
    (ssh_host, ssh_port),
    ssh_username=ssh_user,
    ssh_password=ssh_password,
    remote_bind_address=(mysql_host, mysql_port)
) as tunnel:
    # Connect to mysql
    connection = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        port=tunnel.local_bind_port,
    )
    cursor = connection.cursor()
    cursor.execute('SHOW DATABASES')
    print(cursor.fetchall())
    cursor.close()

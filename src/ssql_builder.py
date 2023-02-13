from functools import wraps
import inspect
from typing import List
from ssql import SSql
import mysql
from mysql.connector.errors import OperationalError


class SSqlBuilder:
    """
    Provides a safe to use sql wrapper over ssh.

    If the system raises a `OperationalError` the connection will be reset
    """

    def base(ssql: SSql):
        """
        creates the connection and cursor objects and passes them to the function,
        then closes the connection after the function is executed.
        """
        def wrap(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    with ssql as (conn, curs):
                        return func(*args, connection=conn, cursor=curs, **kwargs)
                except OperationalError:
                    # For operational errors we want to reset the connection to the server
                    # and retry
                    ssql.restart()
                    with ssql as (conn, curs):
                        return func(*args, connection=conn, cursor=curs, **kwargs)
            return wrapper
        return wrap

    def insert(ssql: SSql, table_name):
        """
        Builds a simple insert query based on the function arguments.
        """
        def wrap(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                fields = inspect.getfullargspec(func).args[:-3]
                sql_string = f"INSERT INTO {table_name} ({','.join(fields)}) VALUES ({','.join(['%s' for i in fields])});"
                try:
                    with ssql as (conn, curs):
                        return func(*args, sql_query=sql_string,
                                    connection=conn, cursor=curs, **kwargs)
                except OperationalError:
                    # For operational errors we want to reset the connection to the server
                    # and retry
                    ssql.restart()
                    with ssql as (conn, curs):
                        return func(*args, sql_query=sql_string,
                                    connection=conn, cursor=curs, **kwargs)
            return wrapper
        return wrap

    def select(ssql: SSql, table_name: str = "", select_fields: List[str] = []):
        """
        Builds a simple select query based on the function arguments.
        """
        def wrap(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                fields = inspect.getfullargspec(func).args[:-3]
                sql_string = f"SELECT {','.join(select_fields)} FROM {table_name} WHERE {','.join([f'{field} = %s' for field in fields])}; "
                try:
                    with ssql as (conn, curs):
                        return func(*args, sql_query=sql_string,
                                    connection=conn, cursor=curs, **kwargs)
                except OperationalError:
                    # For operational errors we want to reset the connection to the server
                    # and retry
                    ssql.restart()
                    with ssql as (conn, curs):
                        return func(*args, sql_query=sql_string,
                                    connection=conn, cursor=curs, **kwargs)
            return wrapper
        return wrap

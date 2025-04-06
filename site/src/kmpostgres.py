import psycopg2


class RecordInputException(Exception):
    """Invalid data submitted"""
    def __init__(self, message="Invalid Data submitted"):
        self.message = message
        super().__init__(self.message)


class ConnectionException(Exception):
    """Database connection failed"""
    def __init__(self, message="Unable to connect to database"):
        self.message = message
        super().__init__(self.message)


def validate_insert_data(**record_data):
    if type(record_data.get('title')) is not str:
        raise RecordInputException()
    if type(record_data.get('url')) is not str:
        raise RecordInputException()
    if type(record_data.get('description')) is not str:
        raise RecordInputException()
    if type(record_data.get('samaccountname')) is not str:
        raise RecordInputException()
    if type(record_data.get('tags')) is not list:
        raise RecordInputException()
    for tag in record_data.get('tags'):
        if type(tag) is not str:
            raise RecordInputException()

    valid_record = {
        'title': record_data['title'],
        'url': record_data['url'],
        'description': record_data['description'],
        'samaccountname': record_data['samaccountname'],
        'tags': record_data['tags'],
        'reported': []
    }
    return valid_record


def insert_record(conn_params, **record_data):
    """
    Inserts a record into the 'Records' table of the 'knowledgemesh' PostgreSQL database.

    Parameters:
        conn_params (dict): Connection parameters with keys 'host', 'user', 'password', and 'port'.
            Example: {'host': 'localhost', 'user': 'postgres', 'password': 'secret', 'port': 5432}
        **record_data: Arbitrary keyword arguments corresponding to column names and their values.
            Example: name='John Doe', age=30, created_at='2025-03-21' TODO: update this to final payload

    Usage:
        conn_params = {
            'host': 'localhost',
            'user': 'postgres',
            'password': 'yourpassword',
            'port': 5432
        }
        insert_record(conn_params, name='John Doe', age=30, created_at='2025-03-21')
    """
    # Connect to the knowledgemesh database
    try:
        conn = psycopg2.connect(
            dbname=conn_params.get('dbname', "knowledgemesh"),
            user=conn_params.get('user', 'docker'),
            password=conn_params.get('password', 'docker'),
            host=conn_params.get('host', '127.0.0.1'),
            port=conn_params.get('port', 5432)
        )
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        raise ConnectionException()

    cur = conn.cursor()

    # TODO: rebuild this query so that there is data validation on the keys
    # Build the INSERT query dynamically based on the provided record_data
    columns = record_data.keys()
    values = record_data.values()

    query = "INSERT INTO Records ({}) VALUES ({})".format(
        ", ".join(columns),
        ", ".join(["%s"] * len(columns))
    )

    try:
        cur.execute(query, tuple(values))
        conn.commit()
        print("Record inserted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error inserting record:", e)
    finally:
        cur.close()
        conn.close()


def update_record(conn_params, **record_data):
    """
    Updates a record into the 'Records' table of the 'knowledgemesh' PostgreSQL database.

    Parameters:
        conn_params (dict): Connection parameters with keys 'host', 'user', 'password', and 'port'.
            Example: {'host': 'localhost', 'user': 'postgres', 'password': 'secret', 'port': 5432}
        **record_data: Arbitrary keyword arguments corresponding to column names and their values.
            Example: name='John Doe', age=30, created_at='2025-03-21'  TODO: update this to final payload

    Usage:
        conn_params = {
            'host': 'localhost',
            'user': 'postgres',
            'password': 'yourpassword',
            'port': 5432
        }
        update_record(conn_params, name='John Doe', age=30, created_at='2025-03-21')
    """
    # Connect to the knowledgemesh database
    try:
        conn = psycopg2.connect(
            dbname=conn_params.get('dbname', "knowledgemesh"),
            user=conn_params.get('user', 'docker'),
            password=conn_params.get('password', 'docker'),
            host=conn_params.get('host', '127.0.0.1'),
            port=conn_params.get('port', 5432)
        )
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        raise ConnectionException()

    cur = conn.cursor()

    query = """
        UPDATE Records
        SET title         = %s,
            description   = %s,
            url           = %s,
            tags          = %s,
            updated       = CURRENT_TIMESTAMP
        WHERE id = %s
        AND samaccountname = %s;
    """
    params = (
        record_data['title'],
        record_data['description'],
        record_data['url'],
        record_data['tags'],
        record_data['id'],
        record_data['samaccountname']
    )

    try:
        cur.execute(query, params)
        conn.commit()
        print("Record inserted successfully.")
        success = True
    except Exception as e:
        conn.rollback()
        print("Error inserting record:", e)
        success = False
    finally:
        cur.close()
        conn.close()
        return success


def delete_record(conn_params, **record_data):
    """
    Updates a record into the 'Records' table of the 'knowledgemesh' PostgreSQL database.

    Parameters:
        conn_params (dict): Connection parameters with keys 'host', 'user', 'password', and 'port'.
            Example: {'host': 'localhost', 'user': 'postgres', 'password': 'secret', 'port': 5432}
        **record_data: Arbitrary keyword arguments corresponding to column names and their values.
            Example: name='John Doe', age=30, created_at='2025-03-21'  TODO: update this to final payload

    Usage:
        conn_params = {
            'host': 'localhost',
            'user': 'postgres',
            'password': 'yourpassword',
            'port': 5432
        }
        update_record(conn_params, name='John Doe', age=30, created_at='2025-03-21')
    """
    # Connect to the knowledgemesh database
    try:
        conn = psycopg2.connect(
            dbname=conn_params.get('dbname', "knowledgemesh"),
            user=conn_params.get('user', 'docker'),
            password=conn_params.get('password', 'docker'),
            host=conn_params.get('host', '127.0.0.1'),
            port=conn_params.get('port', 5432)
        )
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        raise ConnectionException()

    cur = conn.cursor()

    query = (
        "DELETE FROM Records"
        f"  WHERE id = {record_data['id']}"
        f"  AND samaccountname = '{record_data['samaccountname']}';"
    )

    try:
        cur.execute(query)
        conn.commit()
        print("Record deleted successfully.")
        success = True
    except Exception as e:
        conn.rollback()
        print("Error deleting record:", e)
        success = False
    finally:
        cur.close()
        conn.close()
        return success

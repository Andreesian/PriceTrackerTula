import psycopg2
from typing import List, Tuple, Optional

def create_connection(database: str, user: str, password: str, host: str, port: str) -> psycopg2.extensions.connection:
    return psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

def close_connection(connection: psycopg2.extensions.connection):
    connection.close()

def add_user(connection: psycopg2.extensions.connection, id_user: int, nickname: str, request_ids: Optional[List[int]] = None):
    request_ids = request_ids or []
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sell_bot.users (id_user, nickname, request_id) VALUES (%s, %s, %s)", (id_user, nickname, request_ids))
        connection.commit()

def add_request(connection: psycopg2.extensions.connection, id_request: int, product_name: str, update_time: str, price_history: List[int], url_id: int):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sell_bot.requests (id_request, product_name, update_time, price_history, url_id) VALUES (%s, %s, %s, %s, %s)",
                       (id_request, product_name, update_time, price_history, url_id))
        connection.commit()

def add_url(connection: psycopg2.extensions.connection, id_url: int, url: str, short_name: str):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sell_bot.urls (id_url, url, short_name) VALUES (%s, %s, %s)", (id_url, url, short_name))
        connection.commit()

def get_user_by_id(connection: psycopg2.extensions.connection, id_user: int) -> Optional[Tuple[int, str, List[int]]]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_user, nickname, request_id FROM sell_bot.users WHERE id_user = %s", (id_user,))
        result = cursor.fetchone()
    return result

def get_request_by_id(connection: psycopg2.extensions.connection, id_request: int) -> Optional[Tuple[int, str, str, List[int], int]]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_request, product_name, update_time, price_history, url_id FROM sell_bot.requests WHERE id_request = %s", (id_request,))
        result = cursor.fetchone()
    return result

def get_url_by_id(connection: psycopg2.extensions.connection, id_url: int) -> Optional[Tuple[int, str, str]]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_url, url, short_name FROM sell_bot.urls WHERE id_url = %s", (id_url,))
        result = cursor.fetchone()
    return result

def update_user(connection: psycopg2.extensions.connection, id_user: int, new_nickname: Optional[str] = None, new_request_ids: Optional[List[int]] = None):
    with connection.cursor() as cursor:
        if new_nickname:
            cursor.execute("UPDATE sell_bot.users SET nickname = %s WHERE id_user = %s", (new_nickname, id_user))
        if new_request_ids is not None:
            cursor.execute("UPDATE sell_bot.users SET request_id = %s WHERE id_user = %s", (new_request_ids, id_user))
        connection.commit()

def update_request(connection: psycopg2.extensions.connection, id_request: int, new_product_name: Optional[str] = None, new_update_time: Optional[str] = None,
                   new_price_history: Optional[List[int]] = None, new_url_id: Optional[int] = None):
    with connection.cursor() as cursor:
        if new_product_name:
            cursor.execute("UPDATE sell_bot.requests SET product_name = %s WHERE id_request = %s", (new_product_name, id_request))
        if new_update_time:
            cursor.execute("UPDATE sell_bot.requests SET update_time = %s WHERE id_request = %s", (new_update_time, id_request))
        if new_price_history is not None:
            cursor.execute("UPDATE sell_bot.requests SET price_history = %s WHERE id_request = %s", (new_price_history, id_request))
        if new_url_id:
            cursor.execute("UPDATE sell_bot.requests SET url_id = %s WHERE id_request = %s", (new_url_id, id_request))
        connection.commit()

def update_url(connection: psycopg2.extensions.connection, id_url: int, new_url: Optional[str] = None, new_short_name: Optional[str] = None):
    with connection.cursor() as cursor:
        if new_url:
            cursor.execute("UPDATE sell_bot.urls SET url = %s WHERE id_url = %s", (new_url, id_url))
        if new_short_name:
            cursor.execute("UPDATE sell_bot.urls SET short_name = %s WHERE id_url = %s", (new_short_name, id_url))
        connection.commit()

def delete_user(connection: psycopg2.extensions.connection, id_user: int):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sell_bot.users WHERE id_user = %s", (id_user,))
        connection.commit()

def delete_request(connection: psycopg2.extensions.connection, id_request: int):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sell_bot.requests WHERE id_request = %s", (id_request,))
        connection.commit()

def delete_url(connection: psycopg2.extensions.connection, id_url: int):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sell_bot.urls WHERE id_url = %s", (id_url,))
        connection.commit()

# Example usage
connection = create_connection("burnoutbotsell", "postgres", "Alesha2109!", "localhost", "5432")

add_user(connection, 1, "JohnDoe")
add_url(connection, 1, "https://example.com/product1", "Product 1")
add_request(connection, 1, "Product 1", "1 day", [100, 110, 120], 1)

user = get_user_by_id(connection, 1)
request = get_request_by_id(connection, 1)
url = get_url_by_id(connection, 1)

print(user)
print(request)
print(url)

update_user(connection, 1, "JaneDoe", null)
update_request(connection, 1, new_update_time="2 days", new_price_history=[100, 105, 110])
update_url(connection, 1, new_short_name="Product 1 - Updated")

user = get_user_by_id(connection, 1)
request = get_request_by_id(connection, 1)
url = get_url_by_id(connection, 1)

print(user)
print(request)
print(url)

delete_user(connection, 1)
delete_request(connection, 1)
delete_url(connection, 1)

close_connection(connection)

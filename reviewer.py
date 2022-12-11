import mysql.connector
import os
from dotenv import load_dotenv

# CONSTANTS
MAX_LEN = 45
# CONSTANTS

def check_table_exists(table_name, cursor):
    stmt = "SHOW TABLES LIKE " + "'" + table_name + "'"
    cursor.execute(stmt)
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False

def exist_in_db(value, attribute, table_name, cursor):
    stmt = "SELECT " + attribute + "\n" + "FROM " + table_name + "\n" + "WHERE " + attribute + " = " + value
    cursor.execute(stmt)
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False

def save_reviewer_to_db(first_name, last_name, cursor):
    insert_stmnt = "INSERT INTO reviewer (first_name, last_name) VALUES (%s, %s)"
    cursor.execute(insert_stmnt, (first_name, last_name))
    stmt = "SELECT reviewer_id\n" + "FROM reviewer\n" +  "ORDER BY reviewer_id " + "DESC"
    cursor.execute(stmt)
    result = cursor.fetchall()
    r = result[0][0]
    return r

def get_full_name(id, cursor):
    stmt = "SELECT " + "first_name, last_name" + "\n" + "FROM " + "reviewer" + "\n" + "WHERE " + "reviewer_id" + " = " + str(id)
    cursor.execute(stmt)
    result = cursor.fetchone()
    return result

def get_film_id_by_name(cursor):
    film_name = input("Enter the film name: ")
    stmt = "SELECT " + "film_id" + "\n" + "FROM " + "film" + "\n" + "WHERE " + "title" + " = " + "'" + str(film_name) + "'"
    cursor.execute(stmt)
    result = cursor.fetchall()
    return result, film_name

def ask_for_film_name(cursor):
    while(True):
        result, film_name = get_film_id_by_name(cursor)
        flag = len(result)
        if flag == 1:
            r = result[0][0]
            return r
        if flag > 1:
            print("There is more than one film with this name")
            stmt = "SELECT " + "film_id, release_year" + "\n" + "FROM " + "film" + "\n" + "WHERE " + "title" + " = " + "'" + str(film_name) + "'"
            cursor.execute(stmt)
            s = cursor.fetchall()
            print(s)
            film_id = input("Enter the film id: ")
            film_id = int(film_id)
            for r in result:
                if film_id == r[0]:
                    return film_id 
            print("Wrong id")   
        elif flag == 0:
            print("The film you entered doesn’t exist in the database, please select another film")

def rate(reviewer_id, film_id, cursor):
    pass

def print_all_ratings(film_id, cursor):
    pass

def name_is_valid(first_name, last_name):
    return len(first_name) <= MAX_LEN and len(last_name) <= MAX_LEN
        

def main():

    # Enables us to get password from .env file
    load_dotenv()

    # Connect to local sakila
    db = mysql.connector.connect(
        user='root',
        password = os.getenv('MYSQL_ROOT_PASSWORD'),
        host='localhost',
        database='sakila'
    )

    # Create a cursor
    cursor = db.cursor()

    db.autocommit = True
    cursor = db.cursor(prepared=True)

    # Check if the rating and reviewer tables exist 

    if not check_table_exists("reviewer", cursor):
        # Reviewer table doesnt exist there for we create it
        cursor.execute("""
        CREATE TABLE reviewer (
        reviewer_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
        first_name VARCHAR(45) NOT NULL,
        last_name VARCHAR(45) NOT NULL
        );
    """)
    if not check_table_exists("rating", cursor):
        # Rating table doesnt exist there for we create it
        cursor.execute("""
            CREATE TABLE rating (
            film_id smallint Unsigned NOT NULL,
            reviewer_id INT NOT NULL,
            rating decimal(2, 1) NOT NULL,
			FOREIGN KEY (film_id) REFERENCES film(film_id),
			FOREIGN KEY (reviewer_id) REFERENCES reviewer(reviewer_id),
            CONSTRAINT rating_id PRIMARY KEY (film_id, reviewer_id)
            );
        """)

    id = input("Please enter your ID: ")
    flag = get_full_name(id, cursor)
    if not flag:
        print("ID does not registered in our system")
        while(True):
            first_name = input("Please enter your first name: ")
            last_name = input("Please enter your last name: ")
            if name_is_valid(first_name, last_name):
                id = save_reviewer_to_db(first_name, last_name, cursor)
                break
    else:  
        first_name, last_name = flag
    print(f"Hello {first_name} {last_name}")
    film_id = ask_for_film_name(cursor)
    rate(id, film_id, cursor)
    print_all_ratings(film_id, cursor)

main()
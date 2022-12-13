import mysql.connector
import os
from dotenv import load_dotenv
from tabulate import tabulate

# -- CONSTANTS -- #
MAX_LEN = 45
FETCHING_LIMIT=100
# -- CONSTANTS -- #

# --------- QUERIES ---------- #
CREATE_RATING_TABLE_Q = """
        CREATE TABLE rating (
                    film_id smallint Unsigned NOT NULL,
                    reviewer_id INT NOT NULL,
                    rating decimal(2, 1) NOT NULL,
                    FOREIGN KEY (film_id) REFERENCES film(film_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                    FOREIGN KEY (reviewer_id) REFERENCES reviewer(reviewer_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                    CONSTRAINT rating_id PRIMARY KEY (film_id, reviewer_id)
                    );
        """
CREATE_REVIEWER_TABLE_Q = """
        CREATE TABLE reviewer (
                    reviewer_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    first_name VARCHAR(45) NOT NULL,
                    last_name VARCHAR(45) NOT NULL
                    );
    """

PRINT_RATINGS_Q = """
        SELECT f.title, CONCAT(r.first_name,' ', r.last_name) AS name, rt.rating
        FROM film f, reviewer r, rating rt
        WHERE rt.reviewer_id = r.reviewer_id AND
	    f.film_id = rt.film_id
    """
# --------- QUERIES ---------- #


# Validate rate
def is_valid(rate):
    try:                                            # Cathces strings
        rate_to_float = float(rate)
    except ValueError:
        print("Invalid Rating")
        return False
    count_after_decimal = rate[::-1].find('.')      # Returns -1 if not found -> case only integer
    if count_after_decimal > 1:                     # If there is more than one number after the decimal point
            print("Invalid Rating")
            return False
    if count_after_decimal == -1:                   # Catches Pure integer
        if int(rate) < 0 or int(rate) > 9:
            print("Invalid Rating")
            return False
    if rate_to_float < 0.0 or rate_to_float > 9.9:  # Check if in range
        print("Invalid Rating")
        return False
    return True


# Checks if a table exists in db
def check_table_exists(table_name, cursor):
    #stmt = "SHOW TABLES LIKE " + "'" + table_name + "'"
    query = f"SHOW TABLES LIKE '{table_name}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False


# Saves reviewer to database
def save_reviewer_to_db(first_name, last_name, cursor):
    insert_query = "INSERT INTO reviewer (first_name, last_name) VALUES (%s, %s)"
    cursor.execute(insert_query, (first_name, last_name))
    select_query="""
        SELECT reviewer_id
        FROM reviewer
        ORDER BY reviewer_id
        DESC
    """
    cursor.execute(select_query)
    result = cursor.fetchall()
    r = result[0][0]
    return r


# Gets the full name of the user by his id.
def get_full_name(id, cursor):
    query = f"""
        SELECT first_name, last_name
        FROM reviewer
        WHERE reviewer_id = '{str(id)}'
    """
    cursor.execute(query)
    result = cursor.fetchone()
    return result


"""
    # Gets film_id by the film title.
    # Returns the film_name that user input, and the 
    # film_id from the database
"""
def get_film_id_by_name(cursor):
    film_name = input("Enter the film name: ")
    query = f"""
        SELECT film_id
        FROM film
        WHERE title = '{film_name}'
    """
    cursor.execute(query)
    result = cursor.fetchall()
    return result, film_name


"""
    Asks the user for a film name he wish to rate.
    If there is only one film with this name -> returns it's film_id
    If there are more than one film with that name -> let's the user pick the film_id
    from a given list of film_id's existing with this film name.
    Finally, if there is no film with that name -> asks for a different name.
"""
def ask_for_film_name(cursor):
    while(True):
        result, film_name = get_film_id_by_name(cursor)
        flag = len(result)
        if flag == 1:
            r = result[0][0]
            return r
        if flag > 1:
            print("There is more than one film with this name")
            query = f"""
                SELECT film_id, release_year
                FROM film
                WHERE title = '{film_name}'
            """
            cursor.execute(query)
            s = cursor.fetchall()
            print(tabulate(s, headers=('Film ID', 'Release Year'), tablefmt='fancy_grid'))
            film_id = input("Enter the film id: ")
            film_id = int(film_id)
            for r in result:
                if film_id == r[0]:
                    return film_id 
            print("Wrong id")   
        elif flag == 0:
            print("The film you entered doesn't exist, please select another film")


# Checks if a given reviewer already rated this film
def already_rated(reviewer_id,film_id, cursor):   
    query = f"""
    SELECT EXISTS(SELECT * 
                  FROM rating 
                  WHERE reviewer_id={str(reviewer_id)} AND
                  film_id={str(film_id)})
    """
    cursor.execute(query)
    s = cursor.fetchone()
    if s[0] == 1:
        return True
    else:
        return False


# Update an existing review left by this reviewer
def update_rate(reviewer_id,film_id, cursor, rate):
    query = f"""
        UPDATE rating 
        SET rating={rate} 
        WHERE reviewer_id={reviewer_id} AND
        film_id={film_id}
    """
    cursor.execute(query)


# Insert new record rate to db.
def insert_rate(reviewer_id,film_id, cursor, rate):
    query = "INSERT INTO rating (film_id, reviewer_id, rating) VALUES (%s,%s,%s)"
    cursor.execute(query,(film_id, reviewer_id, rate))


"""
    Blocking function until user input a valid rate.
    If user already reviewed this fiim -> updates his review, Else
    creates a new record in the rating table.
"""
def rate(reviewer_id, film_id, cursor):
    rate = input("Please enter your rate (1-10): ")
    while not is_valid(rate):
        rate = input("Please enter your rate (1-10): ")
    if already_rated(reviewer_id,film_id, cursor):
        update_rate(reviewer_id,film_id, cursor, rate)
    else:
        insert_rate(reviewer_id,film_id, cursor, rate)


# Prints all ratings in the table up to 100 results
def print_all_ratings(cursor):
    query = PRINT_RATINGS_Q
    cursor.execute(query)
    rows = list()
    current_row = cursor.fetchone()
    i = 0
    # Fetch up to 100 Results
    while current_row != None and i < FETCHING_LIMIT:
        rows.append(current_row)
        current_row = cursor.fetchone()
        i += 1
    print(tabulate(rows, headers=
    ('Film Title', 'Reviewer\'s Name', 'Rate'),tablefmt='fancy_grid'
    ))


# Checks if the user first and last name are valid
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

    # Check if the rating and reviewer tables exist and if not -> creates them
    if not check_table_exists("reviewer", cursor):   
        cursor.execute(CREATE_REVIEWER_TABLE_Q) 
    if not check_table_exists("rating", cursor):
        cursor.execute(CREATE_RATING_TABLE_Q)

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
    print_all_ratings(cursor)

main()
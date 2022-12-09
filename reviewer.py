import mysql.connector
import os
from dotenv import load_dotenv

# CONSTANTS
FILM = "film"
USERS = "users"
UNVALID = True
UNINITIALIZED = -1
MAX_LEN = 45
# CONSTANTS

def exist_in_db(value, table_name):
    pass

def save_user_to_db(id, first_name, last_name):
    pass

def get_firstname(id):
    pass

def get_lastname(id):
    pass

def get_num_of_records(value, table_name):
    pass

def present_films(user_filmname):
    pass

def ask_for_review(user_filmname, film_id):
    pass

def print_all_ratings():
    pass

def is_valid(first_name, last_name):
    return len(first_name) <= MAX_LEN and len(last_name) <= MAX_LEN
        
# Blocking function until we get a valid film name from the user
def ask_for_filmname():
    user_filmname = ""
    film_id = UNINITIALIZED
    while(UNVALID):
        user_filmname = input("Please enter the film name you would like to review: ")
        if not exist_in_db(user_filmname, USERS):
            print("The film youv'e entered does not exist")
            continue
        elif len(get_num_of_records(user_filmname, FILM)) > 2:
            present_films(user_filmname)
            film_id = input("Enter your film id")
            if not exist_in_db(film_id, FILM):
                continue
            else:
                UNVALID = False
    return user_filmname, film_id

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


    id = input("Please enter your ID")

    if not exist_in_db(id, USERS):
        print("ID does not registered in our system")
        while(UNVALID):
            first_name = input("Please enter your first name: ")
            last_name = input("Please enter your last name: ")
            if is_valid(first_name, last_name):
                save_user_to_db(id, first_name, last_name)
                UNVALID = False
        # For later iterations
        UNVALID = True
        
    else:
        first_name = get_firstname(id)
        last_name = get_lastname(id)
        print(f"Hello {first_name} {last_name}")
        user_filmname, film_id = ask_for_filmname()
        ask_for_review(user_filmname, film_id)
        print_all_ratings()

    
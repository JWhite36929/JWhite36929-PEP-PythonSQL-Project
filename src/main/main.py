import csv
import sqlite3
import re

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()


def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users('resources/users.csv')
    load_and_clean_call_logs('resources/callLogs.csv')
    write_user_analytics('resources/userAnalytics.csv')
    write_ordered_calls('resources/orderedCalls.csv')

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.

# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    #regex to validate a name is alpha characters while allowing names such as O'Malley or Dread-Scott
    name_pattern = re.compile(r"^[A-Za-z]+(?:[-'][A-Za-z]+)*$")

    with open(file_path) as file:
        reader = csv.DictReader(file)

        for row in reader:

            # skip rows with too many columns
            if None in row:
                continue
            
            first = row['firstName'].strip()
            last = row['lastName'].strip()

            # skip missing values
            if not first or not last:
                continue

            # skip invalid names
            if not (name_pattern.fullmatch(first) and
                    name_pattern.fullmatch(last)):
                    continue

            cursor.execute(
                "INSERT INTO users (firstName, lastName) VALUES (?, ?)",
                (first, last)
            )
        conn.commit()

# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    phone_pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")
    valid_directions = {"inbound", "outbound"}    

    with open(file_path) as file:
        reader = csv.DictReader(file)

        for row in reader:

            # skip if too many columns
            if None in row:
                continue

            # strip whitesapce
            row = {k: v.strip() for k, v in row.items()}

            # skip if missing values
            if not all(row.values()):
                continue

            # skip if invalid phone number
            if not phone_pattern.fullmatch(row['phoneNumber']):
                continue

            # skip if invalid direction
            if row['direction'] not in valid_directions:
                continue

            # validate numeric field are numeric
            try:
                start = int(row["startTime"])
                end = int(row["endTime"])
                user_id = int(row["userId"])
            except ValueError:
                continue

            cursor.execute(
                """
                INSERT INTO callLogs
                (phoneNumber, startTime, endTime, direction,userId)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row["phoneNumber"],
                    start,
                    end,
                    row["direction"],
                    user_id,
                ),
            )
        conn.commit()

# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):
    cursor.execute("""
        SELECT
            userId,
            AVG(endTime - startTime) as avgDuration,
            COUNT(*) AS numCalls
        FROM callLogs
        GROUP BY userId
        ORDER BY userId
    """)

    with open(csv_file_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["userId", "avgDuration", "numCalls"])

        writer.writerows(cursor.fetchall())
    



# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):

    cursor.execute(
        """
        SELECT
            callId,
            phoneNumber,
            startTime,
            endTime,
            direction,
            userId
        FROM callLogs
        ORDER BY userId, startTime
        """
    )

    with open(csv_file_path, "w") as file:
        writer = csv.writer(file)

        writer.writerow([
            "callId",
            "phoneNumber",
            "startTime",
            "endTime",
            "direction",
            "userId"
        ])

        writer.writerows(cursor.fetchall())

# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()

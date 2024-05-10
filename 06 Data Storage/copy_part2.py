import psycopg2
import time 

# Define database connection parameters
DBname = "postgres"
DBuser = "postgres"
DBpwd = "165833"
TableName = "censusdatastaging"
Datafile = "acs2015_census_tract_data_part2.csv"

# Connect to the database
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    return connection

# Load data using the copy_from function
def load_data_copy_from(conn, datafile):
    with conn.cursor() as cursor:
        print(f"Loading data from file: {datafile}")
        
        # Open the CSV file in read mode
        with open(datafile, 'r') as f:
            # Skip the header row if your CSV file contains headers
            next(f)
            
            start_time = time.time()

            # Use copy_from to load data from CSV file into the target table
            # Specify the null option to handle empty strings as NULL
            cursor.copy_from(f, TableName, sep=',', null='')

            # Calculate elapsed time
            elapsed_time = time.time() - start_time

        print(f"Data loading completed in {elapsed_time:.4f} seconds.")
        # Commit the changes to the database
        conn.commit()

# Main function
def main():
    # Establish a connection to the database
    conn = dbconnect()
    
    # Load data using copy_from
    load_data_copy_from(conn, Datafile)
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()


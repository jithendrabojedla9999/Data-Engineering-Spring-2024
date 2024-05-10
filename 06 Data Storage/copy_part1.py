import psycopg2
import time

# Define the database connection parameters
DBname = "postgres"
DBuser = "postgres"
DBpwd = "165833"
TableName = 'censusdatastaging'  # Load data into the unlogged staging table
Datafile = "acs2015_census_tract_data_part1.csv"  # Path to the data file

# Function to load data using copy_from
def load_data_copy_from(conn, datafile):
    with conn.cursor() as cursor:
        print(f"Loading data from file: {datafile}")
        
        # Open the CSV file in read mode
        with open(datafile, 'r') as f:
            # Skip the header row if your CSV file contains headers
            next(f)
           # Start measuring time
            start_time = time.time()
            # Use copy_from to load data from CSV file into the target table
            cursor.copy_from(f, 'censusdatastaging', sep=',', null='')

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
        
        print(f"Data loading completed in {elapsed_time:.4f} seconds.")
        # Commit the changes to the database
        conn.commit()

# Function to establish the database connection
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    return connection

# Main function
def main():
    # Establish database connection
    conn = dbconnect()
    
    # Load data using copy_from
    load_data_copy_from(conn, Datafile)
    
    # Close the database connection
    conn.close()

# Execute the main function
if __name__ == '__main__':
    main()


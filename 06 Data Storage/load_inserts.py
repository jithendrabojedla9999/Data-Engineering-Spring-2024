# Import necessary libraries
import time
import psycopg2
import argparse
import csv

# Define database connection parameters
DBname = "postgres"
DBuser = "postgres"
DBpwd = "165833"
TableName = 'CensusData'
Datafile = "filedoesnotexist"  # Name of the data file to be loaded
CreateDB = False  # Indicates whether the DB table should be (re)-created

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0  # ENHANCE: handle the null vals
        row['County'] = row['County'].replace('\'','')  # TIDY: eliminate quotes within literals

    ret = f"""
       {row['CensusTract']},            -- CensusTract
       '{row['State']}',                -- State
       '{row['County']}',               -- County
       {row['TotalPop']},               -- TotalPop
       {row['Men']},                    -- Men
       {row['Women']},                  -- Women
       {row['Hispanic']},               -- Hispanic
       {row['White']},                  -- White
       {row['Black']},                  -- Black
       {row['Native']},                 -- Native
       {row['Asian']},                  -- Asian
       {row['Pacific']},                -- Pacific
       {row['Citizen']},                -- Citizen
       {row['Income']},                 -- Income
       {row['IncomeErr']},              -- IncomeErr
       {row['IncomePerCap']},           -- IncomePerCap
       {row['IncomePerCapErr']},        -- IncomePerCapErr
       {row['Poverty']},                -- Poverty
       {row['ChildPoverty']},           -- ChildPoverty
       {row['Professional']},           -- Professional
       {row['Service']},                -- Service
       {row['Office']},                 -- Office
       {row['Construction']},           -- Construction
       {row['Production']},             -- Production
       {row['Drive']},                  -- Drive
       {row['Carpool']},                -- Carpool
       {row['Transit']},                -- Transit
       {row['Walk']},                   -- Walk
       {row['OtherTransp']},            -- OtherTransp
       {row['WorkAtHome']},             -- WorkAtHome
       {row['MeanCommute']},            -- MeanCommute
       {row['Employed']},               -- Employed
       {row['PrivateWork']},            -- PrivateWork
       {row['PublicWork']},             -- PublicWork
       {row['SelfEmployed']},           -- SelfEmployed
       {row['FamilyWork']},             -- FamilyWork
       {row['Unemployment']}            -- Unemployment
    """

    return ret


def initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    parser.add_argument("-c", "--createtable", action="store_true")
    args = parser.parse_args()

    global Datafile
    Datafile = args.datafile
    global CreateDB
    CreateDB = args.createtable

# read the input data file into a list of row strings
def readdata(fname):
    print(f"readdata: reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)
        
        rowlist = []
        for row in dr:
            rowlist.append(row)

    return rowlist

# convert list of data rows into list of SQL 'INSERT INTO ...' commands
def getSQLcmnds(rowlist):
    cmdlist = []
    for row in rowlist:
        valstr = row2vals(row)
        cmd = f"INSERT INTO {TableName} VALUES ({valstr});"
        cmdlist.append(cmd)
    return cmdlist

# connect to the database
def dbconnect():
    connection = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    connection.autocommit = True
    return connection

# create the target table 
# assumes that conn is a valid, open connection to a Postgres database
def createUnloggedTable(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            DROP TABLE IF EXISTS CensusDataStaging;
            CREATE UNLOGGED TABLE CensusDataStaging (
                CensusTract         NUMERIC,
                State               TEXT,
                County              TEXT,
                TotalPop            INTEGER,
                Men                 INTEGER,
                Women               INTEGER,
                Hispanic            DECIMAL,
                White               DECIMAL,
                Black               DECIMAL,
                Native              DECIMAL,
                Asian               DECIMAL,
                Pacific             DECIMAL,
                Citizen             DECIMAL,
                Income              DECIMAL,
                IncomeErr           DECIMAL,
                IncomePerCap        DECIMAL,
                IncomePerCapErr     DECIMAL,
                Poverty             DECIMAL,
                ChildPoverty        DECIMAL,
                Professional        DECIMAL,
                Service             DECIMAL,
                Office              DECIMAL,
                Construction        DECIMAL,
                Production          DECIMAL,
                Drive               DECIMAL,
                Carpool             DECIMAL,
                Transit             DECIMAL,
                Walk                DECIMAL,
                OtherTransp         DECIMAL,
                WorkAtHome          DECIMAL,
                MeanCommute         DECIMAL,
                Employed            INTEGER,
                PrivateWork         DECIMAL,
                PublicWork          DECIMAL,
                SelfEmployed        DECIMAL,
                FamilyWork          DECIMAL,
                Unemployment        DECIMAL
            );  
        """)
        print(f"Created unlogged staging table: CensusDataStaging")

def loadToStaging(conn, icmdlist):
    # Start a transaction
    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows into unlogged staging table")
        start = time.perf_counter()
        
        for cmd in icmdlist:
            cursor.execute(cmd.replace(TableName, 'CensusDataStaging'))  # Load to unlogged staging table
        
        elapsed = time.perf_counter() - start
        print(f'Finished loading into unlogged staging table. Elapsed Time: {elapsed:.4f} seconds')

# Now, create the primary key and index after loading data
    with conn.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {TableName} ADD PRIMARY KEY (CensusTract);")
        cursor.execute(f"CREATE INDEX idx_{TableName}_State ON {TableName}(State);")
        print("Added Primary Key and Index")

def appendData(conn):
    with conn.cursor() as cursor:
        print("Appending data from unlogged staging table to main table")
        cursor.execute(f"""
            INSERT INTO {TableName}
            SELECT * FROM CensusDataStaging;
        """)
        print("Finished appending data from unlogged staging table to main table")

def load(conn, icmdlist):
    loadToStaging(conn, icmdlist)  # Load data to unlogged staging table
    appendData(conn)  # Append data from unlogged staging table to main table

    # Create primary key and index on the main table after appending data
    with conn.cursor() as cursor:
        print(f"Creating primary key and index on {TableName}")
        cursor.execute(f"ALTER TABLE {TableName} ADD PRIMARY KEY (CensusTract);")
        cursor.execute(f"CREATE INDEX idx_{TableName}_State ON {TableName}(State);")
        print(f"Created primary key and index on {TableName}")

def main():
    initialize()
    conn = dbconnect()
    rlis = readdata(Datafile)
    cmdlist = getSQLcmnds(rlis)

    if CreateDB:
        createUnloggedTable(conn)

    load(conn, cmdlist)


if __name__ == "__main__":
    main()

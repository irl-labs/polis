## [MA Secretary of State - Elections Division](https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm)

The Commonwealth of Massachusetts maintains a legacy database (1995)  that cities and towns use to upload details about the residents and request extracts for elections and town records purposes.

Below are the three types of extracts we turned into datasets.  From 2004 to 2023, there were about 110 different extracts providing snapshots of some 3.5M records.  As is apparent, the legacy system is suboptimal and a replacement is being planned.

Histograms are pre-calculated; see the ```histograms.ipynb``` notebook.

A. People schema contains 6 tables

    1. attributes ~90K rows
    ```CREATE TABLE IF NOT EXISTS people.attributes
            (
                people_id character(12) COLLATE pg_catalog."default" NOT NULL,
                name character varying(50)[] COLLATE pg_catalog."default",
                date_name date[],
                address_id smallint[],
                date_address_id date[],
                party smallint[],
                date_party date[],
                precinct smallint[],
                date_precinct date[],
                date_dob date,
                dob date,
                sex smallint,
                CONSTRAINT attributes_pkey PRIMARY KEY (people_id)
            )```
    2. addresses  ~30K rows
        * address_id - unique, incremental integer key
        * streetName
        * streetNum
        * unit
        * streetSuffix
        * pid - parcel id; from assessor parcels
    3. elections ~70K rows
    4. registered ~80K rows
    5. residents ~90K rows
        all use
        * people_id - unique, incremental integer key
        * date - array/list of dates
    6. histograms ~300K rows; 210K are from the 21 precinct histograms
        * date - from elections, registered, residents tables
        * type - one of ``` [activity, precinct, party, sex] ```
        * age  - missing default to 1900-01-01
        * count
    

B. MA Database columns

    1. True Lists of Residents  {TOWN_ID}RES_123456.txt
        Census information aboput residents over the age of 18.
        * Record Sequence Number
        * Resident Id Number
        * Last Name
        * First Name
        * Middle Name
        * Title
        * Date of Birth
        * Residential Address - Street Number
        * Residential Address - Street Suffix
        * Residential Address - Street Name
        * Residential Address - Apartment Number
        * Residential Address - Zip Code
        * Mailing Address - Street Name and Number
        * Mailing Address - Apartment Number
        * Mailing Address - City or Town
        * Mailing Address -State
        * Mailing Address - Zip Code
        * Occupation
        * Party Affiliation
        * Nationality
        * Ward Number
        * Voter Status
        * Mail to Code

    2. Registered Voters  {TOWN_ID}VOT_123456.txt
        All residents who are registered to vote
        * Record Sequence Number 
        * Voter ID Number 
        * Last Name 
        * First Name 
        * Middle Name 
        * Title 
        * Residential Address Street Number 
        * Residential Address Street Suffix 
        * Residential Address Street Name 
        * Residential Address Apartment Number 
        * Residential Address Zip Code 
        * Mailing Address ¿ Street Number and Name 
        * Mailing Address - Apartment Number 
        * Mailing Address - City or Town 
        * Mailing Address - State
        * Mailing Address - Zip Code 
        * Party Affiliation 
        * Date of Birth 
        * Date of Registration 
        * Ward Number 
        * Precinct Number 
        * Congressional District Number 
        * Senatorial District Number 
        * State Representative District 
        * Voter Status
        
    3. Election Voting Activity   {TOWN_ID}ANP_123456.txt
        Who voted in an election.
        a. ANP for local/state elections
        b. ACP for Federal elections
        c. Column headers
        * Party Affiliation 
        * Voter ID Number 
        * Last Name 
        * First Name 
        * Middle Name 
        * Residential Address - Street Number
        * Residential Address - Street Suffix 
        * Residential Address - Street Name 
        * Residential Address - Apartment Number 
        * Residential Address - Zip Code 
        * Type of Election 
        * Election Date 
        * City/ Town Name 
        * City/ Town Indicator 
        * City/ Town Code Assigned Number
        * Voter Title 
        * Ward Number 
        * Precinct Number 
        * Voter Status r
        * Mailing Address - Street Number/Name 
        * Mailing Address - Apartment Number 
        * Mailing Address - City/Town 
        * Mailing Address - State 
        * Mailing Address - Zip Code
        
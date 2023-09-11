## [MA Department of Elementary and Secondary Education](https://profiles.doe.mass.edu/)

A. School profiles using [statewide](https://profiles.doe.mass.edu/statereport/) reports detailing:
   
1. [Student Enrollment](https://profiles.doe.mass.edu/statereport/enrollmentbygrade.aspx)
    * [public](https://profiles.doe.mass.edu/statereport/enrollmentbygrade.aspx) - enrollment  
    * [private](https://profiles.doe.mass.edu/statereport/nonpublicschoolreport.aspx) - enrollment  
2. [Assessments](https://profiles.doe.mass.edu/statereport/nextgenmcas.aspx) - mcas  
3. [Finances](https://profiles.doe.mass.edu/statereport/ppx.aspx)
    * [Per pupil expenditures](https://profiles.doe.mass.edu/statereport/ppx.aspx) - ppx  
    * [Chapter 70 Funding/Spending](https://profiles.doe.mass.edu/statereport/netschoolspendingtrend.aspx) - nss  
    * [salaries](https://profiles.doe.mass.edu/statereport/teachersalaries.aspx) - teacher_salaries  
4. [Teachers](https://profiles.doe.mass.edu/statereport/teacherbyracegender.aspx)   
    * [race/gender](https://profiles.doe.mass.edu/statereport/teacherbyracegender.aspx) - teacher_race  
    * [age](https://profiles.doe.mass.edu/statereport/agestaffing.aspx) - teacher_age  
    * [program area](https://profiles.doe.mass.edu/statereport/programareastaffing.aspx) - teacher_program_area  


1. Common [postgres](https://www.postgresql.org/) database tables prefixed with schools_ under infrastructure schema; e.g. ```infrastructure.schools_enrollment```

    * typical table definition
        ```
                CREATE TABLE infrastructure.schools_{category} (
                    "school_id" INTEGER,
                    "year" SMALLINT,
                    "{category}" SMALLINT,
                    "value" INT,
                    PRIMARY KEY ("school_id","year","{category}")
                );
                CREATE INDEX schools_{category}_idx 
                    ON infrastructure.schools_{category}("school_id");
                CREATE INDEX schools_{category}_year_idx 
                    ON infrastructure.schools_{category}("year");
        ```
  
    * ```schools_mcas``` table adds grade, subject (math/ela)
  
2. columns melted into ```category```.  key-value pairs are defined in ```common.int_value_pairs```

    * school_id - names
    * school_type - public, private, district, charter and collaborative 
    * category labels; e.g. teacher_race e.g. 'Male', 'Female', 'White'
  
  
3. Extract, Transform and Load

    * Run time about 5 minutes
    * space requirements
        * enrollments 600K rows / 26M size
        * mcas        1.6M rows / 70M size
        * nss/ppx      60K rows /  3M size
        * teachers    150K rows /  7M size
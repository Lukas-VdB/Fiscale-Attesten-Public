# Code Scheme
This scheme defines the order of operations for the code

## A. Generate Tax Certificate template
1. Read user config file
2. Open Word document
3. Write template information to Word document
4. Save Word document

## B. Preprocess spreadsheet information and API setup

### I. Create dictionary with activity data *(Weekenddata)*
1. Check if Workbook with spreadsheets exists
2. Load spreadsheet *Weekenddata*
3. Create dictionary with:
    - For each age group (tak):
        - All activities and for each activity:
            - start date
            - end date
            - price
4. Delete spreadsheet from memory to save resources:
    - "del"
    - "workbook.close()"
    - "gc.colect()"

### II. Generate dictionary with age group data
1. Read user config file
2. Calculate first year for each age group
3. Generate dictionary

### III. Load Spreadsheet with presence data *(Aanwezigheden)*
1. Load and cache spreadsheet
2. Check column and row headers 
    - Read column and row headers 
    - Save in config file
    - Save as dictionary
3. Read and create list of all names in spreadsheet *Aanwezigheden*

### IV. Establish connection with Groepsadmin API
1. Create login request
2. Let user login
3. Store access token and header

## C. Generate Tax Certificate for every member

**Iterate through the member list from step B. II.**  
**Following steps are repeated for each member.**

### I. Retrieve member information from Groepsadmin API
1. Request member data from Groepsadmin API:
    - full name
    - address
        - street
        - streetnumber
        - zipcode
        - city
    - date of birth
    - alternative year
    - scouting op maat (yes/no)
    - contactperson 1:
        - full name
        - address
    - contactperson 2:
        - full name
        - address
2. Store member data as object of dataclass *Member*
3. Determine contact and store contact data as object of dataclass *Person*

### II. Generate activities for member
**Following steps are repeated for each activity.**
1. Check member presence in spreadsheet *Aanwezigheden*
2. Create copy of *Activity* object
3. Adapt dates and prices to following cases:
    - Member is 14 before activity
    - Member becomes 14 during activity
    - Member has the *Scouting op Maat* discount
    - Precamp for *jonggiver* and *giver* camp

### III. Write data to Tax Certificate template
1. Create copy of template document
2. Write and icnrement serial number
3. Write member and contact data
4. Write activity data
5. Write signatue
6. Save and convert to pdf file
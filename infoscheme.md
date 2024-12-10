# Information Scheme
This scheme defines where the application gets its information from

## Groepsadmin API
#### For each member:
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

## Spreadsheet: "Aanwezigheden"
#### For each member:
- full name
- presence on activities:
    - groepsweekend
    - takweekend 2
    - kamp
    - takweekend 1

## Spreadsheet : "Weekenddata"
#### For each age group (tak):
Activities:
- groepsweekend
- takweekend 2
- kamp
- takweekend 1
#### For each activity:
- start date
- end date
- price

## User config file
#### Info about the youth movement:
- name
- kbo number
- address
#### Info about the certification agency:
- name
- kbo number
- address
#### Signature from the representative of the youth movement:
- place (city)
- full name
- role (within the organisation)
#### Calender year
#### For each age group (tak):
- amount of years (1,2 or 3)

## Config file
This information is generated from previous sources, we just use it to store the info
#### For each age group (tak):
- the (birth)year of the first-years
#### For each spreadsheet:
Information about which column or row holds what data
# data_management_framework

This is a repository for the Data Management Framework - a generic, flexible, and extensible framework to build data-driven prognostics applications off of.   

## Setup steps 
1. clone the repository  `git clone https://github.com/darrahts/data_management_framework.git`  
2. make [setup_database.sh](https://github.com/darrahts/data_management_framework/blob/main/setup_database.sh) executable and run it to setup the database and core tables `cd data_management_framework && chmod +x setup_database.sh`  
3. [optional] create a conda environment `conda create --name=datasci python=3.8 pandas jupyterlab scikit-learn psycopg2 seaborn tqdm pyarrow`




## References
[A Data Management Framework & UAV Simulation Testbed for theStudy of System-level Prognostics Technologies](https://www.researchgate.net/publication/356517965_Data_Management_Framework_UAV_Simulation_Testbed_for_the_Study_of_System-level_Prognostics_Technologies)

[A Data-Centric Approach to the Study of System-Level Prognostics for Cyber Physical Systems: Application to Safe UAV Operations](https://www.researchgate.net/publication/361487074_A_Data-Centric_Approach_to_the_Study_of_System-Level_Prog-_nostics_for_Cyber_Physical_Systems_Application_to_Safe_UAV_Operations)

[Developing Deep Learning Models for System Remaining Useful Life Predictions: Application to Aircraft Engines](https://www.researchgate.net/publication/361487238_Developing_Deep_Learning_Models_for_System_Remaining_Useful_Life_Predictions_Application_to_Aircraft_Engines)


<!--
- [Database schema](#database-schema) intended for a PostgreSQL DBMS
- [Python API](#python-api) to query the database
- [Data exploration and analysis](#data-exploration-and-analysis) notebooks
- [References](#references)
- (more to follow...)

The [Home Mortgage Disclosure Act data (HMDA)](#home-mortgage-disclosure-act-data) ~~is currently the only data available for use. Other data sources will be listed and described as they are made available.~~ provides data on loan applications and contains approximately 25M records per year.  

The [American Community Survey data (ACS)](#american-community-survey-data) provides data on race, age, sex, and population at the census tract level.

The [Zillow Home Value Index (ZHVI)](#zillow-home-value-index-data) provides median home values by neighborhood.

## Home Mortgage Disclosure Act data
Description of the data here

The current data can be downloaded from [here](https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/2020). An interactive map to view the data can be found [here](https://ffiec.cfpb.gov/data-browser/maps/2020?geography=state).

- Loan Application Register (LAR) data
- Panel data
- Transmittal Sheet data

Some of the census tracts in the LAR data file are broken and the file [census_tract_fix.csv](/data/census_tract_fix.csv) fixes them. Reference for this fix can be found [here](https://github.com/cfpb/mapusaurus/blob/master/mapusaurus/geo/errors.py)

## American Community Survey data
Description of the data here

The current data can be downloaded from [here](https://data.census.gov/cedsci/table?q=DP05&y=2020)

## Zillow Home Value Index data
Description of the data here

The current data can be downloaded from [here](https://www.zillow.com/research/data/)

## [Database Schema](/sql)


## [Python API](/package)

### Environment
- if you have a gpu enabled system, use `name=tfgpu`, `tensorflow-gpu`, and `keras-gpu` below.
```
conda create --name=tfcpu python=3.8 tensorflow keras jupyter psycopg2 pandas seaborn boto3

conda activate tfcpu
```

## [Data Exploration and Analysis](/notebooks)



## TODO

- environment file
- documentation
- references


## Redlining Methodology

The standard methodology for identifying lending institutions that are redlining is to compare a given lender to their peer group in a given geography. However, there are multiple methods to do this, and below are some of these methods given by example, in a step by step order to calculate them. 

__1. Peer Group Standard method__ - define an institutions peer group by the 50/200 rule and evaluate the institution against the peer groups in a given geographic area

```{python}
#  do this for all institutions (aka lenders)
lenders = api.get_lenders()
for lender in lenders:

    # get all the census tracts the lender lends in, and the number of records per tract, and the white population percentage of that tract
    tracts = api.get_lar_tracts(lei=lender.lei,counts=True,white_pct=True)

    for row in tracts:
        # if the tract is a minority majority tract by race then get peer groups
            peer_group = api.get_peer_groups(lei=lender.lei,)

    

```
__2. Peer Group Custom__ - 50/200 test but define the peer group based on specific metrics (i.e. requires human in the loop)  

__3. Market Aggregate__ - everyone in the census tract that made a type of loan in question in minority vs majority tracts (i.e. heloc example)  

__4. Tract Penetration__ - ratio of minority to majority loan applications by lender (inference on marketing)

__5. Lender Volume__ - tract penetration test + ratio of minority tracts to majority tracts in a given MSA  

__6. Denial for collateral__ - look at this type of denial by bank in minority vs majority tracts, can be done as market aggregate or by peer group

__7. Appriasal bias__ - i.e. reverse redlining, are minority owned homes appraised less


## misc notes (to be deleted)

prioritize lendors to analyze by their volume by msa

filter for types of loans (i.e. heloc example)

compare ratio of approvals of minority to majority

compare ratio of majority-minority tracts to ratio of minority approvals

compare bank to itself (i.e. aggregate a banks majority loan approval, then compare to each minority tract)

at what level do we do this? MSA, county, or tract? We could actually do this at all levels with little code modification to the same piece of code

-->

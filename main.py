# Import modules
import os
from pathlib import Path
import pandas as pd
import requests
from datetime import datetime
from plotnine import *
from yaspin import yaspin
import time
import logging

# VARIABLES AND INITIALISATION
error_count = 0
url_cases = 'https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv'
f = open("covidtracker.log", "a")
# url_deaths = 'https://coronavirus.data.gov.uk/downloads/csv/coronavirus-deaths_latest.csv'

def getStats():
    global error_count
    cwd = os.path.dirname(os.path.realpath(__file__))
    path = Path("stats/")
    path_to_stats = cwd / path

    with yaspin(text=" Checking if 'stats' folder is present...", color="yellow") as spinner:
        time.sleep(1)  # time consuming code

        if not os.path.exists(path_to_stats):
            spinner.fail("✘")
            os.makedirs(path_to_stats)
        else:
            spinner.ok("✔")

    with yaspin(text=" Downloading COVID-19 cases...", color="yellow") as spinner:
        time.sleep(2)
        try:
            response = requests.get(url_cases)
            with open(os.path.join(path_to_stats, "covid-cases.csv"), 'wb') as f:
                f.write(response.content)
        except Exception:
            spinner.fail("✘")
            error_count += 1
        else:
            spinner.ok("✔")
    """
    with yaspin(text=" Downloading COVID-19 deaths...", color="yellow") as spinner:
        time.sleep(2)
        try:
            response = requests.get(url_deaths)
            with open(os.path.join(path_to_stats, "covid-deaths.csv"), 'wb') as f:
                f.write(response.content)
        except Exception:
            spinner.fail("✘")
            error_count += 1
        else:
            spinner.ok("✔")
    """

def csv_parser():
    # Get abs path
    cwd = os.path.dirname(os.path.realpath(__file__))
    path = Path("stats/")
    path_to_stats = cwd / path

    # Get path to files
    covid_case_file_path = path_to_stats / "covid-cases.csv"
    # covid_death_file_path = path_to_stats / "covid-deaths.csv"

    # Read CSV files
    cases = pd.read_csv(covid_case_file_path).dropna()
    # deaths = pd.read_csv(covid_death_file_path).dropna()

    # Get England data
    cases_filtered_england = cases.loc[cases['Area name'] == "England"]
    # deaths_filtered_england = deaths.loc[deaths['Area name'] == "England"]

    # Sort by date
    cases_sorted = cases_filtered_england.sort_values(by='Specimen date')
    # deaths_sorted = deaths_filtered_england.sort_values(by='Reporting date')

    # Convert date strings to datetime objects
    cases_sorted['Specimen date'] = pd.to_datetime(cases_sorted['Specimen date'])
    # deaths_sorted['Reporting date'] = pd.to_datetime(deaths_sorted['Reporting date'])

    # Return data from function
    return cases_sorted # ,deaths_sorted

# First, get latest stats using getStats()
getStats()

# Then, parse the data: we only need the dates and their corresponding values.
imported = csv_parser()
cases = imported #[0]
# deaths = imported[1]

# Temporary variables
date_today = datetime.now().strftime('%d-%m-%Y')
cwd = os.path.dirname(os.path.realpath(__file__))
path_2 = Path("graphs/")
path_to_graphs = cwd / path_2

with yaspin(text=" Checking if 'graphs' folder is present...", color="yellow") as spinner:
    time.sleep(1)
    if not os.path.exists(path_to_graphs):
        spinner.fail("✘")
        os.makedirs(path_to_graphs)
    else:
        spinner.ok("✔")


with yaspin(text=" Creating and saving the daily cases plot...", color="yellow") as spinner:
    try:
        p1 = ggplot(cases, aes(x="Specimen date", y="Daily lab-confirmed cases", group = 1)) + geom_col() + labs(title = "Daily COVID-19 Cases") + scale_x_date(date_breaks = "3 days") + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan', show_legend=True) + stat_smooth(method='mavg', method_args={'window': 7}, color='blue') + theme(axis_text_x=element_text(rotation=45, hjust=1))
        p1.save(filename=('cases_daily_' + str(date_today)),path=path_to_graphs,height=6, width=20, units = 'in', dpi=1000, verbose = False)
    except Exception as e:
        spinner.fail("✘")
        error_count += 1
        #f = open("covidtracker.log", "a")
        #f.write(str(Argument))
        #f.close()
        print(e)
    else:
        spinner.ok("✔")

"""
with yaspin(text=" Creating and saving the daily change in deaths plot... ", color="yellow") as spinner:
    try:
        p2 = ggplot(deaths, aes(x="Reporting date", y="Daily change in deaths", group = 1)) + geom_col() + labs(title = "Daily Change in Deaths") + scale_x_date(date_breaks = "3 days") + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan') + stat_smooth(method='mavg', method_args={'window': 7}, color='blue') + theme(axis_text_x=element_text(rotation=45, hjust=1))
        p2.save(filename = ('deaths_change_daily_' + str(date_today)),path=path_to_graphs,height=6, width=20, units = 'in', dpi=1000, verbose = False)
    except Exception:
        spinner.fail("✘")
        error_count += 1
    else:
        spinner.ok("✔")
"""

with yaspin(text=" Creating and saving the cumulative cases plot...", color="yellow") as spinner:
    try:
        p3 = ggplot(cases, aes(x="Specimen date", y="Cumulative lab-confirmed cases", group = 1)) + geom_point() + geom_line() + labs(title = "Cumulative Cases") + scale_x_date(date_breaks = "3 days") + theme(axis_text_x=element_text(rotation=45, hjust=1))
        p3.save(filename = ('cumulative_cases_' + str(date_today)),path=path_to_graphs,height=6, width=20, units = 'in', dpi=1000, verbose = False)
    except Exception as e:
        spinner.fail("✘")
        error_count += 1
        #f = open("covidtracker.log", "a")
        #f.write(str(Argument))
        #f.close()
        print(e)
    else:
        spinner.ok("✔")

"""
with yaspin(text=" Creating and saving the cumulative deaths plot...", color="yellow") as spinner:
    try:
        p4 = ggplot(deaths, aes(x="Reporting date", y="Cumulative deaths", group = 1)) + geom_point() + geom_line() + labs(title = "Cumulative Deaths") + scale_x_date(date_breaks = "3 days") + theme(axis_text_x=element_text(rotation=45, hjust=1))
        p4.save(filename = ('cumulative_deaths_' + str(date_today)),path=path_to_graphs,height=6, width=20, units = 'in', dpi=1000, verbose = False)
    except Exception:
        spinner.fail("✘")
        error_count += 1
    else:
        spinner.ok("✔")
"""

if error_count > 1:
    print("⚠  {} errors were encountered during runtime. Check the logs...".format(error_count))
else:
    print("❤  Success. Thank you for your patience.")
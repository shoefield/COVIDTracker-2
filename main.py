# Import modules
import os
from pathlib import Path
import pandas as pd
import requests
import traceback
from datetime import datetime
from plotnine import *
import sys
import threading
import itertools
import time

class Spinner:

    def __init__(self, message, delay=0.1):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        sys.stdout.write(message)

    def write_next(self):
        with self._screen_lock:
            if not self.spinner_visible:
                sys.stdout.write(next(self.spinner))
                self.spinner_visible = True
                sys.stdout.flush()

    def remove_spinner(self, cleanup=False):
        with self._screen_lock:
            if self.spinner_visible:
                sys.stdout.write('\b')
                self.spinner_visible = False
                if cleanup:
                    sys.stdout.write(' ')       # overwrite spinner with blank
                    sys.stdout.write('\r')      # move to next line
                sys.stdout.flush()

    def spinner_task(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    def __enter__(self):
        if sys.stdout.isatty():
            self._screen_lock = threading.Lock()
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task)
            self.thread.start()

    def __exit__(self, exception, value, tb):
        if sys.stdout.isatty():
            self.busy = False
            self.remove_spinner(cleanup=True)
        else:
            sys.stdout.write('\r')


# VARIABLES AND INITIALISATION
url_cases = 'https://coronavirus.data.gov.uk/downloads/csv/coronavirus-cases_latest.csv'
url_deaths = 'https://coronavirus.data.gov.uk/downloads/csv/coronavirus-deaths_latest.csv'


def getStats():
    cwd = os.path.dirname(os.path.realpath(__file__))
    path = Path("stats/")
    path_to_stats = cwd / path

    print("[*] Checking if 'stats' folder is present...")
    if not os.path.exists(path_to_stats):
        print("[*] Does not exist. Creating 'stats' folder...")
        os.makedirs(path_to_stats)
    else:
        try:
            unix_datetime_cases = datetime.utcfromtimestamp(
                os.path.getmtime(os.path.join(
                    path_to_stats, "covid-cases.csv")))
            unix_datetime_deaths = datetime.utcfromtimestamp(os.path.getmtime(
                os.path.join(path_to_stats, "covid-deaths.csv")))
            print("[@] 'covid-cases.csv' last modified: {}".format(
                unix_datetime_cases))
            print("[@] 'covid-deaths.csv' last modified: {}".format(
                unix_datetime_deaths))

            if unix_datetime_cases.date() and unix_datetime_deaths.date() == datetime.today().date():
                print("[@] Local data is up-to-date. Skipping download.")
                return None
            else:
                pass
        except Exception:
            print("[/] It appears that the data has not been downloaded.")

    print("[*] Attempting to download COVID-19 cases...")
    try:
        response = requests.get(url_cases)
        with open(os.path.join(path_to_stats, "covid-cases.csv"), 'wb') as f:
            f.write(response.content)
    except Exception:
        traceback.print_exc()
        print("[/] Failed to download COVID-19 cases.")
    else:
        print("[@] Successfully downloaded COVID-19 cases!")

    print("[*] Attempting to download COVID-19 deaths...")
    try:
        response = requests.get(url_deaths)
        with open(os.path.join(path_to_stats, "covid-deaths.csv"), 'wb') as f:
            f.write(response.content)
    except Exception:
        print("[/] Failed to download COVID-19 deaths!")
    else:
        print("[@] Successfully downloaded COVID-19 deaths!")


def csv_parser():
    # Get abs path
    cwd = os.path.dirname(os.path.realpath(__file__))
    path = Path("stats/")
    path_to_stats = cwd / path

    # Get path to files
    covid_case_file_path = path_to_stats / "covid-cases.csv"
    covid_death_file_path = path_to_stats / "covid-deaths.csv"

    # Read CSV files
    cases = pd.read_csv(covid_case_file_path).dropna()
    deaths = pd.read_csv(covid_death_file_path).dropna()

    # Get England data
    cases_filtered_england = cases.loc[cases['Area name'] == "England"]
    deaths_filtered_england = deaths.loc[deaths['Area name'] == "England"]

    # Sort by date
    cases_sorted = cases_filtered_england.sort_values(by='Specimen date')
    deaths_sorted = deaths_filtered_england.sort_values(by='Reporting date')

    # Convert date strings to datetime objects
    cases_sorted['Specimen date'] = pd.to_datetime(cases_sorted['Specimen date'])
    deaths_sorted['Reporting date'] = pd.to_datetime(deaths_sorted['Reporting date'])

    # Return data from function
    return cases_sorted, deaths_sorted


# First, get latest stats using getStats()
getStats()

# Then, parse the data: we only need the dates and their corresponding values.
imported = csv_parser()
cases = imported[0]
deaths = imported[1]

# Temporary variables
date_today = datetime.now().strftime('%d-%m-%Y')
cwd = os.path.dirname(os.path.realpath(__file__))
path_2 = Path("graphs/")
path_to_graphs = cwd / path_2

print("[*] Checking if 'graphs' folder is present...")
if not os.path.exists(path_to_graphs):
    print("[*] Does not exist. Creating 'graphs' folder...")
    os.makedirs(path_to_graphs)


with Spinner("Creating and saving the daily cases plot... "):
    p1 = ggplot(cases, aes(x="Specimen date", y="Daily lab-confirmed cases", group = 1)) + geom_point() + geom_line() + labs(title = "Daily COVID-19 Cases") + scale_x_date(date_breaks = "3 days") + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan', show_legend=True) + stat_smooth(method='mavg', method_args={'window': 7}, color='blue') + theme(axis_text_x=element_text(rotation=45, hjust=1))
    p1.save(filename=('cases_' + str(date_today)),path=path_to_graphs,height=5, width=15, units = 'in', dpi=1000, verbose = False)

with Spinner("Creating and saving the daily change in deaths plot... "):
    p2 = ggplot(deaths, aes(x="Reporting date", y="Daily change in deaths", group = 1)) + geom_point() + geom_line() + labs(title = "Daily change in deaths") + scale_x_date(date_breaks = "3 days") + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan') + stat_smooth(method='mavg', method_args={'window': 7}, color='blue') + theme(axis_text_x=element_text(rotation=45, hjust=1))
    p2.save(filename = ('death_change_' + str(date_today)),path=path_to_graphs,height=5, width=15, units = 'in', dpi=1000, verbose = False)
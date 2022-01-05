import requests
import pandas as pd
import json
from pathlib import Path
import shutil
import logging
from datetime import datetime

ACCESS_TOKEN = 'YOUR_TOKEN_HERE'
HEADERS = {'Authorization' : 'Bearer ' + ACCESS_TOKEN }

FY = '2019'

logging.basicConfig(filename='export.log', level=logging.INFO)

PERIODS = ['Januar', 'Februar', 'März', 'April', \
    'Mai', 'Juni', 'Juli', 'August', 'September', \
    'Oktober', 'November', 'Dezember', 'Sonderperioden']

def check_fiscal_year(FY):
    # Check if the requested year is among the years available and
    # return the timestamps for the beginning and the end of the period
    r = requests.get('https://appload.scopevisio.com/rest/fiscalyears', headers=HEADERS)
    data = json.loads(r.text)
    for year in data['years']:
        # check for the requested year
        if year['name'] == FY:
            for period in year['periods']:
                if period['name'] == 'Dezember':
                    ts_end = period['endTs']
            # on success return the timestamps
            return(year['beginningTs'], ts_end)

def get_document_numbers(ts_start, ts_end):
    # Results are paginated (100 results per request), but no information
    # on the total number of records is provided by the API.
    # So we need to loop through until the length of the result is 0.
    # (Still HTTP 200 is returned in this case.)
    i = 1
    while True:
        HEADERS['Content-Type'] = 'application/json'
        query = json.dumps({
                'page' : i,
                'fields' : [
                    "rowNumber",
                    "postingDate",
                    "documentNumber",
                    "externalDocumentNumber",
                    "accountNumber",
                    "accountName",
                    "createdTs",
                    "externalDocumentTs",
                    "documentText",
                    "postingPeriodLabel"
                ],
                'postingDateSince' : ts_start,
                'postingDateBefore' : ts_end
            })
        r = requests.post('https://appload.scopevisio.com/rest/journal', \
            headers=HEADERS, data=query)
        data = json.loads(r.text)
        # break the loop when the length of the result is 0
        if len(data['records']) == 0:
            break
        i += 1
        # yield the results to the main fuction as long as there are results
        yield data

def create_folders(FY, periods):
    for period in PERIODS:
        Path(FY + '/' + period).mkdir(parents=True, exist_ok=True)

def get_documents(df, FY, periods):
    logging.info("Range: " + str(df.index))
    for n in df.index:
        log = "Dokument: " + df['documentNumber'][n] + "  Periode: " + df['postingPeriodLabel'][n]
        url = 'https://appload.scopevisio.com/rest/journal/' + df['documentNumber'][n] + '/file'
        r = requests.get(url, headers=HEADERS)
        log = log + " - HTTP Status: " + str(r.status_code)
        if r.status_code == 200:
            filename = df['documentNumber'][n] + '.pdf'
            file = open(filename, 'wb')
            file.write(r.content)
            file.close()
            #now move file to correct folder
            if df['postingPeriodLabel'][n] in PERIODS:
                sub_folder = df['postingPeriodLabel'][n]
            else:
                sub_folder = 'Sonderperioden'
            p = Path(FY + '/' + sub_folder + '/' + filename)
            log = log + " - " + str(p)
            shutil.move(filename, p)
            log = log + " - [OK]"
            print(log)
            logging.info(log)
        else:
            log = log + " - No file - [SKIP]"
            print(log)
            logging.info(log)

def main():
    print("Start...!")
    dt = datetime.now()
    logging.info("*** Start at " + str(dt) +" ***")
    # Get the timestamp for the given year
    ts_start, ts_end = check_fiscal_year(FY)
    # Due to pagination, we need to build the dataframe using Pandas by and by
    for x, page in enumerate(get_document_numbers(ts_start, ts_end)):
        if x == 0:
            df = pd.json_normalize(page, record_path=['records'])
        else:
            df_next = pd.json_normalize(page, record_path=['records'])
            df = df.append(df_next, ignore_index=True)
    # Each posting consists of at least 2 entries (min. 2 accunts touched)
    # We don't want to download duplicate documents later so we elimated duplicates
    # by documentNumber
    df.drop_duplicates(subset=['documentNumber'], inplace=True, ignore_index=True)
    # For creating the sub-directories, we get all the posting period labels
    df_periods = df.drop_duplicates(subset=['postingPeriodLabel'], ignore_index=True)
    periods = df_periods['postingPeriodLabel'].tolist()
    # build the local folder structure
    create_folders(FY, periods)
    # get the documents and place them in the right directory
    get_documents(df, FY, periods)
    dt = datetime.now()
    logging.info("*** End at " + str(dt) +" ***")
    print("... Finished.")

if __name__ == "__main__":
    main()
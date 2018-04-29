import os
import logging
import argparse
import pandas as pd

# Logging configuration 
FORMAT = '[%(levelname)s] [ %(name)s ] %(message)s' 
logging.basicConfig(level=logging.INFO, format=FORMAT) 
logger = logging.getLogger(os.path.basename(__file__))

def create_second_table(kpi_file, output_file):
  # read the data to put in the table
  kpi_data = pd.read_csv(kpi_file)

  # isolate unique client, run_date combos for the table tracking which have been classified and as whether or not is is an alert
  tracking_data = kpi_data.drop_duplicates(subset=['client_name', 'run_date'])[['client_name', 'run_date']]

  # expand to include the KPI columns
  kpis = ['cos', 'ctr', 'cr', 'spend', 'site_events']
  kpi_list = kpis * tracking_data.shape[0] # duplicates all entries to have 1 per client
  tracking_data = tracking_data.append([tracking_data] * (len(kpis) - 1), ignore_index=True) # duplicates rows of clients
  tracking_data = tracking_data.sort_values(['client_name', 'run_date']) # put dataframe in proper order for adding the KPI column
  tracking_data = tracking_data.reset_index(drop=True)
  tracking_data['kpi'] = kpi_list

  # # add boolean columns
  tracking_data['is_classified'] = False
  tracking_data['is_alert'] = False

  # write the data
  tracking_data.to_csv(output_file, index=False)

if __name__ == "__main__":
  # Parse command line arguments
  parser = argparse.ArgumentParser(description='Use KPI Evolution File to Generate Classification Lookup File')     
  parser.add_argument('--kpi_file')     
  parser.add_argument('--output_file')     
  args = parser.parse_args()
  create_second_table(kpi_file=args.kpi_file, output_file=args.output_file)
  logger.info("Your classification file has been generated.")
  

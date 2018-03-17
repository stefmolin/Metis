import os
from shutil import copy
import logging
import random
import pandas as pd

def copy_data_file_over(src, dst, logger):
  '''Copy a file to a new location (overwriting if it exists already if in testing) 
     
     Arguments:
        src:    File to copy.
        dst:    Destination to copy file to
        logger: The logger to use for status updates.'''
  # if we are in dev always copy (and overwrite the file) if not check first if it is there already
  if os.environ.get('DEPLOYMENT_ENVIRONMENT') == 'testing' or not os.path.isfile(dst):
    # if file is not already there, move it
    logger.debug("Copying file {a} to {b}".format(a=src, b=dst))
    # copy file to somewhere postgres can reach it
    copy(src=src, dst=dst)

def index_generator(index_list, use_first=None):
  '''Generate indices for selecting KPI evolutions
  
  Arguments:
    index_list:   List of indices to select from
    use_first:    Indices that should be used once before using the index_list. 
                  These should also be included in the index_list.'''
  if use_first:
    # if there are indices that need to be used first, shuffle them and yield each once
    random.shuffle(use_first)
    for index in use_first:
      yield index
  while True:
    # shuffle the indices and yield one by one until they run out then repeat
    random.shuffle(index_list)
    for index in index_list:
      yield index

def get_unclassified_indices(all_combos_df, classified_combos_df):
  '''Get the indices that haven't been classified
  
  Arguments:
    all_combos_df:  Pandas dataframe of all client_name, kpi, and run_date combinations in database
    classified_combos_df: Pandas dataframe of all data in the classification logs 
                          (at time of container launch since we will only query once)'''
  # this is doing a join by matching up the column names--make sure they stay the same in the tables
  unclassified = all_combos_df.reset_index().merge(classified_combos_df, how='left', indicator=True).\
    set_index('index').query("_merge == 'left_only'")
  return list(unclassified.index.values)

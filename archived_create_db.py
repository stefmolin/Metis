# These are one-time functions that were used to fill the database.
# They are no longer part of the database class, but here for reference.

def __setup_db(self):
  '''Create the schema specified in MetisDatabase constructor
     and create tables in the database as specified by importing
     of the metis.models module.

     Note: this method is only to be used in the MetisDatabase constructor'''
  # status
  self.logger.info('Initializing database schema and tables')

  # wait for DB container to restart
  time.sleep(60)

  # Create the schemas
  schemas = [self.schema]
  for schema in schemas:
    # create the schema if the database is reachable
    query = 'CREATE SCHEMA IF NOT EXISTS {}'.format(schema)
    for _ in range(30):
      try:
        self.engine.execute(query)
        break
      except OperationalError as e:
        last_error = e
        time.sleep(1)
    else:
      raise(last_error) # database wasn't reachable

  # create tables if they don't already exist
  self.Base.metadata.create_all(self.engine)

def __write_to_table(self, table_name, data_file):
  '''Write the data from a given CSV file to the designated
  table in the database.

   Arguments:
     table_name: The name of the table to copy the file to (without the schema--
                 this will be taken from the attributes defined upon construction of this class)
     data_file:  The file to copy from'''
  # new path for the file (so postgres can access for copy)
  path_in_container = '/data/' + os.path.basename(data_file)

  # make sure data file is in proper folder
  utils.copy_data_file_over(src=data_file, dst=path_in_container, logger=self.logger)

  # write to table
  self.logger.info("Writing to table '{}'".format(table_name))
  query = 'COPY {schema_name}.{table} FROM \'{filepath}\' WITH DELIMITER \',\' CSV HEADER'.\
    format(schema_name=self.schema, table=table_name, filepath=path_in_container)

  # need to retry since there is now a lot more data
  for _ in range(30):
    try:
      time.sleep(1) # see if this stops it from failing the first time
      self.session.execute(query)
      self.session.commit()
      break
    except OperationalError as e:
      last_error = e
      self.session.rollback() # need to undo the transaction since something failed
      time.sleep(1)
  else:
    raise(last_error) # database wasn't reachable

def __fill_table(self, directory, table_name):
  '''For files that haven't already been used, write them to the database (mapped by directory).

    Arguments:
      directory:  The path to the directory where the files for a given table are
                  (1:1 relationship required)
      table_name: Name of the table to copy the files (without schema--handled internally)'''
  # files written to the database already
  files_written = [f[0] for f in self.session.query(models.FilesWritten.file_name).all()]

  # debug statements
  self.logger.debug("Files used already: " + ', '.join(files_written))

  # get files that can be written to the tables
  files = [os.path.basename(x.path) for x in os.scandir(directory) if x.is_file() and x.name.endswith('.csv')]

  for file in files:
    if not file in files_written:
      self.logger.debug('Writing new file {} to database.'.format(file))
      # write to database from file
      self.__write_to_table(table_name=table_name, data_file=os.path.join('data', table_name, file))
      # note that the file has been used
      self.session.add(models.FilesWritten(file_name = file))
      self.session.commit()
    else:
      self.logger.debug(file + ' has been used already.')

def __fill_data_tables(self, directory_dict):
  '''Fill tables according to a mapping of directory of data files to table name.

     Arguments:
        directory_dict: Dictionary where the key is the name of the target table and the
                        directory of the date files for a given table is the value.'''
  # fill all tables in the directory dictionary
  for key, value in directory_dict.items():
    self.__fill_table(directory=value, table_name=key)


def get_db_tables(self):
  '''Get list of the tables currently created in the database'''
  return self.Base.metadata.tables.keys()

def debug_tables(self, tables):
  '''If in debug logging level, query for 5 sample rows and row count from given tables.

     Arguments:
       tables:  The tables (schema.table_name) to get diagnostics for.'''
  if self.logger.getEffectiveLevel() == 10: # if we are debugging, check what the tables look like
    query_one = 'SELECT * FROM {} LIMIT 5'
    query_two = 'SELECT COUNT(0) FROM {}'
    for table in tables:
      self.logger.debug("Some entries from table '{}'".format(table))
      results = self.session.execute(query_one.format(table))
      for result in results:
        self.logger.debug(result)
      self.logger.debug("Total rows in table '{}': ".format(table) + str(self.session.execute(query_two.format(table)).scalar()))

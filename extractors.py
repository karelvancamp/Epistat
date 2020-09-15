import glob
import tabula
import pandas as pd
import re
import logging


def find_table(file, column=None, value=None):
    tables = tabula.read_pdf(file, pages="all", multiple_tables=True, silent=True)
    return [x for x in tables
            if (column == None or column in x.columns)
            and (value == None or value in x[column].values)]


def scan_files(star_pattern, function, column=None, value=None):
    A = {file: function(file, column, value) for file in glob.glob(star_pattern)}
    return {x: pd.concat(y) for x, y in A.items() if y}


column = 'Unnamed: 0'
value = 'Plaats van overlijden'
star_pattern = "data\epistat_daily\*2020*.pdf"
save_at = 'derived data\epistat\epistat_place_of_death.csv'


def deaths_details_epistat():

    def double_merged(df, column):
        # df[column] = df[column].str.replace(' ','')
        df[column.split(' ')] = df[column].str.replace('[0-9]{1,3}%', '-') \
                                    .str.split("-", n=2, expand=True, ) \
                                    .iloc[:, [0, 1]]
        return df

    def single_merged(df, column):
        # df[column] = df[column].str.replace(' ','')
        df[column] = df[column].str.replace('[0-9]{1,3}%', '-') \
                         .str.split("-", n=1, expand=True, ) \
                         .iloc[:, [0]]
        return df

    cleaner = {'Vlaanderen Brussel': lambda df: double_merged(df, 'Vlaanderen Brussel'),
               'Wallonië': lambda df: single_merged(df, 'Wallonië'),
               'België': lambda df: single_merged(df, 'België'),
               'Vlaanderen': lambda df: single_merged(df, 'Vlaanderen'),
               'Brussel': lambda df: single_merged(df, 'Brussel'), }

    def clean_frame(df, name):
        for x in df.columns:
            if x in cleaner:
                cleaner[x](df)
        if 'Vlaanderen Brussel' in df.columns:
            df.drop('Vlaanderen Brussel', 1, inplace=True)
        for x in df.columns:
            if 'Unnamed' not in x:
                try:
                    df[x] = df[x].str.replace(' ', '')
                except:
                    logging.info(f'Could not process {name}')
        dt = re.findall('[0-9]{8}', name)[0]
        df['Date_reporting'] = pd.to_datetime(dt, format='%Y%m%d')
        return df

    def do():

        # scan the pdf files for 'Plaats van overlijden' tables
        library = scan_files(star_pattern, find_table, column, value)
        # return library
        logging.info(f'{len(library)} tables found.')

        # clean data & handle inconsistent layout
        solution = {x: clean_frame(y, x) for x, y in library.items()}

        concat_results = pd.concat([x for x in solution.values()]).reset_index(level=0)
        results = concat_results[['index',
                                  'Unnamed: 0',
                                  'Wallonië',
                                  'België',
                                  'Vlaanderen',
                                  'Brussel',
                                  'Date_reporting', ]]

        clean_results = results.groupby(by=['Date_reporting', 'index', 'Unnamed: 0']).sum()
        logging.info(f'{len(clean_results)} records found.')
        # save to csv
        clean_results.to_csv(save_at)

        return clean_results, library

    cr = do()
    return cr


def partial_melt(df, index_1, index_2):
    test1 = df.loc[pd.IndexSlice[:, [index_1], [index_2]], :]
    test1 = test1.unstack()
    test1.columns = test1.columns.to_flat_index()
    return test1


clean_results = deaths_details_epistat()

# with open(save_at, 'w')as f:     f.write(clean_results)
# clean_results = deaths_details_epistat()

"""
clean_results.reset_index(inplace=True)

translate = {(3, 'Bevestigde gevallen'):'Hospital PCR postive cases',
(4, 'Mogelijke gevallen'):'Hospital PCR negative cases',
(4, 'Bevestigde gevallen'):'Hospital PCR postive cases',
(5, 'Mogelijke gevallen'):'Hospital PCR negative cases',

(5, 'Bevestigde gevallen'):'Care center PCR postive cases',
(6, 'Mogelijke gevallen'):'Care center PCR negative cases',
(6, 'Bevestigde gevallen'):'Care center PCR postive cases',
(7, 'Mogelijke gevallen'):'Care center PCR negative cases'}


def ix(x):
    return tuple(x) in translate

selection = clean_results[clean_results[["index","Unnamed: 0"]].apply(lambda x:ix(x), axis=1)]
selection['Type'] = selection[["index","Unnamed: 0"]].apply(lambda x:ix(x), axis=1)


selection.set_index(keys=['Date_reporting','index',"Unnamed: 0"], inplace=True)


show = {
 (3, 'Bevestigde gevallen'),
 (4, 'Mogelijke gevallen'),
(4, 'Bevestigde gevallen'),
(5, 'Mogelijke gevallen'),
(5, 'Bevestigde gevallen'),
 (6, 'Bevestigde gevallen'),
 (7, 'Mogelijke gevallen'),
}

test = pd.concat([partial_melt(clean_results[['Vlaanderen','Wallonië','Brussel','België']], x,y)
                  for x,y in show],
                 axis=1, sort=False)

overview = test.fillna(0).astype('int').unstack()

overview.to_csv('derived data\epistat\epistat_place_of_death_.csv')
"""

def partial_melt(df, index_1, index_2):
    test1 = df.loc[pd.IndexSlice[:, [index_1], [index_2]], :]
    test1 = test1.unstack().unstack()
    test1.columns = test1.columns.to_flat_index()
    return test1

clean_results = pd.read_csv(save_at)
clean_results.set_index(keys=['Date_reporting', 'index', "Unnamed: 0"], inplace=True)

show = {
 (3, 'Bevestigde gevallen'),
 (4, 'Mogelijke gevallen'),
 (6, 'Bevestigde gevallen'),
 (7, 'Mogelijke gevallen'),
}

test = pd.concat([partial_melt(clean_results[['Vlaanderen','Wallonië','Brussel','België']], x,y)
                  for x,y in show],
                 axis=1, sort=False)

overview = test.fillna(0).astype('int')
overview.to_csv('derived data\epistat\epistat_place_of_death_.csv')


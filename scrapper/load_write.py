from django.conf import settings
import os
import pandas as pd

csv_path = os.path.join(settings.DATA_DIR, 'scrapper') 


def load_db_tolist(args):     
    # print(csv_path)
    from_csv = pd.read_csv(f'{csv_path}/{args}.csv')    
    loaded_db = from_csv.search_word.to_list()
    return loaded_db

def load_db_todict(args):     
    # print(csv_path)
    from_csv = pd.read_csv(f'{csv_path}/{args}.csv')     
    loaded_db = from_csv.to_dict('records')    
    return loaded_db        

def write_todb(args,filename):
    # print(csv_path)
    make_df = pd.DataFrame(args)
    make_df.to_csv(f'{csv_path}/{filename}.csv', index = False)    

def append_todb(args,filename):
    # print(csv_path)
    make_df = pd.DataFrame(args)
    make_df.to_csv(f'{csv_path}/{filename}.csv', mode = "a", header = None, index = False)
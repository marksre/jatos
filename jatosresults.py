## navigate to location of python virtual environment
## once in correct directory, use this command in bash: source .venv/bin/activate
## to run: python jatosresults.py
 
import glob
import pandas
import json

input_path = '/Users/rebeccamarks/Desktop/jatos/'

## each individual will need to specify:
output_path = '/Users/rebeccamarks/Desktop/jatos/'

def jatos_to_dfs(filename):
    """
    A function to read in each jatos output file as multiple dataframes
    """
    line_number = 0
    with open(filename) as data_file:    
        for line in data_file:
            line_number += 1
            try:
                data = json.loads(line)
            except:
                print(f'An error occurred while reading file {filename} on line {line_number}')
                continue
            df = pandas.json_normalize(data, 'data')
            yield df

def combine_jatos():
    """
    A function to concatenate jatos output 'df' objects
    """
    filenames = glob.glob(f'{input_path}/**/*.txt')

    dfs = []
    for filename in filenames:
        dfs_per_file = jatos_to_dfs(filename)
        for df in dfs_per_file:
            dfs.append(df)

    return pandas.concat(dfs) ##concat -> becomes one df

def convert_task(task):
    """
    Rename task labels
    """
    lookup = {
        "English": "ENMA",
        "Visual": "VMA",
        "Chinese": "CHMA",
        "Spanish": "SPMA"
    }

    return task if task not in lookup else lookup[task]
    
def convert_rt(response, response_time):
    """
    A function to replace RT for all null responses with 'None'
    """
    if response == 'f':
        return response_time
    elif response == 'j':
        return response_time
    return None

def rotate(l, n):
    return l[n:] + l[:n]

def fix_rt(df):
    df['rt'] = df.apply(lambda x: convert_rt(x.response, x.response_time), axis=1)
    return df

## filter: only experimental trials
## groupby subject & task
## mean acc and rt for each subject/task combo
## subID = rows, mean_acc and mean_rt = columns
def transform(df):
    df = df.rename(columns={"correct": "acc", "subID": "record_id"})
    df['task'] = df.task.apply(convert_task)
    df = df.sort_values(by=['task', 'record_id'])
    experimentaltrial = df['trial_type'] == 'experiment'
    df = df[experimentaltrial]
    print(df)
    df = df.groupby(['task','Cond','record_id']).mean()
    df.reset_index(inplace=True)
    return df    

def pivot(df):
    print(df)
    df = df.pivot(index='record_id', columns=['task','Cond'], values=['acc', 'rt'])
    df.columns = ['_'.join(rotate(c, 1)) for c in df.columns]
    df = df.reindex(sorted(df.columns), axis=1)
    return df


df = combine_jatos()
df = fix_rt(df)
df = transform(df)
df = pivot(df)
df.to_csv(f'{output_path}/Jatos-to-RedCap.csv')

print(df)

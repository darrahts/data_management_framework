
import json
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt
import random
import string
import sys


def progressbar(iterator, prefix="", size=60, out=sys.stdout):
  """
      @brief: Progress bar display for generators
      
      @params: 
              iterator - when using a generator, wrap in a list
              prefix - anything desired to be displayed 
  """
    count = len(iterator)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, u"#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(iterator):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


def generate_serial_number(length: int = 8) -> str:
  """
      @brief: generates random alpha numeric serial numbers
      
      @params: 
              length - the length of the serial number
  """
    return ''.join(random.choices(string.digits + string.ascii_letters, k=length))


def load_json(file_location, data_header, footer):
  """
      @brief: loads a json file as a dict
      
      @params: 
              file_location - the parent directory of the json files
              data_header - the header part of the file name
              footer - the footer part, must end in .json
  """
    fname = log_location + '/' + data_header + footer
    with open(fname, 'r') as f:
        data = json.loads(f.read())
    return data


def parse_json(json_object, target_key, res=[]):
  """
      @brief: parses a json object or python dict for a specific key
              the key can reside in any level
      
      @params: 
              json_object - the json or dict object
              target_key - the key to search for
              res - output variable (typically [])
  """
    if type(json_object) is dict and json_object:
        for key in json_object:
            if key == target_key:
                res.append(json_object[key])
            parse_json(json_object[key], target_key, res)

    elif type(json_object) is list and json_object:
        for item in json_object:
            parse_json(item, target_key, res)
    
    return res


def chunk_generator(X, n):
  """
    @brief: breaks large data into smaller equal pieces + remainder as last yield
    
    @params:
          X - the dataframe, list, or np.array of data 
          n - the size of the chunk
  """
    for i in range(0, len(X), n):
        if type(X) == pd.core.frame.DataFrame:
            yield i+1, X.iloc[i:i+n]
        else:
            yield i+1, X[i:i+n]


def plot_feature_distributions(df: pd.DataFrame = None,
                                scale: bool = False,
                               feature_range: tuple = (-1,1),
                               figsize: tuple = (12,4)) -> None:
    if scale:
        scaler = preprocessing.MinMaxScaler(feature_range=feature_range)
        _df = df.copy()
        _df = pd.DataFrame(data=scaler.fit_transform(_df), columns=df.columns)
    else:
        _df = df
    _plt = _df.melt(var_name='Feature', value_name='Normalized')
    plt.figure(figsize=(figsize))
    ax = sns.violinplot(x='Feature', y='Normalized', data=_plt)
    _ = ax.set_xticklabels(_df.keys(), rotation=45)
    plt.title("Normalized Feature Distribution")
    plt.show()
    
    
def plot_loss(history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    #plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_rmse(history):
    plt.plot(history.history['root_mean_squared_error'], label='root_mean_squared_error')
    plt.plot(history.history['val_root_mean_squared_error'], label='val_root_mean_squared_error')
    #plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('RMSE')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
    
    
    
    
    
    
    
    

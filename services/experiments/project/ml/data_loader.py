import os
import pandas as pd
import pickle

class DataLoader:
    @classmethod
    def load(cls, file_path):
        filename, file_extension = os.path.splitext(file_path)
        if 'csv' in file_extension:
            data = pd.read_csv(file_path, encoding = 'utf8')
        elif 'pkl' in file_extension:
            with open(file_path, 'rb') as pickle_file:
                data = pickle.load(pickle_file)
        else:
            raise Exception("Unsupported file extension. Data Cannot be loaded.")
        return data

    @classmethod
    def save(cls, file_object, file_path):
        filename, file_extension = os.path.splitext(file_path)
        if 'pkl' in file_extension :
            with open(file_path, 'wb') as handle:
                pickle.dump(file_object, handle)
        else:
            raise Exception("Unsupported file extension. Data Cannot be loaded.")



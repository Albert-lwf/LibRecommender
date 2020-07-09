import os
import sys
import zipfile
import pickle
import subprocess
from urllib.request import urlretrieve
import tqdm
import numpy as np
import pandas as pd
# from imp import reload
# reload(download_data)


def _download(par_path=None, prompt=True):
    if not os.path.exists(os.path.join(par_path, "ml-1m", "ratings.dat")):
        answered = not prompt
        while not answered:
            print('movielens-1m dataset could not be found. Do you wish to download it? [Y/n] ', end='')
            choice = input().lower()
            if choice in ["yes", "y"]:
                print("Downloading...")
                download_path = os.path.join(par_path, "ml-1m.zip")
                with tqdm.tqdm(unit='B', unit_scale=True) as p:
                    def report(chunk, chunksize, total):
                        p.total = total
                        p.update(chunksize)
                    urlretrieve("http://files.grouplens.org/datasets/movielens/ml-1m.zip",
                                download_path, reporthook=report)
            #    subprocess.call('wget "http://files.grouplens.org/datasets/movielens/ml-1m.zip"', shell=True)
                print("Download Done !")
                print("-" * 20)
                answered = True
            elif choice in ["no", "n"]:
                answered = True
                print("refued to download, then exit...")
            #    sys.exit()
    else:
        print("Dataset already downloaded.")


def _extract_and_preprocess_data(par_path=None, feat=False):
    if not os.path.exists(os.path.join(par_path, "ml-1m")):
        file_path = os.path.join(par_path, "ml-1m.zip")
        if not os.path.exists(file_path):
            raise FileNotFoundError("ml-1m not found...")
        with zipfile.ZipFile(file_path, 'r') as f:
            f.extractall(par_path)
        print("Extract Zipfile Done !")
    #   os.remove(file_path)

    if feat and not os.path.exists(os.path.join(par_path, "ml-1m", "merged_data.csv")):
        ratings = pd.read_csv(os.path.join(par_path, "ml-1m", "ratings.dat"), sep="::",
                              usecols=[0, 1, 2, 3], names=["user", "item", "rating", "time"])
        users = pd.read_csv(os.path.join(par_path, "ml-1m", "users.dat"), sep="::",
                            usecols=[0, 1, 2, 3], names=["user", "gender", "age", "occupation"])
        items = pd.read_csv(os.path.join(par_path, "ml-1m", "movies.dat"), sep="::",
                            usecols=[0, 2], names=["item", "genre"])
        items["genre1"], items["genre2"], items["genre3"] = zip(*items["genre"].apply(split_genre))
        items.drop("genre", axis=1, inplace=True)

        data = pd.merge(ratings, users, on="user")
        data = pd.merge(data, items, on="item")

    #    user_unique = np.unique(data.user.values)
    #    user_id_map = dict(zip(user_unique, np.arange(len(user_unique))))
    #    data["user"] = data["user"].map(user_id_map)

    #    item_unique = np.unique(data.item.values)
    #    item_id_map = dict(zip(item_unique, np.arange(len(item_unique))))
    #    data["item"] = data["item"].map(item_id_map)

        data.to_csv(os.path.join(par_path, "ml-1m", "merged_data.csv"), index=False, header=False)
        print("Merge Data Done !")


def prepare_data(par_path=None, feat=False, data="ml-1m"):
    if par_path is None:
        par_path = os.path.join(os.path.expanduser("~"),  ".libreco_data")
    if not os.path.exists(par_path):
        os.makedirs(par_path)
    _download(par_path)
    _extract_and_preprocess_data(par_path, feat)


def split_genre(line):
    genres = line.split("|")
    if len(genres) == 3:
        return genres[0], genres[1], genres[2]
    elif len(genres) == 2:
        return genres[0], genres[1], "missing"
    elif len(genres) == 1:
        return genres[0], "missing", "missing"
    else:
        return "missing", "missing", "missing"







import os
import numpy as np
import pandas as pd
from recomender import *

import seaborn as sns
import plotly.express as px 
import matplotlib.pyplot as plt 

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist

import regex
import warnings
warnings.filterwarnings("ignore")

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from collections import defaultdict
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib

import spotipy
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict


# initializing the standard scaler
standard_scaler = StandardScaler()

# reading the data from tracks data
#data = pd.read_csv("tracks.csv")

# filtering the tracks to have only 3 features
#tracks_data = data[["danceability", "energy", "tempo"]]


#tracks_data = tracks_data[:-1]



# Initializing and fitting the data on normalized data using no. of clusters as 10
#kmeans = KMeans(n_clusters=10, random_state=0).fit(tracks_data_normlaized)

# store the clustered data
#clustered_data = kmeans.predict(tracks_data_normlaized)
redirect_uri = "http://localhost:5001/callback"
f = open("keys.txt",'r')
client_id = f.readline().strip()
client_secret = f.readline().strip()
token = util.prompt_for_user_token(scope= 'user-library-read',client_id=client_id, client_secret= client_secret,redirect_uri = redirect_uri) 
sp = spotipy.Spotify(auth = token)


# method to find the song data using spotify api using name and year
def find_song(name, year):
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']

    # get all the features of the song using track id
    audio_features = sp.audio_features(track_id)[0]

    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

   # create song data dictionary with features and their values
    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data)



# getting the song data from song
def get_song_data(song, spotify_data):
    
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name'])].iloc[0]
        return song_data
    
    except IndexError:
        return find_song(song['name'], song['year'])
 
    # taking the song list and returning the mean values of those songs in vector form
def get_mean_vector(song_list, spotify_data,relevant_cols):
    
    song_vectors = []
    # for each song in list
    for song in song_list:
        # get song data from song
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            print('Warning: {} does not exist in Spotify or in database'.format(song['name']))
            continue

        # taking relevant columns and forming a vector
        song_vector = song_data[relevant_cols].values
        # creating a list of song vectors
        song_vectors.append(song_vector)  
    # making a matrix from song vectors
    song_matrix = np.array(list(song_vectors))

    # returning the mean of the song matric
    return np.mean(song_matrix, axis=0)


'''method to flatten out the list of songs into a single dictionary with keys as 'name' and 'year' 
  and their values as list '''
def flatten_dict_list(dict_list):
    
    # creating empty dict with keys as 'name' and 'year'
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    
    # creating lists of values for their keys
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict



def filter_non_english(text):
    text = str(text)
    # replace non-English characters with an empty string
    return text.isascii()





# main method which returns the songs similar to the given songs
def recommend_songs( song_list, spotify_data, n_songs=10):

    print("\n \n \n \n \n ")
    print("Song_list")
    print(song_list)

    scaler = standard_scaler

    # flatten the given song list to single dictionary
    metadata_cols = ['name', 'artists','id']
    song_dict = flatten_dict_list(song_list)
    
#relevant columns
    relevant_cols = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 
                     'instrumentalness', 'liveness', 'valence', 'tempo']

    #pca = PCA(n_components=2)

    
    #spotify_data_pca = pca.fit_transform(spotify_data)

    #song_list_pca = pca.transform(song_list)

    # scale our whole spotify songs training data
    scaled_fit = scaler.fit_transform(spotify_data[relevant_cols])
    

    # Get the mean song vector of the given song list
    song_center = get_mean_vector(song_list, spotify_data,relevant_cols)

    # scale the mean song vector and reshape it
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))

    # Calculate cosine distances between the mean song vector and the spotify database
    # cosine distances is a measure to check how similar the vectors are
    distances = cdist(scaled_song_center, scaled_fit, 'cosine')

    # sort the vectors in ascneding format 
    index = list(np.argsort(distances)[0])
    
    print(index)

    # find songs in spotify database from the indices
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(set(song_dict['name']))]

    # filter non-English songs
    rec_songs = rec_songs[rec_songs['name'].apply(lambda x: filter_non_english(x))]

    calculateMetrics(rec_songs[metadata_cols].to_dict(orient='records')[:10])

    return rec_songs[metadata_cols].to_dict(orient='records')[:n_songs]



def calculateMetrics(rec_songs):

    print(rec_songs)
    sumPop = 0
    longTail = 0
    for track in rec_songs:
        song = sp.track(track["id"])
        popularity = song["popularity"]
        if popularity < 60:
            longTail +=1
        
        sumPop += popularity

    print("\n \n \n")
    print(sumPop/10)
    print(longTail/10)


    return 









    recommend_songs([{'name': 'Gore', 'year':2018},
                {'name': 'Better Now', 'year': 2018},
                {'name': 'Do What I Want', 'year': 2022},
                {'name': 'Knock Down Ginger', 'year': 2020},
                {'name': 'Counting Stars', 'year': 2013}],  data)
    



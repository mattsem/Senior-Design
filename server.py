import spotipy
import json
from recomender import *
import pandas as pd
import urllib.parse
import ast
#import libraries


#import flask tools and spotipy API
from flask import Flask, render_template, redirect, request, jsonify
from spotipy import util

app = Flask(__name__)
token = None
sp = None

#read in downloaded track info - presaved for responsiveness
data = pd.read_csv("tracks.csv")

#defined track data class
class Track:
    def __init__(self, name, artist, songID):
        name
        artist
        songID

#root page backend
@app.route('/')
def index():
    #determine if logged in
    login = request.values.get('login', False)
    savedTracks = request.values.get('savedTracks',None)
    
    #replace quotes
    if savedTracks is not None:
        savedTracks.replace("'",'"')
        #print(savedTracks)
        savedTracks = ast.literal_eval(savedTracks)
    
    #return the page with login data
    return render_template('index.html', login = login, savedTracks = savedTracks)


#page shown once logged in
@app.route('/login/')
def login():
    redirect_uri = "http://localhost:5001/callback"
    #username = "12128523243"
    #spotify login credentials
    global sp

   #read keys from file for privacy
    f = open("keys.txt",'r')
    client_id = f.readline().strip()
    client_secret = f.readline().strip()
    #print(client_id)
    #print(client_secret)

    token = util.prompt_for_user_token(scope= 'user-library-read',client_id=client_id, 
                                       client_secret= client_secret,redirect_uri = redirect_uri) 
    sp = spotipy.Spotify(auth = token)


    #return redirect('/?login=True')


#@app.route('/savedOrTop')
#def savedOrTop():

    selection = request.args.get('savedOrTop')
    print(selection)
    #if(selection == 'top'):
        #savedTracks = sp.current_user_top_tracks(limit = 10)

    #elif(selection == 'saved'):
    
    #grab users saved tracks
    savedTracks = sp.current_user_saved_tracks(limit = 15)
  
    #can remove - saves tracks
    f = open("savedTracks.json", "w")
    str = json.dumps(savedTracks)
    f.write(str)
    f.close()


    #format track list
    print(savedTracks)
    tracks = {}
    tracks["items"] = []
    for item in savedTracks["items"]:
        trackDict = {}
        trackDict["name"] = item["track"]["name"].replace('&','%26')
        trackDict["artist"] = item["track"]["artists"][0]["name"].replace('&','%26')
        trackDict["songID"] = item["track"]["id"]
        tracks["items"].append(trackDict)
    

    #need at least song name,artist, and id
    print("\n \n \n \n \n \n")
    print("Tracks")
    print(tracks)

    return redirect('/?login=True&savedTracks=%s' % tracks)



    
#generates reccommendations based on seedList
@app.route('/createPlaylist', methods= ['POST'])
def createPlaylist():
#python goes here
    seedList = request.get_json()['seedList']

    """
    baseline = sp.recommendations(seed_tracks = seedList, limit = 10)
    print("baseline:")
    
    sumPop = 0
    longTail = 0
    for track in baseline:
        popularity = track["popularity"]
        if popularity < 60:
            longTail +=1
        
        sumPop += popularity


    print("\n \n \n")
    print(sumPop/10)
    print(longTail/10)
    """


    seedTracks = []
    print("\n \n \n \n \n \n")
    print("Seedlist")
    for item in seedList:
        print(item)
        seedTracks.append(sp.track(item))

    print("\n \n \n \n \n \n")
    print("SeedTracks")
    print(seedTracks)

#get seed list, look up song data, pass to recommend songs
#format to recommend input dict [{'name':'name','year':'year'}]

    seedListDict = []
    for track in seedTracks:
        seedDict = {}
        seedDict['name'] = track["name"]
        seedDict['year'] =  int(track["album"]["release_date"][:4])
        seedListDict.append(seedDict)
    
    print("\n \n \n \n \n \n")
    print("SeedListDict")
    print(seedListDict)   



#call recomender.py here
    recommendedList = recommend_songs(seedListDict,data)

    print("\n \n \n \n \n \n")
    print("recommendedList")
    print(recommendedList)


    #look up recommended list features

    #recommendedTracks = []
    #for song in recommendedList:
    #recommendedTracks.append(sp.track(song['id']))

        


    #print("\n \n \n \n \n \n")
    #print("recommendedTracks")
    #print(recommendedTracks)


    #return jsonify(recommendedList)
    return jsonify(recommendedList)



#get song data for given songID
@app.route('/retrieveSongData', methods= ['POST'])
def retrieveSongData():
    data = request.get_json()
    songID = data['id']
    
    songData = sp.audio_features(songID)
    songData.append(sp.track(songID)["name"])
    songData.append(sp.track(songID)["artists"][0]["name"])

    return jsonify(songData)




#backend for search bar

@app.route('/search/', methods = ['GET'])
def search():
    searchTerm = request.values.get('search')
    result = sp.search(q='track:' +searchTerm, type='track', limit = 1)

    print(result)

    track = result['tracks']['items'][0]

    print("\n \n \n \n \n \n")
    print(track['id'])


    
    return jsonify(track)

if __name__ == '__main__':
    app.run(debug=True)
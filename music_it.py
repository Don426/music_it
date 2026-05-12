# CLI Python Music Library Manager enabling music searches through iTunes API 
# and Favourites/Library curation, making use of CSV storage

import csv
import json
import os
import requests
import sys


SONG_REQ_LIMIT = 15

playlists = ["Favourites"]

def main():
    while True:
        # Extract user action, handle exiting and termination of program through home_menu function
        choice = home_menu()

        #if user wants to search
        if choice == "add songs":

            #show search menu and return user choice of search
            search_choice = search_menu()

            #if user selects 'back', restart main loop
            if search_choice == "back":
                continue

            #if user chooses search by song name, get song string and call song search api function
            elif search_choice == "song name":
                #get song choice from user
                song = input("Search for song: ")
                songs = request_song(song)
                action = int(input("Enter a number to save a song to your library, or 0 to go back: "))
                if action == 0:
                    continue
                elif action in range(1, SONG_REQ_LIMIT + 1):
                    save_to_library(songs[action - 1])

            # If user chooses to search by artist, the program will extract the artist name and call api function
            elif search_choice == "artist/band name":
                artist = input("Search for Artist: ")
                request_artist(artist)

        elif choice == "my library":
            # Show library to user




# API request function for a search by song action
def request_song(song_search):
    songs = []
    try:
        params = {
            "entity" : "song",
            "limit" : SONG_REQ_LIMIT,
            "term" : song_search
        }
        response = requests.get(f"https://itunes.apple.com/search", params=params)
        response.raise_for_status()
    except requests.HTTPError:
        print("Invalid Request")
    else:
        response_dict = response.json()
        print(json.dumps(response_dict, indent=2))
        results = response_dict["results"]

        i = 0
        for track in results:
            i += 1
            name = track["trackName"]
            artist = track["artistName"]
            id = track["trackId"]
            genre = track["primaryGenreName"]
            album = track["collectionName"]
            print(f"{i}. {name} - {artist}")
            songs.append({
                            "id" : id,
                            "name" : name,
                            "artist" : artist,
                            "album" : album,
                            "genre" : genre
                        })
        
        return songs


# API request function for calling artist information
def request_artist(artist_name):
    try:
        params = {
            "entity" : "musicArtist",
            "limit" : 5,
            "term" : artist_name
        }
        response = requests.get(f"https://itunes.apple.com/search", params=params)
        response.raise_for_status()
    except requests.HTTPError:
        print("Invalid Request")
    else:
        response_dict = response.json()
        results = response_dict["results"]

        i = 0
        for artist in results:
            i += 1
            name = artist["artistName"]
            print(f"{i}. {name}")

        
def save_to_library(song):
    fieldnames = ["id", "name", "artist", "album", "genre", "playlist" ]
    # Determine playlist to save song to
    print("Save To:\n")
    i = 0
    for playlist in playlists:
        i += 1
        print(f"{i}. {playlist}")

    action = int(input(f"Enter a number to save {song['name']} to a playlist,"
                   " or 0 to create a new playlist"))
    
    # Save it to song
    if action == 0:
        # Create new playlist
        save_to_library(song)
    elif action in range(1, len(playlists) + 1):
        # Determine if file exists (if not write file headers)
        song["playlist"] = playlists[action - 1]
        file_exist = os.path.exists("library.csv")
        # open/create file
        with open("library.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exist:
                writer.writeheader()
            
            writer.writerow(song)
    else:
        print("Invalid Input")
                


# Searching Sub-Menu functionality
def search_menu():
    #dictionary for easy menu changes
    menu = {
        "1" : "Song Name",
        "2" : "Artist/Band Name",
        "3" : "Back",
        "4" : "Exit"
    }
    #print menu
    print("Search Song by: ")

    for num, choice in menu.items():
        print(num, choice, sep=". ")

    while True:
        try:
            #get search choice
            choice = int(input("\nEnter Choice (Number): "))
        except ValueError: #handle exception of incorrect input
            print("Please enter a number.")
            continue
        except EOFError: #exit on ctrl+z
            sys.exit()
        else:
            match choice:
                case 1 | 2:
                    #return choice value if wanting to search
                    return menu[str(choice)].lower()
                case 3:
                    return "back"
                case 4:
                    sys.exit()
                case _:
                    #handle illogical input
                    print("Invalid Choice. Try again.")
                    continue


# Main Menu Functionality
def home_menu(): #Shows home interface
    print("\n#_#__#__#___#_____- MUSIC IT -_____#___#__#_#\n")

    #dictionary of menu items for easy managing
    menu = {
        "1":"My Library",
        "2":"Add Songs",
        "3":"Exit"
    }
    #print dictionary items
    for num, choice in menu.items():
        print(num, choice, sep=". ")

    while True:
        try:
            choice = int(input("\nEnter Number: "))
        except ValueError:
            pass
            continue
        except EOFError: #catches ctrl+z eoferror
            sys.exit()
        else:
            if choice != 3: 
                return menu[str(choice)].lower() #return chosen menu item or exit if it is chosen
            else:
                print("\nExiting....\n")
                sys.exit()


if __name__ == "__main__":
    main()
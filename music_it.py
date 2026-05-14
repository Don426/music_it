# CLI Python Music Library Manager enabling music searches through iTunes API 
# and Favourites/Library curation, making use of CSV storage

import csv
import json
import os
import requests
import sys


SONG_REQ_LIMIT = 15
ARTIST_REQ_LIMIT = 5

library = ["Favourites"]

def main():
    # Populate global playlist array
    populate_library_playlists()
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
                song = input("\nSearch for song: ")
                songs_results = request_song(song, False)
                action = int(input("\nEnter a number to save a song to your library, or 0 to go back: "))
                if action == 0:
                    continue
                elif action in range(1, SONG_REQ_LIMIT + 1):
                    save_to_library(songs_results[action - 1])

            # If user chooses to search by artist, the program will extract the artist name and call api function
            elif search_choice == "artist/band name":
                artist_search = input("Search for Artist: ")
                artists = request_artist(artist_search)
                artist_choice = int(input("\nEnter a number to view an artists songs, or 0 to go back: "))
                if artist_choice == 0:
                    continue
                elif artist_choice in range(1, ARTIST_REQ_LIMIT + 1):
                    # UI heading
                    print(f"\n{artists[artist_choice - 1]}\n________________________")
                    # Empty/Reassign songs list
                    songs_results = []
                    # API request for songs by chosen artist
                    songs_results = request_song(artists[artist_choice-1], True)
                    action = int(input("\nEnter a number to save a song to your library, or 0 to go back: "))
                    if action == 0:
                        continue
                    elif action in range(1, SONG_REQ_LIMIT + 1):
                        save_to_library(songs_results[action - 1])


        elif choice == "my library":
            # Show library to user
            # Playlists: List of tuples (playlist_name, song_count)
            playlists = get_library_overview()
            display_library(playlists)
            
            # Prepare for input to view playlists or back
            library_action = int(input("\nEnter a number to view a playlist, or 0 to go back: "))
            if library_action == 0:
                continue
            else:
                playlist_name = playlists[library_action - 1][0]
                # Songs: List of tuples (song_name, artist)
                playlist_songs = get_playlist(playlist_name)
                display_playlist(playlist_name, playlist_songs)

                # Retrieve action inside library i f playlist is populated
                if playlist_songs:
                    library_action = int(input("\nEnter a number to manage a song, or 0 to go back: "))
                    if library_action == 0: # Back
                        continue
                    else:
                        song_action = song_management_menu(playlist_songs[library_action - 1])
                        if song_action == 0: # Back
                            continue
                        elif song_action == 1: # Remove song
                            # Remove song from playlist
                            remove_song(playlist_songs[song_action - 1][0])
                # If playlist is empty allow user to go back only, to avoid out of range errors
                elif input("Press Enter to Go Back. "):
                    continue
                            
            



# API request function for a search by song action
def request_song(song_search, artist_search):
    songs = []
    if artist_search:
        params = {
            "term" : song_search,
            "entity" : "song",
            "attribute": "artistTerm",
            "limit" : SONG_REQ_LIMIT
        }
    else:
        params = {
            "term" : song_search,
            "entity" : "song",
            "attribute" : "songTerm",
            "limit" : SONG_REQ_LIMIT
        }
    try:
        response = requests.get(f"https://itunes.apple.com/search", params=params)
        response.raise_for_status()
    except requests.HTTPError:
        print("Invalid Request")
    else:
        response_dict = response.json()
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
            "limit" : ARTIST_REQ_LIMIT,
            "term" : artist_name
        }
        response = requests.get(f"https://itunes.apple.com/search", params=params)
        response.raise_for_status()
    except requests.HTTPError:
        print("Invalid Request")
    else:
        response_dict = response.json()
        results = response_dict["results"]

        artists = []
        i = 0
        for artist in results:
            i += 1
            name = artist["artistName"]
            artists.append(name)
            print(f"{i}. {name}")

    return artists

        
def save_to_library(song):
    fieldnames = ["id", "name", "artist", "album", "genre", "playlist" ]
    # Determine playlist to save song to
    print("Save To:\n")
    i = 0
    for playlist in library:
        i += 1
        print(f"{i}. {playlist}")

    action = int(input(f"\nEnter a number to save {song['name']} to a playlist,"
                   " 0 to create a new playlist, or -1 to go back: "))
    
    # Save it to song
    if action == 0:
        # Create new playlist
        library.append(input("\nPlaylist Name: "))

        # Call function again
        save_to_library(song)
    elif action in range(1, len(library) + 1):
        # Determine if file exists (if not write file headers)
        song["playlist"] = library[action - 1]
        file_exist = os.path.exists("library.csv")
        # open/create file
        with open("library.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exist:
                writer.writeheader()
            
            writer.writerow(song)
    elif action == -1:
        return
    else:
        print("Invalid Input")


def get_library_overview():
    # Determine playlists and sizes and return list of tuples with playlist:song_count key-value pairs
    if os.path.exists("library.csv"):
        playlists = []
        # Loop through playlists
        for playlist in library:
            # Initialise song count
            count = 0

            # Loop through library.csv
            with open("library.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["playlist"] == playlist:
                        count += 1
            # Create new playlist tuple
            playlists.append((playlist, count))
        
        return playlists
    else:
        return [("Favourites", 0)]


def display_library(playlists):
    print("\nLibrary \n_____________________\n")
    i = 1
    for playlist, song_count in playlists:
        print(f"{i}. {playlist:<20} ({song_count} songs)")
        i += 1
    print()

def get_playlist(playlist_name):
    # Loop through CSV, return list of lists (song_id, song_name, artist)
    songs = []
    if os.path.exists("library.csv"):
        with open("library.csv") as file:
            reader = csv.DictReader(file)

            for song in reader:
                if song["playlist"] == playlist_name:
                    songs.append([song["id"], song["name"], song["artist"]])

        return songs

    else: 
        print("Error retrieving library")
        return []

def display_playlist(playlist_name, songs):
    # Ensure the playlist is populated with any number of songs
    if songs:
        # Loop through list of song tuples and display
        print(f"\n{playlist_name}\n___________________")
        print(f"{'No.':<5} {'Song':<40} {'Artist'}")
        i = 1
        for id, song, artist in songs:
            print(f"{i}{'.':<5}{song:<40} {artist}")
            i += 1
    # However if empty, handle the exception neatly
    else:
        print(f"\n{playlist_name}\n___________________")
        print("Empty Playlist\n")

        

def song_management_menu(song_details):
    print(f"{song_details[1]} - {song_details[2]}")
    print("1. Remove from Playlist\n")
    action = int(input("Enter your choice (number), or 0 to go back: "))
    return action


def remove_song(song_id):
    lines = []
    with open("library.csv") as file:
        reader = csv.DictReader(file)
        # Get fieldnames for writing
        fieldnames = reader.fieldnames
        # Loop through file copying only songs not being deleted
        for line in reader:
            if not (line["id"] == song_id):
                lines.append(line)

    # Rewrite file without the removed song
    with open("library.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lines)

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
    print("\nSearch Song by: ")

    for num, choice in menu.items():
        print(num, choice, sep=". ")

    while True:
        try:
            #get search choice
            choice = int(input("\nEnter Choice (Number): "))
        except ValueError: #handle exception of incorrect input
            print("\nPlease enter a number.")
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
                    print("\nInvalid Choice. Try again.")
                    continue


# Main Menu Functionality
def home_menu(): #Shows home interface
    print("\n__________________ MUSIC IT __________________\n")

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
            choice = int(input("\nEnter Number or 3 to Exit: "))
        except ValueError:
            pass
            continue
        except EOFError: #catches ctrl+z eoferror
            sys.exit()
        else:
            if choice != 3: 
                return menu[str(choice)].lower() #return chosen menu item or exit if it is chosen
            else:
                print("\nExited\n")
                sys.exit()


def populate_library_playlists():
# Populates global array of active playlists for easier access during runtime

    if os.path.exists("library.csv"):
        with open("library.csv") as file:
            reader = csv.DictReader(file)
            for line in reader:
                # Populates array with distinct playlist names
                if line["playlist"] not in library:
                    library.append(line["playlist"])
    # If library.csv doesnt exist, it would be the programs first run and there would not be additional playlists yet.           
    
if __name__ == "__main__":
    main()
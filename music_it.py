import requests
import sys

def main():
    while True:
        choice = home_menu()
        #if user wants to search
        if choice == "search":
            #show search menu and return user choice of search
            search_choice = search_menu()
            #if user wants to go back to main menu, restart main loop
            if search_choice == "back":
                continue
            #if user chooses search by song name, get song string and call song search api function
            elif search_choice == "song name":
                #get song choice from user
                song_search = input("Search for song: ")
                request_song(song_search)

def request_song(song_search):
    try:
        response = requests.get(f"https://itunes.apple.com/search/entity=song&limit=15&term={song_search}")
        response.raise_for_status()
    except requests.HTTPError:
        print("Invalid Request")
    else:
        response_dict = response.json()
        print(response_dict)

def search_menu():
    #dictionary for easy menu changes
    menu = {
        "1" : "Song Name",
        "2" : "Artist/Band Name",
        "3" : "Back",
        "4" : "Exit"
    }
    #print menu
    for num, choice in menu.items():
        print(num, choice, sep=". ")

    while True:
        try:
            #get search choice
            choice = int(input("\nEnter Choice (Number): "))
        except ValueError: #handle exception of incorrect input
            "Please enter a number."
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

def home_menu(): #Shows home interface
    print("\n#_#__#__#___#_____- MUSIC IT -_____#___#__#_#\n")

    #dictionary of menu items for easy managing
    menu = {
        "1":"View My Library",
        "2":"Search",
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

main()
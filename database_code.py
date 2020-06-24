from pymongo import MongoClient
from py2neo import Graph
import redis
import secrets
import json
import time
import random
import string
import time
from datetime import datetime

try:
    conn = MongoClient()
    print("Connected successfully MongoDB!!!")
except:
    print("Could not connect to MongoDB")

# connection to Redis database

try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    print("Connected successfully Redis!!!")
except:
    print("Could not connect to Redis")

# connection to neo4j database
try:
    graph = Graph(host='localhost', port=7687, password="1234")
    print("Connected successfully Neo4J!!!")
except:
    print("Could not connect to Neo4J")

print("Please Choose your Option below:")
print("Are you a New Customer here? Please type: Yes otherwise No ")
new_user = input("Enter your choice here: ")


def random_code(stringLength):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))


def new_user_registration():
    db = conn.myshows_db
    global collection_new_user
    collection_new_user = db.new_login
    global collection_reward
    collection_reward = db.reward
    global new_User_Name
    global new_User_Password
    global new_First_Name
    global new_Last_Name
    global new_Email_id
    global new_Phone_Number
    global new_Date_of_Birth
    global new_Place_of_Birth
    global referral_code
    global first_name
    global last_name
    global card_number
    global expiration_date
    cash_reward = 0
    updated_cash_reward = 0

    new_User_Name = input("Enter Your User Name: ")
    new_User_Password = input("Enter Your Password: ")
    new_First_Name = input("Enter Your First Name: ")
    new_Last_Name = input("Enter Your Last Name: ")
    new_Email_id = input("Enter Your Email Address: ")
    new_Phone_Number = input("Enter Your Phone Number: ")
    new_Date_of_Birth = input("Enter Your Date of Birth: ")
    new_Place_of_Birth = input("Enter Your Place of Birth: ")
    print("Please enter your card details to get a free trial of one Month:")
    first_name = input("Enter the first name on your card: ")
    last_name = input("Enter the last name on your card: ")
    card_number = input("Enter Your 16 digit card number: ")
    length = len(card_number)
    if length >= 16:
        expiration_date = input("Enter Your Expiration Date of card: ")
    else:
        print("Please enter correct 16 digit card number:")
        card_number = input("Enter Your 16 digit card number: ")
        expiration_date = input("Enter Your Expiration Date of card: ")

    referral_code = new_User_Name + random_code(6)
    print("Your referral code is:", referral_code)

    document1 = {
        "user_name": new_User_Name,
        "Reward value": cash_reward,
        "my_referral_code": referral_code,
        "referred_with_code": None,
        "referred_by_code": None
    }
    collection_reward.insert_one(document1)

    referral_code_input = input("Do you have referral code? If yes please type Yes:")
    if referral_code_input == "Yes":
       fun_referral_code()

    else:
        print("You have not earned cash points but your account has been created")
        collection_new_user.insert_many(
            [
                {
                    "new_UserName": new_User_Name,
                    "new_Password": new_User_Password,
                    "new_First_Name": new_First_Name,
                    "new_Last_Name": new_Last_Name,
                    "new_Email_id": new_Email_id,
                    "new_Phone_Number": new_Phone_Number,
                    "new_Date_of_Birth": new_Date_of_Birth,
                    "new_Place_of_Birth": new_Place_of_Birth,
                    "random_code": referral_code,
                    "first_name": first_name,
                    "last_name": last_name,
                    "card_number": card_number,
                    "expiration_date": expiration_date,
                    "user_type": "NonePremium"
                },
            ]
        )

        query = """
                MERGE (u:USER{username: \"""" + new_User_Name + """\"})
    
                    """
        graph.run(query)


def fun_referral_code():
    friends_refer_id = input("Enter referrer's code:")
    data_referrer = collection_reward.find_one({"my_referral_code": friends_refer_id})
    # print(data_referrer)
    referred_by_usr = input("Enter the username of the user who referred you?")
    if data_referrer['user_name'] == referred_by_usr:
        print("VERIFIED!!!")
        query = """create(u:user{username:\"""" + new_User_Name + """\"})"""
        graph.run(query)
        collection_new_user.insert_many(
            [
                {
                    "new_UserName": new_User_Name,
                    "new_Password": new_User_Password,
                    "new_First_Name": new_First_Name,
                    "new_Last_Name": new_Last_Name,
                    "new_Email_id": new_Email_id,
                    "new_Phone_Number": new_Phone_Number,
                    "new_Date_of_Birth": new_Date_of_Birth,
                    "new_Place_of_Birth": new_Place_of_Birth,
                    "random_code": referral_code,
                    "referred_by_code": friends_refer_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "card_number": card_number,
                    "expiration_date": expiration_date,
                    "user_type": "NonePremium"
                },
            ]
        )

        # Fetching id of person using referral code
        data_referree = collection_reward.find_one({"my_referral_code": referral_code})
        new_reward_value_referree = data_referree['Reward value']
        get_cash_update_referree = new_reward_value_referree + 50
        # print(get_cash_update_referree)
        get_id_referree = data_referree['_id']
        # print(get_id_referree)

        # fetching id of person who has given referral code
        get_id_referrer = data_referrer['_id']
        get_name_referrer = data_referrer['user_name']
        new_reward_value_referrer = data_referrer['Reward value']
        get_cash_update_referrer = new_reward_value_referrer + 50
        # print(get_cash_update_referrer)
        # print(get_name_referrer)
        # print(get_id_referrer)

        # updating info of who is using referral code
        collection_reward.replace_one({"_id": get_id_referree},
                                      {"user_name": new_User_Name, "Reward value": get_cash_update_referree,
                                       "my_referral_code": referral_code,
                                       "referred_by_code": friends_refer_id})

        # Updating info of who has given referral code
        collection_reward.replace_one({"_id": get_id_referrer},
                                      {"user_name": get_name_referrer, "Reward value": get_cash_update_referrer,
                                       "my_referral_code": friends_refer_id,
                                       "referred_with_code": friends_refer_id})

        # document1 = {
        #    "user_name": new_User_Name,
        #   "Reward value": updated_cash_reward,
        #  "my_referral_code": referral_code,
        # "referred_with_code": None,
        # "referred_by_code": friends_refer_id
        # }
        # collection_reward.insert_one(document1)

        # document2 = {
        #   "user_name": referred_by_usr,
        #  "Reward value": updated_cash_reward,
        # "my_referral_code": friends_refer_id,
        # "referred_with_code": friends_refer_id,
        #     "referred_by_code": None
        # }
        # collection_reward.insert_one(document2)
        print("VERIFIED!!! and also earned cashpoints ")

        # query = """
        #     MERGE (u:USER{username: \"""" + new_User_Name + """\"})
        #
        #         """
        # graph.run(query)
        #
        # query = """
        #     MERGE (u:USER{username: \"""" + get_name_referrer + """\"})
        #
        #         """
        # graph.run(query)
        #
        # query = """
        #     match (u1:USER{username: \"""" + new_User_Name + """\"})
        #     match (u2:USER{username: \"""" + get_name_referrer + """\"})
        #     merge (u1) -[:REFERRED_BY{referralCode: \"""" + friends_refer_id + """\"}] ->  (u2) return *
        #
        #         """
        # graph.run(query)

        query = """ 
            merge(u1: USER {username: \"""" + new_User_Name + """\"})
            merge(u2: USER {username: \"""" + get_name_referrer + """\" })
            merge(u1) - [: REFERRED_BY{referralCode: \"""" + friends_refer_id + """\"}] ->  (u2)
            return (u1) - - (u2)

                """
        graph.run(query)

    else:
        print("Username or Referral code incorrect. ")
        recursive_input = input("Please enter 'Yes' if you would like to try again, or 'No' to quit reward bonus:")
        if recursive_input == "No":
            collection_new_user.insert_many(
                [
                    {
                        "new_UserName": new_User_Name,
                        "new_Password": new_User_Password,
                        "new_First_Name": new_First_Name,
                        "new_Last_Name": new_Last_Name,
                        "new_Email_id": new_Email_id,
                        "new_Phone_Number": new_Phone_Number,
                        "new_Date_of_Birth": new_Date_of_Birth,
                        "new_Place_of_Birth": new_Place_of_Birth,
                        "random_code": referral_code,
                        "first_name": first_name,
                        "last_name": last_name,
                        "card_number": card_number,
                        "expiration_date": expiration_date,
                        "user_type": "NonePremium"
                    },
                ]
            )


            query = """ 
                MERGE (u:USER{username: \"""" + new_User_Name + """\"})
    
                    """
            graph.run(query)
            print("You have not earned cash points but your account has been created")
            exit()
        else:
            fun_referral_code()
    exit()

login_User_Name = ""
ur_id = ""


def login_opt():
    db = conn.myshows_db
    collection_old = db.new_login
    global login_User_Name
    global ur_id

    login_User_Name = input("Enter Your User Name: ")
    login_Password = input("Enter Your Password: ")
    data = collection_old.find_one({"new_UserName": login_User_Name})
    if not data:
        print("User does'nt exists. Login again with correct Username")
        login_opt()
    else:      
        print("username exist")
        passw = data['new_Password']
        if passw== login_Password :
            print("password matched")
            #print(usertyp)
            print("Login successful")
        else:
            print("password mismatched. Login again with correct password")
            login_opt()
        
        usertype = data['user_type']
        if usertype == "Premium":
            premiummenu()
        elif usertype == "NonePremium":
            menu()
        else:
            tvmenu()

def premiummenu():
    print("Please enter which option you want to choose")
    print("1. Enter a watch Party")
    print("2. Follow a friend")
    print("3. Create a watch Party")
    print("4. Search a TV show to watch")
    print("5. List of shows I have watched")
    print("6. My liked shows")
    print("7. My disliked shows")
    print("8. My recommendations")
    print("9: Search TV shows based upon Genre and Rating")
    print("10: View search history")
    print("11: Delete search history")
    print("12: Quit/ Logout")
    opt = input("Enter which option you want to choose:")
    if opt == "1":
        watchparty()
    elif opt == "2":
        follow_friend()
    elif opt == "3":
        new_watchparty()
    elif opt == "4":
        watch_show()
    elif opt == "5":
        my_watched_shows()
    elif opt == "6":
        my_liked_shows()
    elif opt == "7":
        my_disliked_shows()
    elif opt == "8":
        my_recommendations()
    elif opt == "9":
        search()
    elif opt == "10":
        search_history()
    elif opt == "11":
        delete_history()
    elif opt == "12":
        quit()
    else:
        print("Wrong Entry")
        
def menu():
    print("1. Upgrade to Premium Content?")
    print("2. Enter a watch Party")
    print("3. Follow a friend")
    print("4. Search a TV show to watch")
    print("5. List of shows I have watched")
    print("6. My liked shows")
    print("7. My disliked shows")
    print("8. My recommendations")
    print("9: Search TV shows based upon Genre and Rating")
    print("10: View search history")
    print("11: Delete search history")
    print("12: Quit/ Logout")
    opt = input("Enter which option you want to choose:")
    if opt == "1":
        premium_payment()
    elif opt == "2":
        watchparty()
    elif opt == "3":
        follow_friend()
    elif opt == "4":
        watch_show()
    elif opt == "5":
        my_watched_shows()
    elif opt == "6":
        my_liked_shows()
    elif opt == "7":
        my_disliked_shows()
    elif opt == "8":
        my_recommendations()
    elif opt == "9":
        search()
    elif opt == "10":
        search_history()
    elif opt == "11":
        delete_history()
    elif opt == "12":
        quit()
    else:
        print("Wrong Entry")


# ---------------------------------------------Author Prajakta----------------------------------------------------

def premium_payment():
    print("Lets check for cash points earned from your account")
    db = conn.myshows_db
    collection_loginp = db.new_login
    collection_rewardp = db.reward
    data_reward = collection_rewardp.find_one({"user_name": login_User_Name})
    reward_value = data_reward['Reward value']
    if reward_value >= 50:
        reward_dec = input(
            "You have sufficient cash points to disburse to enable premium content. Do you want to use it? Please type Yes for the same.")
        if reward_dec == "Yes":
            get_id = data_reward['_id']
            get_cash_update = reward_value - 50
            collection_rewardp.update_one({"_id": get_id}, {"$set": {"Reward value": get_cash_update}})
            data_update_premium = collection_loginp.find_one({"new_UserName": login_User_Name})
            get_premiumid = data_update_premium['_id']
            collection_loginp.update_one({"_id": get_premiumid}, {"$set": {"user_type": "Premium"}})
            print("Hexy!! You are Premium User now")
            print("Cash points left in your Account are:", get_cash_update)
    else:
        security_code = input(
            "You do not have sufficient cash points to disburse. Enter Your 3 digit security number for further payment: ")
        length = len(security_code)
        if length == 3:
            data_update_premium = collection_loginp.find_one({"new_UserName": login_User_Name})
            print(data_update_premium)
            get_premiumid = data_update_premium['_id']
            print(get_premiumid)
            collection_loginp.update_one({"_id": get_premiumid}, {"$set": {"user_type": "Premium"}})
            print("Hexy!! You are Premium User now")
        else:
            print("Please enter 3 digit security number:")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -----------------------------------------------------------Author Prajakta--------------------------------------------------
def follow_friend():
    print("Please enter the username of the User you want to follow :")
    print(login_User_Name)
    username = input("")
    query = """match(u:USER{username:\"""" + username + """\"})
        return u.username"""
    result = graph.run(query)
    for username in result:
        print("User found in our System. Do you want to follow the user?")
    follow = input("")
    if follow == "yes":
        query = """ match(u:USER{username:\"""" + username['u.username'] + """\"})
            match(a:USER{username:\"""" + login_User_Name + """\"})
            merge (a)-[x:follows]->(u)
            """
        graph.run(query)
        print("You have successfully followed the User.")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        premiummenu()
    else:
        print("Closing the application!")
        quit()


def enterwatch_party():
    print("Want to check for your FriendList? Please Enter Yes")
    enterwp = input("")
    if enterwp == "Yes":
        query = """
        match(u:USER{username:\"""" + login_User_Name + """\"})-[x:follows]->(a:user)
        return a.username
        """
        result = graph.run(query).data()
        print(result)


# ----------------------------------------------------------Author Prajakta-----------------------------------------------
def new_watchparty():
    global login_room_User_Name
    invitation_code = secrets.token_hex(3)
    login_room_User_Name = input("Enter Your User Name: ")
    roomname = login_room_User_Name + "_room"
    r.hset("watchrooms_new", login_room_User_Name, roomname)
    watchrooms = r.hgetall("watchrooms_new")
    print("Your watchroom:", watchrooms)
    r.hset("room_details", roomname, invitation_code)
    Allrooms = r.hgetall("room_details")
    print("Room details with RoomName and Invitation code:", Allrooms)


# -----------------------------------------------------Author Prajakta------------------------------------------------------
def watchparty():
    print("Want to check for your FriendList? Please Enter Yes")
    enterwp = input("")
    if enterwp == "yes":
        query = """
        match(u:USER{username:\"""" + login_User_Name + """\"})-[x:follows]->(a:USER)
        return a.username
        """
        result = graph.run(query).data()
        friends = []
        for x in result:
            friends.append(x["a.username"])
        print("Your entire FriendsList is here:", friends)
        for host in friends:
            rooms = r.hget("watchrooms_new", host)
            print("Watchrooms available from your FriendsList:", rooms)
            if not rooms:
                print("none got back")
            else:
                host_name = input("Enter the host name : ")
                host_room = host_name + "_room"
                invite_check = r.hget("room_details", host_room)
                user_code = input("Please enter Invitation Code : ")
                if invite_check == user_code:
                    print("You are in Watch Party")
                    r.sadd(host_room, login_User_Name)
                    print("All members in", host_room, "watchparty are:", r.smembers(host_room))
                    break
                else:
                    print("Not entered")
    else:
        print("You do not have any friends in your")
    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        premiummenu()
    else:
        print("Closing the application!")
        quit()


# -------------------------------------------Author Yash-----------------------------------------------------------------

def watch_show():
    # Fetch TV show titles from Neo4j and insert them in a list shows
    query = "MATCH (tv:SHOW) RETURN tv.title"
    result = graph.run(query).data()
    shows = []
    for x in result:
        shows.append(x["tv.title"])

    watch = input("Do you want to watch a new TV show? type yes or no: ")
    if watch == 'yes':
        print("Select an option from below to watch a TV show:")
        print("1. Select a show from the list of shows")
        print("2. Search a show by its title")
        a = input("Enter 1 or 2: ")
        if a == "1":
            print("Select a TV show from the list below:")

            # Fetch TV show titles from the list shows and provide a numbered list to the user
            for i in shows:
                print(shows.index(i) + 1, end=' ')
                print(i)

            # Variable to store the user input
            select_show = int(input("Watch show number: "))
            if 0 < select_show <= len(shows):
                z = str(shows[select_show - 1])
                print("Selected show is " + z)

                # Query for fetching the TV show as per the user input
                query = """
                        MATCH (tv:SHOW{title:\"""" + z + """\"}) RETURN tv.title
                        """
                result = graph.run(query).data()

                # Compare user input and the data fetched from the database
                if z == result[0].get('tv.title'):
                    print("TV show found")

                    # Query for deleting the recommendation relationship before watching the TV show
                    query = """ 
                            MATCH (tv:SHOW{title:\"""" + z + """\"}) 
                            MATCH (r:RECOMMENDATIONS{owner: \"""" + login_User_Name + """\"})
                            MATCH (tv)-[rel:RECOMMENDED_TO]->(r) 
                            DELETE rel
                            """
                    graph.run(query)

                    # Query for establishing a relationship between user and TV show
                    query = """
                            MATCH (u:USER{username: \"""" + login_User_Name + """\"}) 
                            MATCH (tv:SHOW{title:\"""" + z + """\"}) 
                            MERGE (u)-[:WATCHED]->(tv)
                            RETURN tv.universe
                            """

                    # Universe is returned and stored in a variable to recommend similar shows to the user
                    tv_universe = graph.run(query).data()
                    print("You have watched " + z)
                    print("Universe is " + tv_universe[0].get('tv.universe'))

                    # Query for generating a recommendations node for a user
                    query = """
                            MERGE (r:RECOMMENDATIONS{name: "Recommendations for you", 
                            owner: \"""" + login_User_Name + """\"})
                            MERGE (u:USER{username: \"""" + login_User_Name + """\"})
                            MERGE (u)-[:HAS]->(r)
                            """
                    graph.run(query)

                    # Query for recommending shows to the user
                    query = """
                            MATCH (tv:SHOW{universe: \"""" + tv_universe[0].get('tv.universe') + """\"})
                            MATCH (r:RECOMMENDATIONS{name: "Recommendations for you", 
                            owner: \"""" + login_User_Name + """\"})--(u:USER{username: \"""" + login_User_Name + """\"})
                            WHERE NOT (u)-[:WATCHED]->(tv)
                            MERGE (tv)-[:RECOMMENDED_TO]->(r)
                            """
                    graph.run(query)
                    print("Similar shows has been recommended to you")
            else:
                print("Invalid input")

        elif a == "2":
            print("You can search a show by its title")
            show_title = input("Enter the title of a show: ")
            if show_title in shows:

                # Query for fetching the TV show as per the user input
                query = """
                        MATCH (tv:SHOW{title:\"""" + show_title + """\"}) RETURN tv.title
                        """
                result = graph.run(query).data()

                # Variable to store the returned data and then comparing user in input with it
                y = result[0].get('tv.title')
                if y == show_title:
                    print("TV show found")

                    # Query for deleting the recommendation relationship before watching the TV show
                    query = """ 
                                                MATCH (tv:SHOW{title:\"""" + y + """\"}) 
                                                MATCH (r:RECOMMENDATIONS{owner: \"""" + login_User_Name + """\"})
                                                MATCH (tv)-[rel:RECOMMENDED_TO]->(r) 
                                                DELETE rel
                                                """
                    graph.run(query)

                    # Query for establishing a relationship between user and TV show
                    query = """
                                                MATCH (u:USER{username: \"""" + login_User_Name + """\"}) 
                                                MATCH (tv:SHOW{title:\"""" + y + """\"}) 
                                                MERGE (u)-[:WATCHED]->(tv)
                                                RETURN tv.universe
                                                """

                    # Universe is returned and stored in a variable to recommend similar shows to the user
                    tv_universe = graph.run(query).data()
                    print("You have watched " + y)
                    print("Universe is " + tv_universe[0].get('tv.universe'))

                    # Query for generating a recommendations node for a user
                    query = """
                            MERGE (r:RECOMMENDATIONS{name: "Recommendations for you", 
                                    owner: \"""" + login_User_Name + """\"})
                            MERGE (u:USER{username: \"""" + login_User_Name + """\"})
                            MERGE (u)-[:HAS]->(r)
                            """
                    graph.run(query)

                    # Query for recommending shows to the user
                    query = """
                            MATCH (tv:SHOW{universe: \"""" + tv_universe[0].get('tv.universe') + """\"})
                            MATCH (r:RECOMMENDATIONS{name: "Recommendations for you", 
                            owner: \"""" + login_User_Name + """\"})--(u:USER{username: \"""" + login_User_Name + """\"})
                            WHERE NOT (u)-[:WATCHED]->(tv)
                            MERGE (tv)-[:RECOMMENDED_TO]->(r)
                            """
                    graph.run(query)
                    print("Similar shows has been recommended to you")
            else:
                print("Show does not exists, please check the spelling and try again or try some other show")

        else:
            print("Invalid input")

    elif watch == "no":
        print("No new shows watched")
    else:
        print("Invalid input")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# ------------------------------------------------------Author Yash---------------------------------------------------------------
def my_liked_shows():
    # Fetch TV show titles of the shows that the the user has liked and insert them in a list shows_liked
    query = """MATCH (u:USER{username: \"""" + login_User_Name + """\"})-[:LIKED]->(tv:SHOW) return tv.title"""
    result = graph.run(query).data()
    shows_liked = []
    for x in result:
        shows_liked.append(x["tv.title"])

    if len(shows_liked) == 0:
        print("You have not liked any TV shows")

    else:
        print("Following are the TV shows you have liked:")

        # Fetch TV show titles from the list shows_liked and provide a numbered list to the user
        for i in shows_liked:
            print(shows_liked.index(i) + 1, end=' ')
            print(i)

        print("Do you want to unlike a TV show from the list above?")
        unlike_option = input("Type yes or no: ")
        if unlike_option == "yes":
            unlike_show = int(input("Please enter the number from the above list of liked shows: "))
            if 0 < unlike_show <= len(shows_liked):
                unlike = str(shows_liked[unlike_show - 1])

                # Check if user has watched the tv show before liking it
                if unlike in shows_liked:
                    print("Selected show is " + unlike)

                    # Query to unlike a tv show
                    query = """
                            MATCH (u:USER{username: \"""" + login_User_Name + """\"})-[r:LIKED]->
                                    (tv:SHOW{title: \"""" + unlike + """\"}) 
                            DELETE r
                            """
                    graph.run(query)

                    print("You have unliked the TV show " + unlike)
                else:
                    print("You have not liked " + unlike + " yet. You have to like a TV show first")
            else:
                print("Invalid input")

        elif unlike_option == "no":
            print("No new TV shows were unliked")
        else:
            print("Invalid input")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# ------------------------------------------------------------Author Yash-------------------------------------------------------
def my_disliked_shows():
    # Fetch TV show titles of the shows that the the user has disliked and insert them in a list shows_disliked
    query = """MATCH (u:USER{username: \"""" + login_User_Name + """\"})-[:DISLIKED]->(tv:SHOW) return tv.title"""
    result = graph.run(query).data()
    shows_disliked = []
    for x in result:
        shows_disliked.append(x["tv.title"])

    if len(shows_disliked) == 0:
        print("You have not disliked any TV shows")

    else:
        print("Following are the TV shows you have disliked:")
        # Fetch TV show titles from the list shows_disliked and provide a numbered list to the user
        for i in shows_disliked:
            print(shows_disliked.index(i) + 1, end=' ')
            print(i)

        print("Do you want to remove a TV show from the above list of disliked shows?")
        undislike_option = input("Type yes or no: ")
        if undislike_option == "yes":
            undislike_show = int(input("Please enter the number from the above list of disliked shows: "))
            if 0 < undislike_show <= len(shows_disliked):
                undislike = str(shows_disliked[undislike_show - 1])

                # Check if user has watched the tv show before disliking it
                if undislike in shows_disliked:
                    print("Selected show is " + undislike)

                    # Query to unlike a tv show
                    query = """
                            MATCH (u:USER{username: \"""" + login_User_Name + """\"})-[r:DISLIKED]->
                                    (tv:SHOW{title: \"""" + undislike + """\"}) 
                            DELETE r
                            """
                    graph.run(query)

                    print("You have removed the TV show " + undislike + " from the list of disliked shows")
                else:
                    print("You have not disliked " + undislike + " yet. You have to dislike a TV show first")
            else:
                print("Invalid input")

        elif undislike_option == "no":
            print("No new TV shows were removed from the list of disliked shows")
        else:
            print("Invalid input")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -----------------------------------------------------Author Yash---------------------------------------------

def my_recommendations():
    # Fetch TV show titles of the shows recommended to the user from Neo4j and insert them in a list recommendations
    query = """MATCH (r:RECOMMENDATIONS{owner: \"""" + login_User_Name + """\"})--(tv:SHOW) return tv.title"""
    result = graph.run(query).data()
    recommendations = []
    for x in result:
        recommendations.append(x["tv.title"])
    if len(recommendations) == 0:
        print("You have no shows in your recommendations")
    else:
        print("Following are the TV shows recommended to you based on the shows you have watched:")

        # Fetch TV show titles from the list shows and provide a numbered list to the user
        for i in recommendations:
            print(recommendations.index(i) + 1, end=' ')
            print(i)

        print("Do you want to watch a TV show from the list of recommended shows?")
        watch_recommended = input("Type yes or no: ")
        if watch_recommended == "yes":
            w = int(input("Enter a show number from the list above to watch: "))
            if 0 < w <= len(recommendations):
                z = str(recommendations[w - 1])
                print("Selected show is " + z)

                # Query for fetching the TV show as per the user input
                query = """
                            MATCH (tv:SHOW{title:\"""" + z + """\"}) RETURN tv.title
                            """
                result = graph.run(query).data()

                # Compare user input and the data fetched from the database
                if z == result[0].get('tv.title'):
                    print("TV show found")

                    # Query for establishing a relationship between user and TV show
                    query = """
                                MATCH (u:USER{username: \"""" + login_User_Name + """\"}) 
                                MATCH (tv:SHOW{title:\"""" + z + """\"}) 
                                MATCH (r:RECOMMENDATIONS{owner: \"""" + login_User_Name + """\"}) 
                                MERGE (u)-[:WATCHED]->(tv) 
                                WITH tv, r, u 
                                MATCH (tv)-[rel:RECOMMENDED_TO]->(r) 
                                DELETE rel
                                """
                    graph.run(query)
                    print("You have watched " + z)
            else:
                print("Invalid input")
        elif watch_recommended == "no":
            print("You didn't watch any of the recommended shows")
        else:
            print("Invalid input")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -----------------------------------------------------------Author Yash-----------------------------------------------

def my_watched_shows():
    print("Following are the TV shows you have watched:")

    # Fetch TV show titles of the shows that the the user has watched and insert them in a list shows_watched
    query = """MATCH (u:USER{username: \"""" + login_User_Name + """\"})-[:WATCHED]->(tv:SHOW) return tv.title"""
    result = graph.run(query).data()
    shows_watched = []
    for x in result:
        shows_watched.append(x["tv.title"])

    # Fetch TV show titles from the list shows_watched and provide a numbered list to the user
    for i in shows_watched:
        print(shows_watched.index(i) + 1, end=' ')
        print(i)

    print("You can like, dislike or remove a TV show that you have watched")
    print("Press enter without any input to exit")
    like_option = input("Type like, dislike or remove: ")
    if like_option == "like":
        like_show = int(input("Please enter the number from the list above: "))
        if 0 < like_show <= len(shows_watched):
            like = str(shows_watched[like_show - 1])

            # Check if user has watched the tv show before liking it
            if like in shows_watched:
                print("Selected show is " + like)

                # Query for liking a tv show
                query = """
                        MATCH (u:USER{username: \"""" + login_User_Name + """\"})
                        MATCH(tv:SHOW{title:\"""" + like + """\"})
                        MERGE (u)-[:LIKED]->(tv)
                        WITH u, tv
                        MATCH (u)-[r:DISLIKED]->(tv) 
                        DELETE r
                        """
                graph.run(query)

                print("You have liked the TV show " + like)
            else:
                print("You have not watched " + like + " yet. Watch a TV show first to like it.")
        else:
            print("Invalid input")

    elif like_option == "dislike":
        dislike_show = int(input("Please enter the number from the list above: "))
        if 0 < dislike_show <= len(shows_watched):
            dislike = str(shows_watched[dislike_show - 1])

            # Check if user has watched the tv show before disliking it
            if dislike in shows_watched:
                print("Selected show is " + dislike)

                # Query for disliking a tv show
                query = """
                        MATCH (u:USER{username: \"""" + login_User_Name + """\"})
                        MATCH(tv:SHOW{title:\"""" + dislike + """\"})
                        MERGE (u)-[:DISLIKED]->(tv)
                        WITH u, tv
                        MATCH (u)-[r:LIKED]->(tv) 
                        DELETE r
                        """
                graph.run(query)

                print("You have disliked the TV show " + dislike)
            else:
                print("You have not watched " + dislike + " yet. Watch a TV show first to dislike it.")
        else:
            print("Invalid input")
    elif like_option == "remove":
        remove_show = int(input("Please enter the number from the list above: "))
        if 0 < remove_show <= len(shows_watched):
            remove = str(shows_watched[remove_show - 1])

            # Check if user has watched the tv show before removing it
            if remove in shows_watched:
                print("Selected show is " + remove)

                # Query for removing a watched tv show and also to remove Liked/ Disliked relation
                query = """
                        MATCH (u:USER{username: \"""" + login_User_Name + """\"})
                        MATCH(tv:SHOW{title:\"""" + remove + """\"})
                        MATCH (u)-[r]->(tv)
                        DELETE r
                        """
                graph.run(query)

                print("You have unwatched the TV show " + remove)
            else:
                print("You have not watched " + remove + " yet.")
        else:
            print("Invalid input")
    else:
        print("Invalid input")
        print("No TV shows were liked or disliked")

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")

    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# ------------------------------------------------------------------Author Manjiri-------------------------------

# Creating a search based on ratings and genre
def searchh():
    global loginname
    print("Enter your genre preference: ")
    choice1 = input("")
    print("Enter the rating : ")
    choice2 = input("")
    # Creating hash with username and timestamp in redis
    loginname = login_User_Name + ':' + str(datetime.now()).replace(' ', ':')
    r.hset(loginname, "Genre", choice1)
    r.hset(loginname, "rating", choice2)

    # Fetching tv shows from Neo4j based upon user's genre and rating preference
    query = """ 
        Match (p:SHOW) WHERE ( p.genre1=\"""" + choice1 + """\" OR p.genre2=\"""" + choice1 + """\" OR p.genre3=\"""" + choice1 + """\"  AND p.IMDBRating >=\"""" + choice2 + """\" )   
        RETURN p.title, p.rating
        """
    # print(query)
    result = graph.run(query).data()
    # Displaying the search result to the user
    print("The Tv shows from the genre", choice1, "and having rating", choice2, "and above are :")
    shows_list = []
    for x in result:
        shows_list.append(x["p.title"])

    for i in shows_list:
        print(shows_list.index(i) + 1, end=' ')
        print(i)

    ans = input("Do you want to Continue: Enter 'Yes' or 'No' ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -------------------------------------------------------------Author Manjiri---------------------------------------
# Fetch Search_history list from Redis
def search_history():
    # getting all the search history keys starting with the username
    pattern = "*" + login_User_Name + "*"
    x = r.keys(pattern=pattern)
    print("My search history: ")

    for var0 in x:
        print(var0)
        # query to get hash along with the fields
        result = r.hgetall(var0)
        print(x.index(var0) + 1, ")", " Genre :", result['Genre'], "Rating :", result['rating'])

    # Option to continue and calling the Main Menu
    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -----------------------------------------------------------------Author Manjiri-----------------------------------------------------
# Delete_history list from Redis
def delete_history():
    pattern = "*" + login_User_Name + "*"

    x = r.keys(pattern=pattern)
    # Displaying the search history list of the user
    for var1 in x:
        print(var1)
        result = r.hgetall(var1)
        print(x.index(var1) + 1, ")", " Genre :", result['Genre'], "and Rating :", result['rating'])

    select = int(input("Enter the number of search record you want to delete: "))
    y = str(x[select - 1])

    # Fetching the selected search history hash from redis
    result1 = r.hgetall(y)

    print("Are you sure you want to delete the search:", " Genre :", result1['Genre'], "and Rating :",
          result1['rating'])
    choice3 = input("Enter 'Yes' to delete OR Enter 'No' to view the search list again : ")

    if choice3 == "Yes" or choice3 == "yes":
        # Query for deleting the search history
        r.delete(y)
        print("Search Record successfully deleted!!!")
    else:
        for var2 in x:
            print(var2)
            result2 = r.hgetall(var2)
            print(x.index(var2) + 1, ")", " Genre :", result2['Genre'], "and Rating :", result2['rating'])

    ans = input("Do you want to continue? Enter 'Yes' or 'No': ")
    if ans == "yes" or ans == "Yes":
        print("")
        menu()
    else:
        print("Closing the application!")
        quit()


# -----------------------------------------------------------------Author Anirudh------------------------------------------------

def adminmenu():
    print(
        " Welcome \n Enter 1 to create user\n Enter 2 to update user \n Enter 3 to delete \n Enter 4 to filter user \n Enter 5 to go back to main menu \n ")
    option = int(input("your option : "))
    if option == 1:
        create_user()
        print('User successfully created')
    elif option == 2:
        update_user()
        print('User successfully updated')
    elif option == 3:
        delete_user()
        print('User successfully deleted')
    elif option == 4:
        filter()
        print('users displayed')
    elif option == 5:
        tvmenu()
    else:
        print("Incorrect option")


# ---------------------------------------Author Ani--------------------------------------------
def tvmenu():
    print("\nMain menu\n 1 to user menu \n 2 to Tv show menu \n 3 to tv show statics\n")
    option = int(input("your option : "))
    if option == 1:
        adminmenu()
    elif option == 2:
        tvshow()
    elif option == 3:
        stats()
    else:
        print('enter valid number')

    # -----------------------------Author Anirudh------------------------------------------------------------


def create_user():
    db = conn.myshows_db
    collection_new_user = db.new_login
    create_username = input('enter the username :')
    create_firstname = input('enter the firstname :')
    create_lastname = input('enter the lastname :')
    create_Email_id = input("Enter the Email Address : ")
    create_password = input('enter the password :')
    create_Phone_Number = input("Enter the Phone Number : ")
    create_Date_of_Birth = input("Enter the Date of Birth : ")
    create_place_of_Birth = input('Enter the Place of Birth :')
    user_type = input("enter user role :")

    mydict = {

        "new_User_Name": create_username,
        "new_First_Name": create_firstname,
        "new_Last_Name": create_lastname,
        "new_Email_id": create_Email_id,
        "new_User_Password": create_password,
        "new_Phone_Number": create_Phone_Number,
        "new_Date_of_Birth": create_Date_of_Birth,
        "new_Place_of_Birth": create_place_of_Birth,
        "user_type": user_type
    }
    collection_new_user.insert_one(mydict)
    print('user added successfully\n')
    adminmenu()

# ----------------------------------------------------Author Anirudh----------------------------------------
def update_user():
    db = conn.myshows_db
    collection_new_user = db.new_login
    print(
        '\n Enter 1 to update firstname\n Enter 2 to update lastname \n Enter 3 to update email id \n Enter 4 to update phone number \n Enter 5 to update email id \n Enter 6 to update user type \n Enter 7 to go back to main menu  ')
    option = int(input('Enter your option :'))
    
    if option == 1:
        criteria = input('\nEnter username to find user :\n')
        upd_firstname = input('Enter new firstname to update :\n')
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"new_First_Name": upd_firstname}})
        print('successfully updated')
        update_user()
    elif option == 2:
        criteria = input('\nEnter username to find user :\n')
        upd_lastname = input('Enter new lastname to update :\n')
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"new_Last_Name": upd_lastname}})
        print('User successfully updated')
        update_user()
    elif option == 3:
        criteria = input('\nEnter username to find user :\n')
        upd_Email_id = input("Enter new Email Address to update :\n ")
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"new_Email_id": upd_Email_id}})
        print('User successfully deleted')
        update_user()
    elif option == 4:
        criteria = input('\nEnter username to find user :\n')
        upd_Phone_Number = input("Enter new Phone Number to update :\n")
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"new_Phone_Number": upd_Phone_Number}})
        print('users displayed')
        update_user()
    elif option == 5:
        criteria = input('\nEnter username to find user :\n')
        upd_Date_of_Birth = input("Enter Date of Birth to update :\n")
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"new_Date_of_Birth": upd_Date_of_Birth}})
        print('Users displayed successfully')
        update_user()
    elif option == 6:
        criteria = input('\nEnter username to find user :\n')
        upd_user_type = input("\nEnter user type to update :\n")
        collection_new_user.update_one({"new_User_Name": criteria}, {"$set": {"user_type": upd_user_type}})
        print('Users displayed successfully')
        update_user()
    elif option == 7:
        tvmenu()
    else:
        print("Incorrect option")
    adminmenu()

# -----------------------------------------------Author Ani------------------------------------------
def delete_user():
    db = conn.myshows_db
    collection_new_user = db.new_login
    name = input('Enter username to delete\n')
    myquery = {"new_User_Name": name}
    collection_new_user.delete_one(myquery)
    print('user deleted successfully')
    adminmenu()


# ---------------------------------------------CODE TO SEARCH USER--------------------------------------------------------

def filter():
    db = conn.myshows_db
    collection_new_user = db.new_login
    d = input('Enter firstname or lastname or email_id or mobile ')
    fname = input('enter to filter')
    myquery = {d: fname}
    x = collection_new_user.find_one(myquery)
    print(x)
    adminmenu()


# -----------------------------------------------------Author Ani-----------------------------------------------------------
def tvshow():
    print(
        " Welcome \n Enter 1 to create tvshow \n Enter 2 to delete tvshow \n Enter 3 to search Tv show \n Enter 4 to go back to main menu")
    option = int(input("your option : "))
    if option == 1:
        create_show()
        print('Tv show successfully created')
    elif option == 2:
        delete_show()
        print('Tv show successfully deleted')
    elif option == 3:
        search()
        print('Tv show displayed')
    elif option == 4:
        tvmenu()
    else:
        print("Incorrect option")


# --------------------------------CODE FOR STATICS OF MOST AND LEAST LIKED SHOWS (STATS METHOD) -------------------------------

def stats():
    print(
        "\nEnter 1 for Tvshow likes \n Enter 2 for Tvshow dislikes \n Enter 3 for Tvshow watched show \n Enter 4 to go back to main menu \n ")
    option = int(input("your option : "))
    if option == 1:
        query = "MATCH (tv:SHOW)<-[r:LIKED]-()  RETURN  tv.title AS showname,  COUNT(r)AS likes order by likes desc"
        result = graph.run(query).data()
        shows = []
        print("TV Show" + "  |  " + "No. of likes")
        for x in result:
            # shows.append(x["showname"])
            # shows.append(x["likes"])
            print("----------------------------------------------------")
            print(x["showname"] + "  |  " + str(x["likes"]))
        for i in shows:
            print(shows.index(i) + 1, end=' ')
            print(i)
        stats()
    elif option == 2:
        query = "MATCH (n:SHOW)<-[r:DISLIKED]-()  RETURN  n.title AS showname,  COUNT(r)AS Dislikes order by Dislikes desc"
        result = graph.run(query).data()
        shows = []
        print("TV Show" + "  |  " + "No. of Dislikes")
        for x in result:
            # shows.append(x["showname"])
            # shows.append(x["likes"])
            print("----------------------------------------------------")
            print(x["showname"] + "  |  " + str(x["Dislikes"]))
        for i in shows:
            print(shows.index(i) + 1, end=' ')
            print(i)
        stats()
    elif option == 3:
        query = "MATCH (n:SHOW)<-[r:WATCHED]-()  RETURN  n.title AS showname,  COUNT(r)AS watched order by watched desc"
        result = graph.run(query).data()
        shows = []
        print("TV Show" + "  |  " + "No. of users watched")
        for x in result:
            # shows.append(x["showname"])
            # shows.append(x["likes"])
            print("----------------------------------------------------")
            print(x["showname"] + "  |  " + str(x["watched"]))
        for i in shows:
            print(shows.index(i) + 1, end=' ')
            print(i)
        stats()
    elif option == 4:
        tvmenu()
    else:
        print('enter valid number')
        stats()


# name = input('enter name')
# MATCH (n)<-[r:LIKED]-() WHERE n.title = name RETURN COUNT(r)

# ------------------------------------------------Author Ani--------------------------------------------
def create_show():
    Title = input('enter show title :')
    IMDBRating = input('enter show rating :')
    Seasons = input('Enter total season :')
    Plot = input('Enter plot :')
    Genre1 = input('Enter genre :')
    Genre2 = input('Enter genre :')
    Genre3 = input('Enter genre :')
    Universe = input('Enter universe :')
    ProductionHouse = input('Enter ProductionHouse :')
    print("\nEnter first director data\n")

    Director1 = input('Enter Director name :')
    Dir1DOB = input('Enter Director DOB :')
    Dir1PlaceOfBirth = input('Enter Director Place of Birth :')
    Dir1NoOfEps = input('Enter Director No of Epsodes :')
    Dir1TimePeriod = input('Enter Director Time Period :')
    Dir1NetWorth = input('Enter Director NetWorth :')

    print("\nEnter second director data\n")

    Director2 = input('Enter Director name :')
    Dir2DOB = input('Enter Director DOB :')
    Dir2PlaceOfBirth = input('enter Director Place of Birth :')
    Dir2NoOfEps = input('Enter Director No of Epsodes :')
    Dir2TimePeriod = input('Enter Director Time Period :')
    Dir2NetWorth = input('Enter Director NetWorth :')

    print('\n Enter first writer data')

    Writer1 = input('Enter Writer name :')
    Writer1DOB = input('Enter WriterDOB :')
    Writer1PlaceOfBirth = input('Enter Writer Place of Birth :')
    Writer1NetWorth = input('Enter Writer Net Worth :')
    Writer1NoOfEps = input('Enter Writer No of Episodes :')
    Writer1TimePeriod = input('Enter Writer TimePeriod :')

    print('\n Enter second writer data')

    Writer2 = input('Enter Writer name :')
    Writer2DOB = input('Enter Writer DOB :')
    Writer2PlaceOfBirth = input('Enter Writer Place of Birth :')
    Writer2NetWorth = input('Enter Writer NetWorth :')
    Writer2NoOfEps = input('Enter Writer No of Episodes :')
    Writer2TimePeriod = input('Enter Writer TimePeriod :')

    print('\n Enter first Artist data')

    Artist1 = input('Enter Artist name :')
    Artist1DOB = input('Enter Artist DOB :')
    Artist1PlaceOfBirth = input('Enter Artist PlaceOfBirth :')
    Artist1NoOfEps = input('Enter Artist NoOfEpisodes :')
    Artist1NetWorth = input('Enter Artist NetWorth :')
    Artist1ScreenName = input('Enter Artist ScreenName :')

    print('\n Enter second Artist data')

    Artist2 = input('Enter Artist name :')
    Artist2DOB = input('Enter Artist DOB :')
    Artist2PlaceOfBirth = input('Enter Artist PlaceOfBirth :')
    Artist2NoOfEps = input('Enter Artist NoOfEpisode :')
    Artist2NetWorth = input(' Enter Artist NetWorth :')
    Artist2ScreenName = input('Enter Artist ScreenName :')

    print('\n Enter third Artist data')

    Artist3 = input('Enter Artist name :')
    Artist3DOB = input('Enter Artist DOB :')
    Artist3PlaceOfBirth = input('Enter Artist PlaceOfBirth :')
    Artist3NoOfEps = input('Enter Artist NoOfEpisode :')
    Artist3NetWorth = input(' Enter Artist NetWorth :')
    Artist3ScreenName = input('Enter Artist ScreenName :')
    print('Tvshow successfully created')

    query = "MERGE (tv:SHOW{title:\"" + Title + "\" , rating:toInteger(\"" + IMDBRating + "\"),seasons:toInteger(\"" + Seasons + "\"),plot:\"" + Plot + "\",genre1:\"" + Genre1 + "\", genre2:\"" + Genre2 + "\", genre3:\"" + Genre3 + "\", universe:\"" + Universe + "\"}) MERGE (w1:WRITER{name:\"" + Writer1 + "\", dateOfBirth:\"" + Writer1DOB + "\", placeOfBirth:\"" + Writer1PlaceOfBirth + "\",netWorth:\"" + Writer1NetWorth + "\"})MERGE (w2:WRITER{name:\"" + Writer2 + "\", dateOfBirth:\"" + Writer2DOB + "\", placeOfBirth:\"" + Writer2PlaceOfBirth + "\", netWorth:\"" + Writer2NetWorth + "\"})MERGE (w1)-[:WROTE{numberOfEpisodes:\"" + Writer1NoOfEps + "\", timePeriod:\"" + Writer1TimePeriod + "\"}]->(tv)MERGE (w2)-[:WROTE{numberOfEpisodes:\"" + Writer2NoOfEps + "\", timePeriod:\"" + Writer2TimePeriod + "\"}]->(tv) MERGE (a1:ARTIST{name:\"" + Artist1 + "\", dateOfBirth:\"" + Artist1DOB + "\", placeOfBirth:\"" + Artist1PlaceOfBirth + "\",netWorth:\"" + Artist1NetWorth + "\"})MERGE (a2:ARTIST{name:\"" + Artist2 + "\", dateOfBirth:\"" + Artist2DOB + "\", placeOfBirth:\"" + Artist2PlaceOfBirth + "\",netWorth:\"" + Artist2NetWorth + "\"})MERGE (a3:ARTIST{name:\"" + Artist3 + "\", dateOfBirth:\"" + Artist3DOB + "\", placeOfBirth:\"" + Artist3PlaceOfBirth + "\",netWorth:\"" + Artist3NetWorth + "\"})MERGE (a1)-[:ACTED_IN{numberOfEpisodes:\"" + Artist1NoOfEps + "\", screenName:\"" + Artist1ScreenName + "\"}]->(tv)MERGE (a2)-[:ACTED_IN{numberOfEpisodes:\"" + Artist2NoOfEps + "\", screenName:\"" + Artist2ScreenName + "\"}]->(tv)MERGE (a3)-[:ACTED_IN{numberOfEpisodes:\"" + Artist3NoOfEps + "\", screenName:\"" + Artist3ScreenName + "\"}]->(tv)MERGE (d1:DIRECTOR{name:\"" + Director1 + "\", dateOfBirth:\"" + Dir1DOB + "\", placeOfBirth:\"" + Dir1PlaceOfBirth + "\", netWorth:\"" + Dir1NetWorth + "\"})MERGE (d2:DIRECTOR{name:\"" + Director2 + "\", dateOfBirth:\"" + Dir2DOB + "\", placeOfBirth:\"" + Dir2PlaceOfBirth + "\", netWorth:\"" + Dir2NetWorth + "\"})MERGE (d1)-[:DIRECTED{numberOfEpisodes:\"" + Dir1NoOfEps + "\", timePeriod:\"" + Dir1TimePeriod + "\"}]->(tv)MERGE (d2)-[:DIRECTED{numberOfEpisodes:\"" + Dir2NoOfEps + "\", timePeriod:\"" + Dir2TimePeriod + "\"}]->(tv) MERGE (p:PRODUCTION_HOUSE{productionHouse:\"" + ProductionHouse + "\"})MERGE (tv)-[:PRODUCED_BY]->(p)"
    graph.run(query)
    tvshow()


# ----------------------------------------- CODE TO DELETE TV SHOW ---------------------------------------------

def delete_show():
    name = input('Enter the tv show title to delete ')
    query = "MATCH (n { title: \"" + name + "\" })DETACH DELETE n"
    graph.run(query)
    print("tv show deleted successfully")
    tvshow()


# ---------------------------------------- CODE TO SEARCH TV SHOW BY TITLE----------------------------------------
#work more
def search():
  query = "MATCH (tv:SHOW) RETURN tv.title"
  result = graph.run(query).data()
  shows = []
  for x in result:
        shows.append(x["tv.title"])
  for i in shows:
                print(shows.index(i) + 1, end=' ')
                print(i)
  tvshow()






if new_user == "Yes":
    new_user_registration()
elif new_user == "No":
    login_opt()

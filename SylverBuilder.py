import re
from SylverUser import SylverUser
import traceback
from datetime import datetime
if __name__ == "__main__":
    print("""
Thank you for participating in the building of the Sylver Coinage 
Endgame Dictionary. This program is built to help identify and 
document new Sylver Coinage positions and requires an Internet 
connection in order to work. The program uses some of your 
machine's CPU power to calculate new positions and update a 
centralized database of positions through an API. For additional
information on Sylver Coinage and this program, please visit:
    <website to be added>
    """)
    
    user_name = ""
    while(len(user_name) < 1):
        user_name = input("User Name: ").lower()
        regex = re.compile("[^a-zA-Z ]")
        user_name = regex.sub("", user_name)
    #print(user_name)
    new_user = SylverUser(user_name)
    try:
        new_user.updateDatabase()
        print(new_user.positions_added_to_database)
    except Exception as e:
        print(traceback.format_exc())
        #print(new_user.position)
    except KeyboardInterrupt:
        print(datetime.now())
        want_to_stop = input("\nAre you sure you would like to stop? [Y]/n: ").lower()
        if (want_to_stop in ["n", "no"]):
            new_user.updateDatabase()
            print(datetime.now())
        else:
            print(new_user.position)
            print(f"""
Thank you so much for all your help! You were able to add {new_user.positions_added_to_database} 
positions to the database!
            """)
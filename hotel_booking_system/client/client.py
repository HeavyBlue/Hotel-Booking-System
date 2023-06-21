import socket
import hashlib
import time
import os
import matplotlib.pyplot as plt
import pickle
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#write ip of server
client.connect((" write your ip", 8000))

permission = {"0": ["create_admin", "change_password", "change_permission", "get_graphic", "change_price"],
              "1": ["get_graphic", "change_price"],
              "2": ["get_graphic"]}


def clear_cmd():
    return os.system('cls' if os.name == 'nt' else 'clear')


def loading_screen(x, what):
    animation = "|/-\\"
    for i in range(x):
        time.sleep(0.1)
        sys.stdout.write("\r" + what + animation[i % len(animation)])
        sys.stdout.flush()


def user_booking():
    clear_cmd()
    client.send("user".encode())
    date = input("Please enter first date [For example (01/01/2023)]\n> ")
    days = input("Please enter last date [For example (01/01/2023)]\n> ")
    dates = date + "-" + days
    client.send(dates.encode())
    available = client.recv(1024).decode()
    if date != days:
        if available == "NotRoom":
            print("Sorry, there are no available rooms.")
            return loading_screen(20, "Returning to the menu ")
        else:
            print("Available room types: ", available)
            room_type = input(f"Please choose the room type\n{available} ").capitalize()
            client.send(room_type.encode())
            breakfast = input("Want you breakfast? [(1) for Yes] [(0) for No]: ")
            client.send(breakfast.encode("utf-8"))
            price = client.recv(1024).decode()
            print(f"Total price is {price} TL")
            name_surname = input("Please enter name and surname: ")
            id_ = input("Please enter your id: ")
            phone_number = input("Please enter your phone number: ")
            while True:
                con_choice_1 = input(f"How do you want to pay?\n[(1) for Online] or [(2) for Hotel] ")
                if con_choice_1 == "1":
                    cc_number = input("Please enter your credit card number: ")
                    cc_vt = input("Please enter your credit card valid thru: ")
                    cc_cvv = input("Please enter your credit card cvv: ")
                    personal_info = "{0}-{1}-{2}-{3}-{4}-{5}\n".format(name_surname, id_, phone_number, cc_number, cc_vt,
                                                                       cc_cvv)
                    client.send(personal_info.encode("utf-8"))
                    break
                elif con_choice_1 == "2":
                    personal_info = "{0}-{1}-{2}-{3}\n".format(name_surname, id_, phone_number, "On Hotel")
                    break
                else:
                    print("Invalid value")
            client.send(personal_info.encode("utf-8"))
            print("Reservation successful!\nThanks for booking!")
            exit()
    else:
        print("Please enter different day")
        time.sleep(1)


class Admin:
    @staticmethod
    def login():
        clear_cmd()
        client.send("admin".encode())
        admin_name = input("Please enter your admin name: ")
        admin_password = hashlib.sha256((input("Please enter your password: ")).encode("utf-8")).hexdigest()
        client.send((admin_name + "-" + admin_password).encode())
        login = client.recv(1024).decode()
        if login == "1":
            return admin_name, True
        else:
            return None, False

    @staticmethod
    def new_password():
        clear_cmd()
        client.send("change_password".encode())
        old_password = hashlib.sha256((input("Please enter current password: ")).encode("utf-8")).hexdigest()
        new_password = input("Please enter new password: ")
        new_password_2 = input("Please enter new Password again: ")
        if new_password == new_password_2:
            new_password_cred = old_password + '-' + hashlib.sha256(new_password.encode("utf-8")).hexdigest()
            client.send(new_password_cred.encode())
            if client.recv(1024).decode() == '1':
                print("Your password has been changed!")
                time.sleep(1)
            else:
                print("Your current password is wrong!")
                time.sleep(1)
        else:
            print("New passwords is not same!")
            time.sleep(1)

    def change_permission(self):
        clear_cmd()
        client.send("change_permission".encode())
        change_user = input("Please enter admin name that do you want to change: ")
        change_level = input("Please enter authority level that do you want to change: ")
        change_ = change_user + "-" + change_level
        client.send(change_.encode())
        msg = client.recv(1024).decode()
        if msg == "No username":
            print("Admin name not found")
            time.sleep(1)
            return self.change_permission()
        else:
            print(msg)
            time.sleep(1)

    @staticmethod
    def create_admin():
        clear_cmd()
        client.send("create_admin".encode())
        new_admin_name = input("Please enter new admin name: ")
        new_admin_password = hashlib.sha256(input("Please enter new admin password: ").encode("utf-8")).hexdigest()
        new_admin_permission = input("Please enter new admin permission\n(0) or (1) or (2): ")
        new_admin_cred = new_admin_name + "-" + new_admin_password + "-" + new_admin_permission
        client.send(new_admin_cred.encode())
        if client.recv(1024).decode() == "1":
            print(f"{new_admin_name} has been added as admin.")
            time.sleep(1)

    @staticmethod
    def change_price():
        clear_cmd()
        client.send("change_price".encode())
        breakfast_or_room = input(
            "What do you want to change?\n[(B) for breakfast price] [(R) for room price]: ").capitalize()
        if breakfast_or_room == "B":
            client.send("breakfast".encode())
            temp_breakfast_price = client.recv(1024).decode()
            breakfast_changed_price = input(f"Breakfast price is {temp_breakfast_price}.\nPlease enter breakfast price "
                                            f"that do you want change\n[If you want to cancel, type (-1)]: ")
            client.send(breakfast_changed_price.encode())
            if breakfast_changed_price == "-1":
                print("Process is canceled!")
                return time.sleep(1)
            else:
                time.sleep(0.15)
                print(client.recv(1024).decode())

        elif breakfast_or_room == "R":
            client.send("room".encode())
            room_changed_type = input("Please enter room type that do you want change\n"
                                      "[Economic] [Suit] [King]: ").capitalize()
            client.send(room_changed_type.encode())
            temp_room_type_price = client.recv(1024).decode()
            room_changed_price = input(f"{room_changed_type} price is {temp_room_type_price}. \nPlease enter room "
                                       f"price that do you want change\n[If you want to cancel, type (-1)]: ")
            client.send(room_changed_price.encode())
            if room_changed_price == "-1":
                print("Process is canceled!")
                return time.sleep(1)
            else:
                print(client.recv(1024).decode())
                time.sleep(1)

    @staticmethod
    def get_graphic():
        clear_cmd()
        client.send("get_graphic".encode())
        choice_1 = input("Income graph [1]\nOccupation ratio graph [2]\n> ")
        client.send(choice_1.encode())
        time.sleep(0.15)
        x, y = pickle.loads(client.recv(4096))
        plt.figure(figsize=(12, 6))
        plt.plot(x, y, "b-.")
        plt.xticks(rotation=45)
        plt.xlabel('Months', )
        if choice_1 == "1":
            plt.ylabel('Total income in TL')
            plt.title('Excepted İncome Graphic In A Year')
        elif choice_1 == "2":
            plt.ylabel('Occupation ratio')
            plt.title('Occupation ratio in a year for months')
        plt.tight_layout()
        plt.show()


while True:
    clear_cmd()
    profile = input("Admin ---> [A]\nBooking -> [B]\nQuit ----> [Q]\n> ").capitalize()
    if profile == "B":
        user_booking()
    elif profile == "A":
        admin = Admin()
        name_admin, admin_result = admin.login()
        if admin_result:
            authority_level = client.recv(1024).decode()
            while True:
                clear_cmd()
                choice = input(
                    f"Welcome {name_admin.capitalize()},"
                    " what would you like to do?\n"
                    "Change password -----------> [1]\n"
                    "Add new admin -------------> [2]\n"
                    "Change price --------------> [3]\n"
                    "Change admins permissions -> [4]\n"
                    "Get graphic ---------------> [5]\n"
                    "Close the session ---------> [6]\n> ")
                if choice == "1":
                    admin.new_password()
                elif choice == "2":
                    if "create_admin" in permission[authority_level]:
                        admin.create_admin()
                    else:
                        print("Invalid authorization level")
                        time.sleep(1)
                elif choice == "3":
                    if "change_price" in permission[authority_level]:
                        admin.change_price()
                    else:
                        print("Invalid authorization level")
                        time.sleep(1)
                elif choice == "4":
                    if "change_permission" in permission[authority_level]:
                        admin.change_permission()
                    else:
                        print("Invalid authorization level")
                        time.sleep(1)
                elif choice == "5":
                    if "get_graphic" in permission[authority_level]:
                        admin.get_graphic()
                    else:
                        print("Invalid authorization level")
                        time.sleep(1)
                elif choice == "6":
                    client.send("quit".encode())
                    loading_screen(15, "Closing the session ")
                    break
                else:
                    print("Invalid value")
                    time.sleep(1)
        else:
            print("Admin name or password is invalid!")
            time.sleep(1)
    elif profile == "Q":
        clear_cmd()
        client.send("quit".encode())
        break
    else:
        print("Invalid value")
        time.sleep(1)

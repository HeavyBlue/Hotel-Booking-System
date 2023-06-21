from datetime import datetime
import pickle
import socket
import time


def listening(port, ip):
    server_connection_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection_.bind((ip, port))
    server_connection_.listen()
    server_, client_address = server_connection_.accept()
    client_ip, client_port = client_address
    print(f"Connection successful {client_ip}")
    return server_, server_connection_

#write your ip
server, server_connection = listening(8000, "write your ip here")


def prices():
    price = open("prices.txt", "r")
    price_list = price.read().split(";")
    room_price, breakfast = eval(price_list[0]), eval(price_list[1])
    price.close()
    return room_price, breakfast


def booking():
    price_ = 0
    date_days = server.recv(1024).decode()
    beginning_day, ending_day = date_days.split("-")
    beginning_day = int(datetime.strptime(beginning_day, '%d/%m/%Y').strftime('%j'))
    ending_day = int(datetime.strptime(ending_day, '%d/%m/%Y').strftime('%j'))
    filled_day_list = [str(day) for day in range(beginning_day, ending_day)]
    with open("book_info.csv", "r+") as book_info:
        book_info_list = book_info.read().split("\n")
        room_types = ""
        for i in book_info_list[1: len(book_info_list) - 1]:
            for k in filled_day_list:
                if k in i.split(";")[2]:
                    break
            else:
                if i.split(";")[1] not in room_types:
                    room_types += i.split(";")[1] + " "
        if room_types == "":
            server.send("NotRoom".encode())
            return
        else:
            time.sleep(0.5)
            server.send(room_types.encode())
            room_type = server.recv(1024).decode("utf-8")
    with open("book_info.csv", "w") as book_info:
        counter = 0
        book_info.write("Room Number;Room Type;Fill Date\n")
        for i in book_info_list[1: len(book_info_list) - 1]:
            temp_dates = ""
            temp_list = i.split(";")
            for k in filled_day_list:
                if k in temp_list[2]:
                    book_info.write(i + "\n")
                    break
                else:
                    temp_dates += str(k) + ","
            else:
                if temp_list[1] == room_type and counter == 0:
                    temp_dates += temp_list[2]
                    temp_list[2] = temp_dates
                    book_info.write(("{0};{1};{2}\n".format(temp_list[0], temp_list[1], temp_list[2])))
                    counter = 1
                else:
                    book_info.write((i + "\n"))
    room_price, breakfast = prices()
    breakfast_choice = server.recv(1024).decode("utf-8")
    if breakfast_choice == "1":
        price_ += room_price[room_type] * len(filled_day_list)
        price_ += breakfast["Breakfast"] * len(filled_day_list)
        breakfast_txt = open("breakfast.txt", "r")
        b_day = eval(breakfast_txt.read())
        breakfast_txt.close()
        for i in filled_day_list:
            b_day[int(i)] += 1
        breakfast_txt = open("breakfast.txt", "w")
        breakfast_txt.write(str(b_day))
        breakfast_txt.close()
    elif breakfast_choice == "0":
        price_ += room_price[room_type] * len(filled_day_list)
    server.send(str(price_).encode())
    personal_info = server.recv(1024).decode("utf-8")
    personal = open("personal_info.txt", "a")
    personal.write(personal_info)
    personal.close()
    exit()


class Admin:
    def __init__(self):
        self.admin_credentials = server.recv(1024).decode().split("-")
        with open("admin.txt", "r") as admin_cred:
            self.admin_creds = admin_cred.read().split("\n")
            self.admin_creds = self.admin_creds[:len(self.admin_creds) - 1]

    def login(self):
        for i in self.admin_creds:
            if self.admin_credentials[0] == i.split("-")[0] and self.admin_credentials[1] == i.split("-")[1]:
                time.sleep(0.15)
                server.send("1".encode())
                time.sleep(0.15)
                server.send(i.split("-")[2].encode())
                return True
        else:
            server.send("0".encode())
            return False

    def change_password(self):
        new_password_credentials = server.recv(1024).decode().split("-")
        counter = 0
        with open("admin.txt", "w") as admin_data:
            for i in self.admin_creds:
                if new_password_credentials[0] == i.split("-")[1]:
                    i = i.split("-")
                    i[1] = new_password_credentials[1]
                    admin_data.write(i[0] + "-" + i[1] + "-" + i[2] + "\n")
                    counter += 1
                    server.send("1".encode())
                else:
                    admin_data.write(i + "\n")
            if counter == 0:
                server.send("0".encode())

    @staticmethod
    def change_permission():
        change_ = server.recv(1024).decode().split("-")
        change_user, change_level = change_[0], change_[1]
        with open("admin.txt", "r") as admin_txt:
            admin_list = admin_txt.read().split("\n")
            for admins_ in admin_list:
                admin_name = admins_.split("-")[0]
                admin_password = admins_.split("-")[1]
                if admin_name == change_user:
                    admin_list.remove(admins_)
                    is_there_user = 1
                    admin_level = change_level
                    temp_admin = admin_name + "-" + admin_password + "-" + admin_level
                    admin_list.append(temp_admin)
                else:
                    is_there_user = 0
        if is_there_user:
            with open("admin.txt", "w") as new_admin_txt:
                for i in admin_list:
                    if i == "":
                        pass
                    else:
                        new_admin_txt.write(i + "\n")
            server.send("Permission changed".encode())
        else:
            server.send("No username".encode())

    @staticmethod
    def create_admin():
        new_admin_creds = server.recv(1024).decode()
        with open("admin.txt", "a") as new_admin:
            new_admin.write(new_admin_creds + "\n")
            server.send("1".encode())

    @staticmethod
    def change_price():
        room_price, breakfast = prices()
        breakfast_or_room = server.recv(1024).decode()

        if breakfast_or_room == "breakfast":
            server.send(str(breakfast["Breakfast"]).encode())
            breakfast_changed_price = server.recv(1024).decode()
            if breakfast_changed_price == "-1":
                return
            else:
                temp_0 = breakfast['Breakfast']
                breakfast["Breakfast"] = int(breakfast_changed_price)
                str_ = f"The change of the breakfast price from {temp_0} to {breakfast_changed_price} is successful."
                server.send(str_.encode())
        elif breakfast_or_room == "room":
            room_changed_type = server.recv(1024).decode()
            temp_1 = room_price[room_changed_type]
            server.send(str(temp_1).encode())
            room_changed_price = server.recv(1024).decode()
            if room_changed_price == "-1":
                return
            else:
                room_price[room_changed_type] = int(room_changed_price)
                str_1 = f"The change of the room price from {temp_1} to {room_changed_price} is successful."
                server.send(str_1.encode())
        to_be_written = f"{room_price};{breakfast}"
        price_file = open("prices.txt", "w")
        price_file.write(to_be_written)
        price_file.close()

    @staticmethod
    def get_graphic():
        month_names = {"Jan": 0, "Feb": 0, "Mar": 0, "Apr": 0, "May": 0, "Jul": 0, "Jun": 0, "Aug": 0,
                       "Sep": 0, "Oct": 0, "Nov": 0, "Dec": 0}
        x = list(month_names.keys())
        room_price, breakfast_price = prices()
        bfast = open("breakfast.txt", "r")
        bfast_list = bfast.read()
        bfast_list = eval(bfast_list)
        bfast.close()
        types = ["Economic", "Suit", "King"]
        prices_ = list(map(int, room_price.values()))
        months = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 365]
        choice_1 = server.recv(1024).decode()

        with open("book_info.csv", "r") as data:
            data = data.read().split("\n")
            if choice_1 == "1":
                for i in range(len(months)):
                    price = 0
                    if months[i] == 30:
                        for k in range(len(types)):
                            for m in data:
                                if types[k] in m:
                                    for n in m.split(";")[2].split(","):
                                        if int(n) <= months[i]:
                                            price += prices_[k]

                        for j in list(bfast_list.keys()):
                            if j <= months[i]:
                                price += int(breakfast_price["Breakfast"]) * bfast_list[j]
                        month_names[x[i]] = price + month_names[x[i]]
                    else:
                        for k in range(len(types)):
                            for m in data:
                                if types[k] in m:
                                    for n in m.split(";")[2].split(","):
                                        if months[i] >= int(n) > months[i - 1]:
                                            price += prices_[k]
                        for j in list(bfast_list.keys()):
                            if months[i] >= j > months[i - 1]:
                                price += int(breakfast_price["Breakfast"]) * bfast_list[j]
                        month_names[x[i]] = price + month_names[x[i]]
                y = []
                for i in x:
                    y.append(month_names[i])
                z = x, y
                data = pickle.dumps(z)
                server.send(data)
            elif choice_1 == "2":
                occu_list = []
                for m in range(len(months)):
                    occu_ = 0
                    for i in data[1: len(data) - 1]:
                        days = i.split(";")[2]
                        for day in days.split(","):
                            if months[m] == 30:
                                if int(day) <= 30:
                                    occu_ += 1
                            elif months[m - 1] < int(day) <= months[m]:
                                occu_ += 1
                    else:
                        occu_list.append((occu_ * 100) / 1110)
                else:
                    y = list(month_names.keys())
                    z = y, occu_list
                    data_ = pickle.dumps(z)
                    server.send(data_)


while True:
    receive = server.recv(1024).decode()
    print(receive.capitalize())
    if receive == "user":
        booking()
    elif receive == "admin":
        admin = Admin()
        is_login = admin.login()
        if is_login:
            while True:
                choice = server.recv(1024).decode()
                if choice == "change_password":
                    admin.change_password()
                elif choice == "change_permission":
                    admin.change_permission()
                elif choice == "create_admin":
                    admin.create_admin()
                elif choice == "change_price":
                    admin.change_price()
                elif choice == "get_graphic":
                    admin.get_graphic()
                elif choice == "quit":
                    break
    elif receive == "quit":
        server_connection.close()
        exit()

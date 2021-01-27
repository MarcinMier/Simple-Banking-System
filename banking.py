import random
import sqlite3

conn = sqlite3.connect('card.s3db')
c = conn.cursor()

c.execute("""DROP TABLE IF EXISTS card""")
c.execute("""
        CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
        )""")


def luhn(base):  # implementing Luhn Algorithm
    new_list = []
    counter = True
    check1 = 0

    for i in base:
        if counter:
            check1 = int(i) * 2
            if check1 > 9:
                check1 -= 9
                new_list.append(check1)
            else:
                new_list.append(check1)
            counter = False
        else:
            new_list.append(int(i))
            counter = True

    check2 = sum(new_list)

    if check2 % 10 == 0:
        luhn_number = 0
    else:
        luhn_number = 10 - (check2 % 10)

    base.append(luhn_number)

    return base


def rand_pin():
    list_pin = ''
    for i in range(4):
        list_pin = list_pin + str((random.randint(0, 9)))
    return list_pin


def rand_acc():  # Creating new account checked by Luhn algorithm
    list_acc = [4, 0, 0, 0, 0, 0]
    for i in range(9):
        list_acc.append(random.randint(0, 9))
    list_acc = luhn(list_acc)  # adding control number
    string = ''  # variable to return the number of account in a string format
    for number in list_acc:
        string = string + str(number)
    return string


def write_in(obj):  # Adding a new card
    c.execute("INSERT INTO card VALUES (?,?,?,?)", (obj.card_id, obj.number, obj.pin, obj.balance))
    conn.commit()


def selection(c_num, p_num):  # Selecting a card and checking pin
    c.execute("""SELECT * FROM card WHERE number = ?""", (c_num,))
    d = c.fetchall()
    if not d:  # Checking if the account exist
        return False
    else:
        return d[0][2] == p_num


def add_income(acc_number):
    print("Enter income:")
    income = input('>')
    c.execute("""UPDATE card SET balance = balance + ? WHERE id = ?""", (income, acc_number))
    conn.commit()
    return print("Income was added!")


def str_to_int_list(word):
    int_list = []
    for w in word:
        int_list.append(int(w))
    return int_list


def tran(acc_number):
    print("Transfer")
    print("Enter card number:")
    rec = input('>')

    if luhn(str_to_int_list(rec[:-1])) != str_to_int_list(rec):
        print('Probably you made a mistake in the card number. Please try again!')
        return 0

    c.execute("""SELECT number FROM card WHERE number = ?""", (rec,))
    receiver_row = c.fetchall()

    if receiver_row == []:
        print('Such a card does not exist.')
        return 0

    if acc_number == rec:
        print("You can't transfer money to the same account!")
        return 0

    print("Enter how much money you want to transfer:")
    transfer = int(input('>'))
    c.execute("""SELECT * FROM card WHERE number = ?""", (acc_number,))
    acc_row = c.fetchall()

    if transfer > acc_row[0][3]:
        print('Not enough money!')
        return 0

    c.execute("""UPDATE card SET balance = balance - ? WHERE id = ?""", (transfer, acc_number))
    c.execute("""UPDATE card SET balance = balance + ? WHERE id = ?""", (transfer, rec))
    conn.commit()
    return print("Income was added!")


def delete(acc_number):
    c.execute("""DELETE FROM card WHERE number = ?""", (acc_number,))
    conn.commit()
    return print('The account has been closed!')


class Account:
    def __init__(self, card_id, number):
        self.card_id = card_id
        self.number = number
        self.pin = rand_pin()
        self.balance = 0


choose = True

while choose:
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    choose1 = input(">")
    print('\n')

    if choose1 == '1':
        temp = rand_acc()
        temp = Account(int(temp), temp)

        print('Your card has been created')
        print('Your card number:')
        print(temp.number)
        print('Your card PIN:')
        print(temp.pin)
        print('\n')

        write_in(temp)

    elif choose1 == '2':
        print('Enter your card number:')
        c_number = input('>')
        print('Enter your PIN:')
        p_number = input('>')
        print('\n')

        if selection(c_number, p_number):

            print('You have successfully logged in!\n')

            while True:
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfer')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                choose2 = input('>')
                print('\n')

                if choose2 == '1':  # Balance
                    c.execute("""SELECT * FROM card WHERE number = ? AND pin = ?""", (c_number, p_number))
                    to_print = c.fetchone()[3]
                    print(f'Balance: {to_print}\n')

                elif choose2 == '2':  # Add income
                    add_income(c_number)

                elif choose2 == '3':  # Do transfer
                    tran(c_number)

                elif choose2 == '4':  # Close account
                    delete(c_number)

                elif choose2 == '5':  # Log out
                    print('You have successfully logged out!\n')
                    break

                elif choose2 == '0':  # Exit
                    choose = False
                    break
        else:
            print('Wrong card number or PIN!\n')

    elif choose1 == '0':
        break
    else:
        pass
conn.commit()
conn.close()

print('Bye!')

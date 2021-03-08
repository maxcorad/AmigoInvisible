#!/usr/bin/env python3
# This script determines for every friend in a group whose 'amigo invisble' are they going to be.
# It will send an SMS to each person with the name of the friend to whom they have to give a present.

# This version of the program creates a class of objects to store the names, phone numbers and
# set of incompatibilities for each ot the friends in a group.

# The information concerning the group of friends is provided from file or input.

# For sending SMS, an AWS account is required (it may incurr in some costs).

usage = """
Given a set of people and incompatibilities, sends an SMS to each person with the name of another person from the group for whom they will have to buy a present.

usage: python AmigoInvisible.py [option] [file]

options and arguments:
-h     : print this help message and exit (also --help)

file   : filename (path relative to execution directory) containing data to be processed;
         data must be stored in the following format: Name;PhoneNumber[;Incompatibility1,Incompatibility2,...]
"""

import random
from boto3 import client        # used to connect to AWS SNS service to send SMS
from sys import argv

class Amigo:
    def __init__(self, name, tel, incomp):
        # Create objects with name, telephone and a set of incompatibilities as properties
        self.name = name
        self.telephone = tel
        self.incompatibilities = incomp

    def from_input(n = None):
        # Creates an Amigo object from input properties
        if n != None: print(f"\nAmigo número {n}:")
        name = input("Nombre: ")
        tel = input("Número de telefono: ")
        incomp = set(input("Enumera los nombres de los amigos a los que este no puede regalar, separados por comas:\n").split(","))
        return Amigo(name, tel, incomp)

    def from_string(line):
        # Creates an Amigo object from string of properties separated by semicolons
        properties = line.split(';')
        name = properties[0]
        tel = properties[1]
        incomp = set(properties[2].split(","))
        return Amigo(name, tel, incomp)

    def invisible(id, friend_list):
        # Select a random Amigo object from a list of available options
        while True:
            amigo_invisible = random.choice(friend_list)
            nombre = amigo_invisible.name
            # Check if choice violates incompatibilities
            if (nombre == id.name) or (nombre in id.incompatibilities): pass
            else:
                # return choice and add it to set of incompatibilities for the rest
                for friend in friend_list: friend.incompatibilities.add(nombre)
                return amigo_invisible


def get_friend_list():
    # Returns a list of friends from information stored in a file or from input
    def list_from_input():
        # Creates a list of Amigo objects of input size
        num_friends = int(input("Introduce el número de amigos:\n"))
        friend_list = [Amigo.from_input(n) for n in range(1, num_friends+1)]
        return friend_list

    def list_from_file(file):
        # Creates a list of Amigo objects from text file
        f = open(file)
        friend_list = [Amigo.from_string(line) for line in f.readlines()]
        f.close()
        return friend_list

    try:
        return list_from_file(argv[1])
    except:
        print("""
        Introduce el nombre del archivo que contiene los datos de los amigos.
        Los datos deben tener el sigiente formato en cada línea:
        Nombre;Telefono[;Incompatibilidad1,Incompatibilidad2,...]

        Alternativamente, presiona <ENTER> para introducir los datos manualmente.
        """)
        file = input()
        return list_from_input() if file == "" else list_from_file(file)

def sorteo():
    # Get list of friends
    friends = get_friend_list()

    # Generate an 'amigo invisible' for each friend in the list
    amigo_invisible_dict = {f:Amigo.invisible(f, friends) for f in friends}

    # Send an SMS to each friend with the corresponding 'amigo invisible'
    for a in amigo_invisible_dict:
        sns_client.publish(
            PhoneNumber=f"+34{a.telephone}",
            Message=f"{a.name}, tienes que regalarle algo a {amigo_invisible_dict.get(a).name}",
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'AmgoInvsble'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )

def main():
    sns_client = client("sns")
    sorteo()


if __name__ == '__main__':
    try:
        if argv[1] == ("-h" or "--help"): print(usage)
    except:
        main()

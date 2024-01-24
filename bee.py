import ijson
import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
import logging
import argparse
import readline
from termcolor import colored  # Import colored for colorization

class Bee:
    def __init__(self):
        self.data = {}
        self.keys = {}
        logging.basicConfig(level=logging.INFO)

    def run(self):
        while True:
            command = input('LOL Bee >> ')
            readline.add_history(command)  # Add the command to the history
            if command == 'exit':
                break
            elif command.startswith('load '):
                filenames = command.split(' ')[1:]
                for filename in filenames:
                    self.load_file(filename)
            elif command.startswith('download '):
                query = command.split(' ', 1)[1]
                self.download_data(query)
            elif command == 'print all':
                self.print_all()
            elif command.startswith('print '):
                parts = command.split(' ')
                key = parts[1]
                if len(parts) > 3 and parts[2] == '-o':
                    outputfile = parts[3]
                    self.print_key_to_file(key, outputfile)
                else:
                    self.print_key(key)
            elif command == 'print_keys':
                self.print_keys()
            elif command == 'help':
                self.print_help()
            else:
                print(f'Unknown command: {command}')

    def load_file(self, filename):
        try:
            if filename.endswith('.json'):
                with open(filename, 'r') as f:
                    objects = ijson.items(f, '')
                    data_list = list(objects)
                    if data_list:
                        self.data[filename] = data_list[0]
                        self.keys[filename] = list(self.data[filename].keys())
                        logging.info(f'Successfully loaded file: {filename}')
                    else:
                        logging.error(f'Empty data in file: {filename}')
            elif filename.endswith('.csv'):
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    data_list = list(reader)
                    if data_list:
                        self.data[filename] = data_list
                        self.keys[filename] = list(data_list[0].keys())
                        logging.info(f'Successfully loaded file: {filename}')
                    else:
                        logging.error(f'Empty data in file: {filename}')
            elif filename.endswith('.xml'):
                tree = ET.parse(filename)
                root = tree.getroot()
                self.data[filename] = self.etree_to_dict(root)
                self.keys[filename] = list(self.data[filename].keys())
                logging.info(f'Successfully loaded file: {filename}')
            else:
                logging.error(f'Unsupported file type: {filename}')
        except Exception as e:
            logging.error(f'Error loading file {filename}: {e}')

    def print_key(self, key, data=None, indent=0):
        if data is None:
            if self.data:
                for filename, file_data in self.data.items():
                    self.print_key(key, file_data, indent)
            elif not self.data:
                logging.info('No data loaded.')
        else:
            if key in data:
                value = data[key]
                if isinstance(value, dict):
                    print(" " * indent + colored(f"{key}:", 'green'))
                    for nested_key, nested_value in value.items():
                        self.print_key(nested_key, {nested_key: nested_value}, indent + 2)
                else:
                    print(" " * indent + colored(f"{key}: {value}", 'green'))
            elif indent == 0:
                logging.info(f'Key not found in data: {key}')

    def print_all(self):
        if self.data :
            for filename, data in self.data.items():
                print(f'Data from {filename}:')
                self.print_recursive(data, indent=2)
        elif not self.data :
            logging.info('No data loaded.')

    def print_keys(self):
        if self.keys:
            for filename, keys in self.keys.items():
                print(f'Keys from {filename}:')
                self.print_recursive_keys(keys, indent=2)
        elif not self.keys:
            logging.info('No keys loaded.')

    def print_recursive_keys(self, keys, indent=0):
        if isinstance(keys, list):
            for key in keys:
                print(" " * indent + f"{key}:")
        elif isinstance(keys, dict):
            for key, value in keys.items():
                print(" " * indent + f"{key}:")
                if isinstance(value, (dict, list)):
                    self.print_recursive_keys(value, indent + 2)
                elif isinstance(value, str):
                    print(" " * (indent + 2) + f"{value}")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, (dict, list)):
                            self.print_recursive_keys(item, indent + 4)
                        elif isinstance(item, str):
                            print(" " * (indent + 4) + f"{item}")
    def print_recursive(self, data, indent=0):
        for key, value in data.items():
            if isinstance(value, dict):
                print(" " * indent + f"{key}:")
                self.print_recursive(value, indent=indent + 2)
            else:
                print(" " * indent + f"{key}: {value}")


    def print_help(self):
        print("""
        Available commands:
        load <filename>... - Load one or more JSON files.
        download <query> - Download data from Shodan.
        print all - Print all data.
        print <key> - Print the value of a specific key.
        print <key> -o <outputfile> - Print the value of a specific key to an output file.
        print_keys - Print all keys.
        help - Print this help message.
        exit - Exit the program.
        """)

def main():
    bee = Bee()
    bee.run()

if __name__ == "__main__":
    main()

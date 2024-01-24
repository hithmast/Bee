import ijson
import argparse
import logging
import shodan

class Bee:
    def __init__(self, api_key=None, verbosity=0):
        self.data = {}
        self.keys = {}
        self.verbosity = verbosity
        self.api = shodan.Shodan(api_key) if api_key else None
        logging.basicConfig(level=logging.INFO)

    def run(self):
        while True:
            command = input('LOL Bee >> ')
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
            elif command == 'print keys':
                self.print_keys()
            elif command == 'help':
                self.print_help()
            else:
                print(f'Unknown command: {command}')

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                objects = ijson.items(f, '')
                data_list = list(objects)
                if data_list:
                    self.data[filename] = data_list[0]
                    self.keys[filename] = list(self.data[filename].keys())
                    if self.verbosity > 0:
                        logging.info(f'Successfully loaded file: {filename}')
                else:
                    logging.error(f'Empty data in file: {filename}')
        except ijson.JSONError as e:
            logging.error(f'Invalid JSON file: {e}')
        except FileNotFoundError:
            logging.error(f'File not found: {filename}')
        except PermissionError:
            logging.error(f'Permission denied: {filename}')

    def download_data(self, query):
        if self.api is not None:
            try:
                results = self.api.search(query)
                self.data[query] = results
                self.keys[query] = list(results.keys())
                if self.verbosity > 0:
                    logging.info(f'Successfully downloaded data for query: {query}')
            except shodan.APIError as e:
                logging.error(f'Shodan API error: {e}')
        else:
            logging.error('No Shodan API key set.')

    def print_all(self):
        if self.data and self.verbosity > 1:
            for filename, data in self.data.items():
                print(f'Data from {filename}:')
                self.print_recursive(data, indent=2)
        elif not self.data and self.verbosity > 0:
            logging.info('No data loaded.')
        
    def print_recursive(self, data, indent=0):
        for key, value in data.items():
            if isinstance(value, dict):
                print(" " * indent + f"{key}:")
                self.print_recursive(value, indent + 2)
            else:
                print(" " * indent + f"{key}: {value}")

    def print_key(self, key):
        if self.data:
            for filename, data in self.data.items():
                if key in data and self.verbosity > 1:
                    print(f'{key} from {filename}: {data[key]}')
                elif key not in data and self.verbosity > 0:
                    logging.info(f'Key not found in {filename}: {key}')
        elif self.verbosity > 0:
            logging.info('No data loaded.')

    def print_key_to_file(self, key, outputfile):
        if self.data:
            for filename, data in self.data.items():
                if key in data:
                    try:
                        with open(outputfile, 'a') as f:
                            f.write(f'{key} from {filename}: {data[key]}\n')
                        if self.verbosity > 0:
                            logging.info(f'Successfully wrote values of {key} from {filename} to {outputfile}')
                    except PermissionError:
                        logging.error(f'Permission denied: {outputfile}')
                elif self.verbosity > 0:
                    logging.info(f'Key not found in {filename}: {key}')
        elif self.verbosity > 0:
            logging.info('No data loaded.')

    def print_keys(self):
        if self.keys and self.verbosity > 1:
            for filename, keys in self.keys.items():
                print(f'Keys from {filename}:', ', '.join(keys))
        elif not self.keys and self.verbosity > 0:
            logging.info('No keys loaded.')

    def print_help(self):
        print("""
        Available commands:
        load <filename>... - Load one or more JSON files.
        download <query> - Download data from Shodan.
        print all - Print all data.
        print <key> - Print the value of a specific key.
        print <key> -o <outputfile> - Print the value of a specific key to an output file.
        print keys - Print all keys.
        help - Print this help message.
        exit - Exit the program.
        """)

def main():
    parser = argparse.ArgumentParser(description='Bee - A JSON file reader.')
    parser.add_argument('-k', '--api-key', type=str, help='set the Shodan API key')
    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2], default=0,
                        help='increase output verbosity')
    args = parser.parse_args()

    bee = Bee(api_key=args.api_key, verbosity=args.verbosity)
    bee.run()

if __name__ == "__main__":
    main()

# Imports
import argparse
import csv
from datetime import date, timedelta, datetime
import pathlib
from numpy import true_divide
from texttable import Texttable
import matplotlib as mpl
from matplotlib import pyplot as plt
import hashlib
import pickle
import copy


# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.

# the Inventory class will be used to keep track of the inventory
class Inventory():
    def __init__(self):
        self.products = []

    def get_rows_for_inventory(self, input_date):
        """
        this method returns: 
            headers
            all products that were on inventory on the input date
        """       
        rows_to_display = []
        if type(input_date) == str:
            input_date = string_to_date(input_date)
        headers = ["product name", "count", "buying price", "expiration date"]
        for item in self.products:
            if string_to_date(item["entry date"]) <= input_date and int(item["count"]) > 0 and string_to_date(item["expiration date"]) >= input_date:
                rows_to_display.append([item["product name"], item["count"], item["buying price"], item["expiration date"]] )
        return headers, rows_to_display

class ArchiveInventory2():
    """
    This class will be added the active invenntory object with the working date as the key
    every time when time is advanced forward, one key-value pair for each day
    """
    def __init__(self):
        self.archives = {}

    def write_to_file(self):
        current_dir = pathlib.Path.cwd()
        file_path = pathlib.Path(current_dir, "archive_inventory.pkl")
        with open(file_path, 'wb') as inventory_file:            
            pickle.dump(self, inventory_file, pickle.HIGHEST_PROTOCOL)

    def add_inventory_for_day(self, day, inventory):
        self.archives[day] = inventory

    def extend_archives_until_date(self, day):
        """
        this method extends the archives until a given date
        """
        dates = self.archives.keys()
        last_day = dates.max()
        while last_day < day:
            last_inventory = copy.deepcopy(self.archives[last_day])
            last_day = last_day + timedelta(days=1)
            self.add_inventory_for_day(last_day, last_inventory)

    def get_inventory_for_day(self, day):
        return self.archives[day]

    def is_product_available_on_last_day(self, product_id, working_day):
        current_inventory = self.archives[working_day]
        last_day = max(self.archives.keys())

        for item in current_inventory.products:
            if item["product id"] == product_id:
                if item["expiration date"] < last_day:
                    last_day = item["expiration date"]
        last_day_inventory = self.archives[last_day]

        for item in last_day_inventory.products:
            if item["product id"] == product_id and item["count"] > 0:
                return True

        return False


class ActiveInventory(Inventory):
    def __init__(self):
        self.products = []
        self.product_id = 0

    def add_product(self, product_name, count, buying_price, selling_price, expiration_date, entry_date, is_init=False):
        """
        this method adds a new product to the inventory
        it also generates a product ID for the product
        """
        self.products.append({
            "product id": self.product_id,
            "product name": product_name,
            "count": count,
            "buying price": buying_price,
            "selling price": selling_price,
            "expiration date": string_to_date(expiration_date),
            "entry date": entry_date
        })
        self.product_id += 1
        # returnig the product ID of the product that was added
        return self.product_id - 1
        
    def sell_product(self, product_id, working_day):
        for item in self.products:
            if item["product id"] == product_id and item["expiration date"] >= working_day and item["count"] > 0:
                item["count"] -= 1


    def print_inventory(self, input_date):
        """
        This method prints the inventory that was available on a given date.
        """

        def create_rows_to_print(input_date):
            """
            this method returns the headers and the table contents for the inventory output
            """            
            rows_to_display = []
            if type(input_date) == str:
                input_date = string_to_date(input_date)
            headers = ["product name", "count", "buying price", "expiration date"]
            for item in self.products:
                if item["expiration date"] >= input_date:
                    rows_to_display.append([item["product name"], item["count"], item["buying price"], item["expiration date"]] )
            return headers, rows_to_display

        def draw_table(headers, rows_to_print):
            """
            this method draws the inventory table on the standard output
            """
            table = Texttable()
            table.header(headers)
            for row in rows_to_print:
                table.add_row(row)

            print(table.draw())

        headers, rows_to_display = create_rows_to_print(input_date)
        draw_table(headers, rows_to_display)

# the ChangeLog class will be used to keep track of finances and days advanced
class ChangeLog():
    def __init__(self):
        self.list_of_actions = []
        self.days_passed = 0
        self.last_hash = ''

    def log_action(self, product_id, action_type, count, price, date, days_advanced, hash=None, is_init=False):
        """
        this method logs any actions made
        """
        self.list_of_actions.append({
            "product id": product_id,
            "action type": action_type,
            "count": count,
            "price": price,
            "date": date,
            "days advanced": days_advanced,
            "hash": hash
        })

    def write_csv(self):
        """
        this method writes the log entries to a csv file
        """
        current_dir = pathlib.Path.cwd()
        file_path = pathlib.Path(current_dir, "change.log")
        with open(file_path, 'w', newline='') as change_file:
            log_writer = csv.writer(change_file, delimiter=";")
            for item in self.list_of_actions:
                log_writer.writerow([item["product id"], item["action type"], item["count"], item["price"], item["date"], item["days advanced"], item["hash"]])
    
    def advance_days(self, num):
        self.days_passed += num

    def generate_hash(self):
        """
        this method should be run:
            - before any changes are made to files in the beginning of the main function
            - after all files were written at the end of the main function
        reading from files is neccessary because the inventory objects' contents might change depending
        on the days passed
        """
        def read_file(file_path):
            string_to_hash = ''
            with open (file_path, "r", newline='') as f:
                f_reader = csv.reader(f, delimiter=";")
                for line in f_reader:
                    if line[1] == "recording new hash":
                        continue #not including hash entries to calculate hash
                    for item in line:
                        string_to_hash += item
            return string_to_hash

        def read_binary_file(file_path):
            with open (file_path, "rb") as f:
                file_content = f.read()
                string = str(file_content)
                return string
        
        def generate_hash(string_to_hash):
            my_hash = hashlib.sha256()
            my_hash.update(string_to_hash)
            result = my_hash.hexdigest()
            return result
        
        current_dir = pathlib.Path.cwd()
        log_file_path = pathlib.Path(current_dir, "change.log")
        archive_inventory_file_path = pathlib.Path(current_dir, "archive_inventory.pkl")
        log_string = read_file(log_file_path)
        archive_inventory_string = read_binary_file(archive_inventory_file_path)
        string_to_hash = log_string + archive_inventory_string
        bytes_string = string_to_hash.encode('utf-8')
        my_hash = generate_hash(bytes_string)
        return my_hash

def string_to_date(input_date):
    """
    this function converts a string to a datetime.date object
    """
    if type(input_date) == date:
        return input_date
    result = datetime.strptime(input_date, "%Y-%m-%d")
    return result.date()

def string_to_month(string):
    """
    input string of format YYYY-MM 
    returns the a datetime.date object with the first day of the given month
    """
    my_date = date(year=int(string[0:4]), month=int(string[5:7]), day=1)
    return my_date

def init_changelog():
    """
    checks if the change.log exists, creates the file if it does not
    with a log creation date enrty
    returns a Changelog instance
    days passed is corrected every passing day
    """
    def create_logfile(file_path):
        with open(file_path, 'w', newline='') as change_file:
            pass

    def create_changelog_from_log_file(file_path):
        with open(file_path, 'r',  newline='') as change_file:
            start_date = None
            days_passed = 0
            log_reader = csv.reader(change_file, delimiter=";")
            changelog = ChangeLog()
            for line in log_reader:
                product_id = None if line[0]=='' else int(line[0])
                action_type = line[1]
                count = None if line[2] == ''  else int(line[2])
                price = None if line[3]== '' else float(line[3])
                my_date = string_to_date(line[4])
                days_advanced = None if line[5] == '' else int(line[5])
                hash_value = line[6]
                changelog.log_action(product_id, action_type, count, price, my_date, days_advanced, hash_value, True)
                if line[1] == "Create log file":
                    start_date = string_to_date(line[4])
                if line[1] == "advance days":
                    days_passed += int(line[5]) # counting days passed since creation of log
            changelog.last_hash = changelog.list_of_actions[-1]["hash"]
            # getting last hash value from last line in file:
            if changelog.last_hash != '':
                check_hash = changelog.generate_hash()
                if check_hash != changelog.last_hash:
                    print("The file's hashes do not match the recorded one.")
                    print("The files might have been corrupted or tampered with.")
                    print("Exiting program.")
                    exit()
            changelog.days_passed = days_passed
            if date.today() > start_date:
                changelog.days_passed = days_passed - int(str(date.today()-(start_date)).split(" ")[0]) # correcting the number of days passed in regard the current date
            if changelog.days_passed < 0:
                changelog.days_passed = 0 # even if correction would do so, days_passed should not go below zero, hence entries for past dates are not possible
            return changelog

    current_dir = pathlib.Path.cwd()
    file_path = pathlib.Path(current_dir, "change.log")
    if not pathlib.Path.exists(file_path):
        create_logfile(file_path)
        changelog = ChangeLog()
        changelog.log_action(None,"Create log file", None, None, date.today(), 0, None)
        return changelog

    else:
        return create_changelog_from_log_file(file_path)

def init_inventory(working_day):
    """this function checks if the inventory file exists, creates the file if it does not
       returns an Archive and and Active Inventory instances
    """
    
    def create_archive_inventory_file(file_path):
        """
        if no inventory.csv file exists, it creates one 
        and returns an ArchiveInventoy and an ActiveInventory instance
        """
        with open(file_path, 'ab') as inventory_file:
            pass
        archive_inventory = ArchiveInventory2()
        return archive_inventory


    def read_archive_inventory_file(file_path):
        archive_inventory = ArchiveInventory2()
        with open(file_path, 'rb') as inventory_file:
                archive_inventory = pickle.load(inventory_file)
        return archive_inventory


    current_dir = pathlib.Path.cwd()
    archive_inventory_file_path = pathlib.Path(current_dir, "archive_inventory.pkl")
    # if inventory file does't exist, create one

    if not pathlib.Path.exists(archive_inventory_file_path):
        archive_inventory = create_archive_inventory_file(archive_inventory_file_path)
    else:
        archive_inventory = read_archive_inventory_file(archive_inventory_file_path)

    try:
        active_inventory = archive_inventory.archives[working_day]
    except KeyError:
        if len(archive_inventory.archives) == 0:
            archive_inventory.add_inventory_for_day(working_day, ActiveInventory())
            active_inventory = archive_inventory.archives[working_day]
        else:
            active_inventory = copy.deepcopy(archive_inventory.archives[working_day - timedelta(days=1)])
            archive_inventory.add_inventory_for_day(working_day, active_inventory)
    
    return archive_inventory, active_inventory

def create_parser():
    # creating the command line parser
    def msg():
        return""" This program supports the below commands. Please see --help for details on the diffrent options.
        inventory -d [YYYY-MM-dd]
        buy -p -c -P -e
        sell -p -c -P
        advance-time -t
        report-revenue -d [YYYY-MM-dd]
        report-profit -d [YYYY-MM]
        """
    parser = argparse.ArgumentParser(usage=msg())
    # adding different argument options below
    parser.add_argument("command", metavar="command", choices=['inventory', 'buy', 'sell', 'advance-time', 'report-revenue', 'report-profit'], nargs=1)
    parser.add_argument("-d", "--date", metavar='', type=str, default=date.today(), help="Specify the date for the inventory (format: YYYY-MM-dd)")   
    parser.add_argument("-p", "--product-name", metavar='', type=str, help="Use this option to specify the name of the product (string)")
    parser.add_argument("-c", "--count", metavar='', type=int, help="Use this option to specify of the amount bought or sold (integer)")
    parser.add_argument("-P", "--price", metavar='', type=float, help="Use this option to specify the price when buying or selling (float)")
    parser.add_argument("-e", "--expiration-date", metavar='', type=str, help="Use this option to specify the expiration date of products when buying (format: YYYY-MM-dd)")    
    parser.add_argument("-t", "--time", metavar='', type=int, help="""Use this option to specify the number of days you want to advance (integer). This option accepts positive and negative numbers as well, but you can not set the internal date prior to the actual date. This will be revised upon the invention of time travel""")
    args = parser.parse_args()
    return args

def sanitize_command(arguments_dict, last_day, first_day):
    """evaluating the command to see which function to call 
       and to see if all proper arguments have been provided
       returns None if all checks were successful
       returns an error message if a check failed
       """
    def sanitize_inventory(arguments_dict, last_day, first_day):
        if type(arguments_dict["date"]) == date:
            return None
        try:
            day = arguments_dict["date"]
            my_date = string_to_date(day)
        except:
            return "The date (-d) must be provided in the following format:  YYYY-MM-dd"
        if my_date > last_day:
            return "The date (-d) needs to be at maximum the day of the last enrty."
        if my_date < first_day:
            return "The date (-d) needs to be at minimum the date of the first entry."
        return None

    def sanitize_buy(argument_dict):
        if argument_dict["product_name"] != '':
            try:
                int(argument_dict["count"])
            except:
                return "Product count (-c) must be a positive integer"
            if int(argument_dict["count"]) <= 0:
                return "Product count (-c) must be a positive integer"
            try:
                float(argument_dict["price"])
            except:
                return "The prouct price (-P) must be a positive number"
            if float(argument_dict["price"]) <= 0:
                return "The prouct price (-P) must be a positive number"
            try:
                day = argument_dict["expiration_date"]
                my_date = string_to_date(day)
            except:
                return "The expiration date (-e) must be provided in the following format:  YYYY-MM-dd"
            if my_date < date.today():
                return "The expiration date (-e) needs to be a future date."
            return None
        else:
            print("ha")
            return "Product name (-p) must be provided."

    def sanitize_sell(arguments_dict):
        try:
            float(arguments_dict["price"])
        except:
            return "Price (-P) must be a number."
        return None

    def sanitize_advance_time(arguments_dict):
        try:
            int(arguments_dict["time"])
            return None
        except:
            return "Please specify the count (-t) of days passed as an integer."

    def sanitize_report_revenue(arguments_dict):
        if type(arguments_dict["date"]) == date:
            return None
        else:
            try:
                string_to_date(arguments_dict["date"])
                return None
            except:
                return "Please specify a date (-d) in the following format: YYYY-MM-dd"

    def sanitize_report_profit(arguments_dict):
        try:
            if len(arguments_dict["date"]) > 7:
                return "Please provide a month to calculate profits for in the format of YYYY-MM"
            string_to_month(arguments_dict["date"])
            return None
        except:
            return "Please provide a month to calculate profits for in the format of YYYY-MM"
        

    if arguments_dict["command"][0] == "inventory":
        return sanitize_inventory(arguments_dict, last_day, first_day)
    elif arguments_dict["command"][0] == "buy":
        return sanitize_buy(arguments_dict)       
    elif arguments_dict["command"][0] == "sell" :
        return sanitize_sell(arguments_dict)      
    elif arguments_dict["command"][0] == "advance-time":
        return sanitize_advance_time(arguments_dict)      
    elif arguments_dict["command"][0] == "report-revenue":
        return sanitize_report_revenue(arguments_dict)
    elif arguments_dict["command"][0] == "report-profit":
        return sanitize_report_profit(arguments_dict)

def print_inventory(headers, rows_to_print):
    # this function creates an stdout table and prints it
    # from headers and data
    table = Texttable()
    table.header(headers)
    for row in rows_to_print:
        table.add_row(row)

    print(table.draw())

def execute_command(archive_inventory, active_inventory, changelog, arguments_dict, first_date, working_date, final_date):
    """
    once the inputs have been sanitized, execute the appropriate command
    """

    def execute_buy(active_inventory, archive_inventory, changelog, product_name, count, price, expiration_date, working_date):
        """
        this function adds a product to the active inventory
        and creates a corresponding log entry
        """
        
        product_id = active_inventory.add_product(product_name, count, float(price), 0.0, expiration_date, date.today()+timedelta(changelog.days_passed))
        if working_date != final_date:
         for key_date, value_inventory in archive_inventory.archives.items():
            # register the same buy for future days inventories
            if key_date > working_date:
                value_inventory.add_product(product_name, count, price, 0.0, expiration_date, date.today()+timedelta(changelog.days_passed))

        changelog.log_action(product_id, "buy", count, price, date.today()+timedelta(changelog.days_passed), None, None)
        print("[*] buy command executed")

    def execute_inventory(archive_inventory, active_inventory, input_date):
        """
        this function shows the inventory for a given day
        """
        active_inventory = archive_inventory.archives[input_date]
        print("Showing the inventory for ", input_date)
        active_inventory.print_inventory(input_date)

    def execute_sell(archive_inventory, active_inventory, changelog, arguments_dict, working_date):
        """
        this function tries to sells one piece of a product in the active inventory
        returns an error if it was not possible
        """
        # setting up a boolean to see if the sell command can be executed
        product_id = int
        for item in active_inventory.products:
            if item["product name"] == arguments_dict["product_name"]:
                product_id = item["product id"]
                break
        can_sell_product = archive_inventory.is_product_available_on_last_day(product_id, working_date)
        if can_sell_product:
            changelog.log_action(active_inventory.products[-1]["product id"], "sell", 1, arguments_dict["price"], arguments_dict["date"], None, None)
            while True:
                try:
                    active_inventory = archive_inventory.get_inventory_for_day(working_date)
                    active_inventory.sell_product(product_id, working_date)
                    working_date = working_date + timedelta(days=1)                  
                except KeyError:
                    break


            print("[*] sell command executed")
        else:
            print("Product is not on stock to sell.")
    
    def execute_advance_time(changelog, arguments_dict, archive_inventory, active_inventory, working_date, final_date):
        """
        this function modifies the days_advanced parameter of the changelog
        ultimately changing the date of the operations
        """
        number_of_days_to_advance = int(arguments_dict["time"])
        changelog.log_action(None, "advance days", None, None, date.today() + timedelta(days=changelog.days_passed), number_of_days_to_advance, None)
        changelog.advance_days(number_of_days_to_advance)
        if number_of_days_to_advance > 0:
            if working_date == final_date:
                for i in range(number_of_days_to_advance):
                    archive_inventory.add_inventory_for_day(working_date + timedelta(days=i), copy.deepcopy(active_inventory))
            elif working_date + timedelta(days=number_of_days_to_advance) > final_date:
                for i in range(number_of_days_to_advance):
                    if working_date + timedelta(days=i) not in archive_inventory.archives.keys():
                        # copying the last available inventory to future days
                        active_inventory = archive_inventory.get_inventory_for_day(working_date + timedelta(days=i-1))
                        archive_inventory.add_inventory_for_day(working_date + timedelta(days=i), copy.deepcopy(active_inventory))
        print("[*] advance time command executed")

    def execute_report_revenue(changelog, arguments_dict):
        """
        this function reports revenues for a given day
        """
        daily_revenue = 0
        if type(arguments_dict["date"]) == date:
            date_to_check = arguments_dict["date"]
        else:
            date_to_check = string_to_date(arguments_dict["date"])
        for item in changelog.list_of_actions:
            if item["date"] == date_to_check:
                if item["action type"] == "sell":
                    daily_revenue += float(item["price"])
        return date_to_check, daily_revenue
        
    def execute_report_profit(changelog, arguments_dict):
        """
        this function outputs income, expenditure and profit for a given month
        """
        def get_days_of_the_month(arguments_dict):
            """
            generate a list of the days of the month to check
            """
            starting_day_of_month = string_to_month(arguments_dict["date"])
            days_to_check = [starting_day_of_month]
            next_day_to_check = starting_day_of_month + timedelta(days=1)
            while next_day_to_check.month == starting_day_of_month.month:
                days_to_check.append(next_day_to_check)
                next_day_to_check = next_day_to_check + timedelta(days=1)
            return days_to_check

        def get_profits_for_a_month(changelog, days_to_check):
            """
            this function returns income and expendifure for a given month
            and also provides a matplotlib bar chart for a better understanding
            """
            expenditure = 0
            income = 0
            cash_flow_list_positive_y = [0 for day in days_to_check]
            cash_flow_list_negative_y = [0 for day in days_to_check]
            cash_flow_dates_list_x = days_to_check
            for item in changelog.list_of_actions:
                if item["date"] in days_to_check:
                    if item["action type"] == "buy":
                        expenditure += item["price"] * item["count"]
                        idx = cash_flow_dates_list_x.index(item["date"])
                        cash_flow_list_negative_y[idx] += -(item["price"] * item["count"])
                    if item["action type"] == "sell":
                        income += item["price"]
                        idx = cash_flow_dates_list_x.index(item["date"])
                        cash_flow_list_positive_y[idx] += item["price"]

            fig = plt.figure()
            ax = plt.subplot(111)
            x = range(len(cash_flow_dates_list_x))
            ax.bar(x, cash_flow_list_positive_y, align='center', alpha=0.5, color="b")
            ax.bar(x, cash_flow_list_negative_y, align='center', alpha=0.5, color="r")
            ax.set_xlabel("Days of the month")
            ax.set_ylabel("Cash flow")


            plt.show()

            return income, expenditure

        my_month = arguments_dict["date"]
        days = get_days_of_the_month(arguments_dict)
        income, expenditure = get_profits_for_a_month(changelog, days)
        print("The income for", my_month, "was", income)
        print("The expenditure for", my_month, "was", expenditure)
        print("The profits for", my_month, "were", income-expenditure)

    if arguments_dict["command"][0] == "buy":
        execute_buy(active_inventory, archive_inventory, changelog, arguments_dict["product_name"], arguments_dict["count"], arguments_dict["price"], arguments_dict["expiration_date"], working_date)
    elif arguments_dict["command"][0] == "inventory":
        if arguments_dict["date"] == date.today():
            execute_inventory(archive_inventory, active_inventory, string_to_date(arguments_dict["date"]) + timedelta(days=changelog.days_passed))
        else:
            execute_inventory(archive_inventory, active_inventory, string_to_date(arguments_dict["date"]))
    elif arguments_dict["command"][0] == "sell":
        execute_sell(archive_inventory, active_inventory, changelog, arguments_dict, working_date)
    elif arguments_dict["command"][0] == "advance-time":
        execute_advance_time(changelog, arguments_dict, archive_inventory, active_inventory, working_date, final_date)
    elif arguments_dict["command"][0] == "report-revenue":
        date_to_check, daily_revenue = execute_report_revenue(changelog, arguments_dict)
        print("The revenue for", date_to_check, "is", daily_revenue)
    elif arguments_dict["command"][0] == "report-profit":
        execute_report_profit(changelog, arguments_dict)

def get_first_and_last_days(changelog, active_inventory):
    """
    this function gets the first and last days of interaction
    with the application, ideintifying the acceptable date range for commands
    """
    first_day = string_to_date(changelog.list_of_actions[0]["date"])
    try:
        last_day = first_day + timedelta(days=changelog.days_passed)
    except:
        last_day = date.today()
    if date.today() > last_day:
        last_day = date.today()
    return first_day, last_day

def main():
    changelog = init_changelog()
    working_day = date.today() + timedelta(changelog.days_passed)
    archive_inventory, active_inventory = init_inventory(working_day)
    arguments = create_parser()
    arguments_dict = vars(arguments)
    first_day, last_day = get_first_and_last_days(changelog, active_inventory)
    result = sanitize_command(arguments_dict, last_day, first_day)
    if result != None:
        print("sanitize command result:")
        print(result)

    if result == None:
        execute_command(archive_inventory, active_inventory, changelog, arguments_dict, first_day, working_day, last_day)


    
    changelog.write_csv()
    # generate new hash only if there were any updates to the files or there was no existing hash:
    if (arguments_dict["command"][0] in ["buy", "sell", "advance-time"]) or changelog.last_hash == '': 
        archive_inventory.write_to_file()
        new_hash = changelog.generate_hash()
        changelog.log_action(None, "recording new hash", None, None, date.today() + timedelta(days=changelog.days_passed), None, new_hash)
        changelog.write_csv()


    



if __name__ == "__main__":
    main()

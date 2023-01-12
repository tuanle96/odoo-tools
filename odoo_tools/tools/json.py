from prettytable import PrettyTable


def pretty_print_json(
        json_data):
    """ Pretty print json data. :param data: json data :return: pretty print json data """
    table = PrettyTable()
    for key, value in json_data.items():
        table.add_row([key, value])

    print(table)

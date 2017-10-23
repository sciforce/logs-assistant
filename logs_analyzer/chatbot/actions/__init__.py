from logs_analyzer.reader import LogsReader


def get_time_slice(database, time_from, time_to):
    mask = (time_from < database['timestamp']) & (database['timestamp'] < time_to)
    return database[mask]


def get_levels(database, levels):
    if isinstance(levels, str):
        mask = database['level'] == levels
    else:
        mask = database['level'] == levels[0]
        for li in range(1, len(levels)):
            mask |= database['level'] == levels[li]
    return database[mask]


def filter_services(database, services):
    if isinstance(services, str):
        mask = database['service'] == services
    else:
        mask = database['service'] == services[0]
        for li in range(1, len(services)):
            mask |= database['service'] == services[li]
    return database[mask]


def print_all(database):
    for elem in database.iterrows():
        LogsReader.pretty_print(elem[1])

import re
import warnings
from datetime import datetime, date, time
import pandas as pd


class LogsReader:
    def __init__(self, logs_to_read):
        self.pattern = re.compile('\[(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+) '
                                  '(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)\-(?P<millisecond>\d+)\]\s*'
                                  '\((?P<level>[DIWE]\d*)\)\s*:(?P<thread>\d+):\s*(?P<message>.*)')
        self.simple_pattern = re.compile('\[(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+) '
                                         '(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)\-(?P<millisecond>\d+)\]\s*'
                                         '\((?P<level>[DIWE]\d*)\)\s*:?\s*(?P<message>.*)')
        self.logs = None
        for name, path_to_log in logs_to_read.items():
            self.read_log(name, path_to_log)

    def read_log(self, name, path_to_log):
        data = []
        with open(path_to_log, 'r') as f:
            for line in f:
                try:
                    data.append(self._parse_log_line(line))
                except ValueError:
                    warnings.warn('Failed to parse line: "{}"'.format(line))
                    continue
        print('Successfully parsed {} lines from log {}'.format(len(data), name))
        data = pd.DataFrame(data)
        if self.logs is None:
            self.logs = data.assign(service=name)
        else:
            self.logs = pd.concat([self.logs, data.assign(service=name)])

    def _parse_log_line(self, line):
        parsed = self.pattern.match(line)
        if parsed is None:
            parsed = self.simple_pattern.match(line)
        if parsed is None:
            raise ValueError('Parsing line failed!')
        parsed_dict = parsed.groupdict()
        if 'thread' not in parsed_dict:
            parsed_dict['thread'] = -1
        entry_date = date(int(parsed_dict['year']), int(parsed_dict['month']), int(parsed_dict['day']))
        entry_time = time(int(parsed_dict['hour']), int(parsed_dict['minute']), int(parsed_dict['second']),
                          1000 * int(parsed_dict['millisecond']))
        entry_timestamp = datetime.combine(entry_date, entry_time)
        result = {'message': parsed_dict['message'],
                  'level': parsed_dict['level'],
                  'thread': int(parsed_dict['thread']),
                  'timestamp': entry_timestamp}
        return result

    @staticmethod
    def pretty_print(entry):
        print('[{}, service {}, thread {}, level {}]\n{}'.format(entry['timestamp'], entry['service'], entry['thread'],
                                                                 entry['level'], entry['message']))

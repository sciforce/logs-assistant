from datetime import datetime

from logs_analyzer.chatbot.actions import get_levels, print_all, get_time_slice, filter_services


class RegisterAction(object):
    actions = {}

    def __init__(self, method):
        self.method = method
        RegisterAction.actions[method.__name__] = method

    def __call__(self):
        self.method()


class HighLevelActions:
    def __init__(self, bot_state):
        self.state = bot_state

    def call_action(self, name):
        self.state.action_executed = False
        if name in RegisterAction.actions:
            self.state.action_executed = RegisterAction.actions[name](self)

    @RegisterAction
    def last_errors(self):
        self.state.results = get_levels(self.state.get_dataset(), 'E')
        return True

    @RegisterAction
    def time_slice(self):
        if len(self.state.date_params) < 1:
            return False
        start_date = self.state.date_params[0]
        end_date = self.state.date_params[1] if len(self.state.date_params) > 1 else datetime.now()
        self.state.results = get_time_slice(self.state.get_dataset(),
                                            start_date, end_date)
        return True

    @RegisterAction
    def clear(self):
        self.state.reset()
        return True

    @RegisterAction
    def show_all(self):
        if self.state.results_empty():
            return False
        else:
            print_all(self.state.results)
            return True

    @RegisterAction
    def head(self):
        if self.state.results_empty():
            return False
        else:
            print_all(self.state.results.head(self.state.get_lines_num()))
            return True

    @RegisterAction
    def tail(self):
        if self.state.results_empty():
            return False
        else:
            print_all(self.state.results.tail(self.state.get_lines_num()))
            return True

    @RegisterAction
    def greeting(self):
        old_status = self.state.already_greeted
        self.state.already_greeted = True
        return not old_status

    @RegisterAction
    def service_filter(self):
        if not self.state.service_params:
            return False
        self.state.results = filter_services(self.state.get_dataset(), self.state.service_params)
        return True

class BotState:
    def __init__(self, data):
        self.all_data = data
        self.results = None
        self.default_lines_num = None
        self.action_executed = None
        self.integer_params = None
        self.service_params = None
        self.date_params = None
        self.already_greeted = None
        self.reset()

    def reset(self):
        self.default_lines_num = 5
        self.results = []
        self.integer_params = []
        self.date_params = []
        self.already_greeted = False
        self.action_executed = False

    def get_lines_num(self):
        if not self.integer_params:
            return self.default_lines_num
        return self.integer_params[0]

    def get_dataset(self):
        if self.results_empty():
            self.results = self.all_data
        return self.results

    def results_empty(self):
        return self.get_rows_num() == 0

    def get_rows_num(self):
        return len(self.results)

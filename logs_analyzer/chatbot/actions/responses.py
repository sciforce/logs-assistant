class RegisterResponse(object):
    responses = {}

    def __init__(self, method):
        self.method = method
        RegisterResponse.responses[method.__name__] = method

    def __call__(self):
        self.method()


class Responses:
    def __init__(self, bot_state, intents_config):
        self.config = intents_config
        self.state = bot_state

    def show_response(self, name):
        RegisterResponse.responses[name](self)

    @RegisterResponse
    def last_errors(self):
        self._blank_or_ok('last_errors')

    @RegisterResponse
    def greeting(self):
        if self.state.action_executed:
            print(self.config['greeting']['responses']['ok'])
        else:
            print(self.config['greeting']['responses']['duplicate'])

    @RegisterResponse
    def clear(self):
        print(self.config['clear']['responses']['ok'])

    @RegisterResponse
    def show_all(self):
        if not self.state.action_executed:
            print(self.config['show_all']['responses']['blank'])

    @RegisterResponse
    def tail(self):
        if not self.state.action_executed:
            print(self.config['tail']['responses']['blank'])

    @RegisterResponse
    def head(self):
        if not self.state.action_executed:
            print(self.config['head']['responses']['blank'])

    @RegisterResponse
    def time_slice(self):
        self._blank_or_ok('time_slice')

    @RegisterResponse
    def service_filter(self):
        self._blank_or_ok('service_filter')

    @RegisterResponse
    def unknown(self):
        print("I don't understand, sorry.")

    def _blank_or_ok(self, intent):
        if not self.state.results_empty():
            print(self.config[intent]['responses']['ok'].format(self.state.get_rows_num()))
        else:
            print(self.config[intent]['responses']['blank'])


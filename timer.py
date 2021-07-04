class Timer():
    __timer = None

    def __init__(self, current_time):
        if Timer.__timer is None:
            Timer.__timer = self
        else:
            raise Exception('Call get_instance()')
        self.current_time = current_time

    @staticmethod
    def get_instance():
        return Timer.__timer
    
    def set_time(self, time):
        self.current_time = time
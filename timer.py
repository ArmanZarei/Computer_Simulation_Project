class Timer:
    __timer = None

    def __init__(self, current_time):
        if Timer.__timer is not None:
            raise Exception("Call get_instance()")
        self.current_time = current_time

    @staticmethod
    def get_instance(reset: bool = False):
        if not Timer.__timer:
            Timer.__timer = Timer(0)
        if reset:
            Timer.__timer.current_time = 0
        return Timer.__timer

    def set_time(self, time):
        self.current_time = time

class Error:
    def __init__(self, id, error):
        self.id = id
        self.error = error
    
    def to_dict(self):
        return self.__dict__
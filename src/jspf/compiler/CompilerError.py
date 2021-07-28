class CompilerError(Exception):
    def __init__(self, err_msg):
        super().__init__(err_msg)


from inspect import signature


class Elem:
    def __init__(self, a: int, b: str, c: dict):
        pass
    

print(signature(Elem).parameters['a'].annotation)
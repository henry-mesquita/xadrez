from .generator import Generator


class Judge:
    def __init__(self, generator: Generator) -> None:
        self.generator: Generator = generator



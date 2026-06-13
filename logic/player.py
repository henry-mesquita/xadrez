from abc import ABC, abstractmethod
import random
from pecas.peca import Cor
from logic.move import Movimento
from logic.state import GameState

class Jogador(ABC):
    def __init__(self, cor: Cor):
        self.cor = cor

    @abstractmethod
    def decidir_lance(self, lances_validos: list[Movimento]) -> Movimento | None:
        pass


class JogadorHumano(Jogador):
    def __init__(self, cor: Cor):
        super().__init__(cor)
        self.lance_reservado: Movimento | None = None

    def decidir_lance(self, lances_validos: list[Movimento]) -> Movimento | None:
        if self.lance_reservado:
            lance = self.lance_reservado
            self.lance_reservado = None
            return lance
        return None


class IAAleatoria(Jogador):
    def decidir_lance(self, lances_validos: list[Movimento]) -> Movimento | None:
        if not lances_validos:
            return None
        return random.choice(lances_validos)

from pecas.peca import Cor, Peca
from pecas.peao import Peao
from pecas.torre import Torre
from pecas.cavalo import Cavalo
from pecas.bispo import Bispo
from pecas.dama import Dama
from pecas.rei import Rei


MAPA_PECAS = {
    'p': Peao,
    'r': Torre,
    'n': Cavalo,
    'b': Bispo,
    'q': Dama,
    'k': Rei
}


def criar_peca(tipo: str, cor: Cor, pos: tuple) -> Peca:
    """
    Cria uma instância de peça baseada no tipo (char), cor e posição.
    Qualquer parte do sistema pode chamar essa função.
    """
    classe = MAPA_PECAS[tipo.lower()]
    return classe(cor=cor, posicao=pos)

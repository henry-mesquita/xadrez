from dataclasses import dataclass

# localização interna da peça (mutável, lista)
type Coord = list[int]


@dataclass(frozen=True)
class Cor:
    BRANCO = 'w'
    PRETO = 'b'


class Peca:
    """
    Classe base abstrata para todas as peças de xadrez.

    Define a interface comum e comportamento genérico compartilhado por todas
    as peças (rei, rainha, torre, bispo, cavalo, peão).
    """
    def __init__(
        self,
        cor: Cor,
        posicao: Coord
    ) -> None:
        """
        Inicializa uma peça.

        Args:
            cor (Cor): Cor da peça (Cor.BRANCO para branco ou Cor.PRETO para preto).
            posicao (Coord): Posição da peça.
        """
        if cor.lower() not in (Cor.BRANCO, Cor.PRETO):
            raise ValueError("Cor tem que estar em: (Cor.BRANCO, Cor.PRETO)")

        self.cor: Cor = cor.lower()
        # Posição visual da peça (sincronizado com a posição lógica)
        self.posicao: Coord = posicao


    def __str__(self) -> str:
        """
        Retorna uma representação de string da peça.
        """
        tipo = self.__class__.__name__
        cor = self.cor
        pos = self.posicao
        return f"Tipo: {tipo} | Cor: {cor} | Posição: {pos})"
    

    def __repr__(self) -> str:
        """
        Retorna uma representação de depuração da peça.
        """
        tipo = self.__class__.__name__
        cor = self.cor
        pos = self.posicao
        return f"Tipo: {tipo} | Cor: {cor} | Posição: {pos})"

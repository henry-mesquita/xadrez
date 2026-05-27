from constantes import *
import numpy as np
from pecas.peca import Peca, Cor
from pecas.bispo import Bispo
from pecas.cavalo import Cavalo
from pecas.dama import Dama
from pecas.peao import Peao
from pecas.rei import Rei
from pecas.torre import Torre
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Movimento:
    """
    Representa um movimento de peça.
    
    Attributes:
        origem (tuple[int, int]): Casa inicial.
        destino (tuple[int, int]): Casa final.

        Formato: (linha, coluna), (x, y)
    """
    origem:     tuple[int, int]
    destino:    tuple[int, int]


class TipoMov(Enum):
    NORMAL          = auto()
    CAPTURA         = auto()
    ROQUE_CURTO     = auto()
    ROQUE_LONGO     = auto()
    EN_PASSANT      = auto()


class Engine:
    """
    Gerenciador de lógica e estado do jogo de xadrez.

    Controla o tabuleiro, valida movimentos, gera movimentos possíveis, gerencia
    turnos e verifica condições de xeque. Totalmente desacoplada da camada visual.
    """
    MAPA_PECAS: dict[str, type[Peca]] = {
        'p': Peao,
        'r': Torre,
        'n': Cavalo,
        'b': Bispo,
        'q': Dama,
        'k': Rei
    }

    ROQUES = {
        (Cor.BRANCO, "curto"): {
            "direito": "roque_curto_branco",
            "origem_rei": (7, 4),
            "destino_rei": (7, 6),
            "origem_torre": (7, 7),
            "destino_torre": (7, 5),
            "casas_seguras": [(7, 5), (7, 6)]
        },

        (Cor.BRANCO, "longo"): {
            "direito": "roque_longo_branco",
            "origem_rei": (7, 4),
            "destino_rei": (7, 2),
            "origem_torre": (7, 0),
            "destino_torre": (7, 3),
            "casas_seguras": [(7, 3), (7, 2)]
        },

        (Cor.PRETO, "curto"): {
            "direito": "roque_curto_preto",
            "origem_rei": (0, 4),
            "destino_rei": (0, 6),
            "origem_torre": (0, 7),
            "destino_torre": (0, 5),
            "casas_seguras": [(0, 5), (0, 6)]
        },

        (Cor.PRETO, "longo"): {
            "direito": "roque_longo_preto",
            "origem_rei": (0, 4),
            "destino_rei": (0, 2),
            "origem_torre": (0, 0),
            "destino_torre": (0, 3),
            "casas_seguras": [(0, 3), (0, 2)]
        }
    }


    def __init__(self) -> None:
        """
        Inicializa a engine com o tabuleiro vazio e carrega a posição inicial.
        """
        self.matriz: np.ndarray = np.full((8, 8), None, dtype=object)
        self.movimentos_possiveis:  list[tuple[tuple[int, int], TipoMov]]   = []
        self.pseudo_movimentos:     list[tuple[tuple[int, int], TipoMov]]   = []

        self.roque_curto_branco:    bool = True
        self.roque_longo_branco:    bool = True
        self.roque_curto_preto:     bool = True
        self.roque_longo_preto:     bool = True

        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

        self.carregar_posicao_fen(fen='8/8/8/4p3/3P4/k7/8/K7 w - - 99 60')
        self.turno = Cor.BRANCO

        self.en_passant: None | list[tuple[int, int], TipoMov] = None
        self.posicao_peao_en_passant: list[tuple[int, int]] = []
        self.posicao_alvo_en_passant: tuple[int, int] = None

        self.vitoria_negras:    bool = False
        self.vitoria_brancas:   bool = False
        self.empate:            bool = False


    def movimento_possivel(self, mov: Movimento) -> bool:
        """
        Valida se um movimento está dentro dos movimentos possíveis.

        Args:
            mov (Movimento): Objeto contendo as coordenadas de origem e destino.

        Returns:
            bool: True se o movimento for valido, False caso contrário.
        """
        destinos_validos = [m[0] for m in self.movimentos_possiveis]
        
        return mov.destino in destinos_validos


    def _verificar_insuficiencia_material(self) -> bool:
        """
        Verifica se restam peças suficientes para aplicar um xeque-mate.
        Regras básicas da FIDE:
        1. Rei vs Rei
        2. Rei e Bispo vs Rei
        3. Rei e Cavalo vs Rei
        4. Rei e Bispo vs Rei e Bispo (mesma cor de casa)
        """
        pecas_vivas: list[Peca] = []
        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if p is not None and not isinstance(p, Rei):
                    pecas_vivas.append(p)

        if len(pecas_vivas) == 0:
            return True

        if len(pecas_vivas) == 1:
            p = pecas_vivas[0]
            if isinstance(p, (Bispo, Cavalo)):
                return True

        if len(pecas_vivas) == 2:
            p1, p2 = pecas_vivas[0], pecas_vivas[1]
            if isinstance(p1, Bispo) and isinstance(p2, Bispo):
                pos1 = self.achar_lc_peca(p1)
                pos2 = self.achar_lc_peca(p2)
                if (pos1[0] + pos1[1]) % 2 == (pos2[0] + pos2[1]) % 2:
                    return True

        return False


    def executar_movimento(self, mov: Movimento, interno: bool=False) -> bool:
        p = self.matriz[mov.origem[0], mov.origem[1]]

        if p is None:
            return False
        
        captura = (
            self.matriz[mov.destino[0], mov.destino[1]]
            is not None
        )

        en_passant_antigo = self.en_passant
        peoes_en_passant_antigo = self.posicao_peao_en_passant.copy()
        alvo_en_passant_antigo = self.posicao_alvo_en_passant

        self.en_passant = None
        self.posicao_peao_en_passant = []
        self.posicao_alvo_en_passant = None

        if isinstance(p, Torre):
            if p.cor == Cor.BRANCO:
                if mov.origem[1] == 0:
                    self.roque_longo_branco = False
                elif mov.origem[1] == 7:
                    self.roque_curto_branco = False

            elif p.cor == Cor.PRETO:
                if mov.origem[1] == 0:
                    self.roque_longo_preto = False
                elif mov.origem[1] == 7:
                    self.roque_curto_preto = False

        if isinstance(p, Rei) and not interno:
            distancia_c = mov.destino[1] - mov.origem[1]

            if abs(distancia_c) == 2:
                if self.verificar_e_aplicar_roque(p.cor, distancia_c):
                    self.mudar_turno()
                    self.limpar_movimentos()
                    return True

                return False

            if p.cor == Cor.BRANCO:
                self.roque_curto_branco = False
                self.roque_longo_branco = False

            else:
                self.roque_curto_preto = False
                self.roque_longo_preto = False

        if isinstance(p, Peao):
            distancia_l = mov.destino[0] - mov.origem[0]

            if (
                p.posicao in peoes_en_passant_antigo
                and
                en_passant_antigo is not None
                and
                mov.destino == en_passant_antigo[0]
            ):
                self.matriz[alvo_en_passant_antigo] = None

            if abs(distancia_l) == 2:
                linha, coluna = mov.destino

                direcao = -1 if p.cor == Cor.PRETO else 1

                self.en_passant = [
                    (
                        linha + direcao,
                        coluna
                    ),
                    TipoMov.CAPTURA
                ]

                self.posicao_alvo_en_passant = mov.destino

                for dc in (-1, 1):
                    c_vizinho = coluna + dc

                    if self.lc_valido(linha, c_vizinho):
                        vizinho = self.matriz[linha, c_vizinho]

                        if (
                            isinstance(vizinho, Peao)
                            and
                            vizinho.cor != p.cor
                        ):
                            self.posicao_peao_en_passant.append(
                                (linha, c_vizinho)
                            )

        self.matriz[mov.destino[0], mov.destino[1]] = p
        self.matriz[mov.origem[0], mov.origem[1]] = None

        p.posicao = mov.destino

        if not interno:
            self.limpar_movimentos()

        if isinstance(p, Peao) or captura:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.mudar_turno()

        if self.turno == Cor.BRANCO:
            self.fullmove_number += 1

        if self._verificar_fim_de_jogo(self.turno):
            self.finalizado = True

        return True


    def _tem_movimentos_legais(self, cor: str) -> bool:
        """
        Verifica se o jogador da cor atual possui pelo menos um movimento legal.
        Usa a estratégia de saída antecipada para performance.

        Args:
            cor (str): Cor do jogador.

        Returns:
            bool: True se o jogador possui pelo menos um movimento legal.
        """
        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if p is not None and p.cor == cor:
                    pseudo = p.gerar_pseudo_movimentos(lc=(li, co))
                    candidatos = self._classificar_movimentos(p, (li, co), pseudo)
                    
                    if isinstance(p, Rei):
                        self._adicionar_roques(cor, candidatos)
                    if (
                        isinstance(p, Peao) and
                        p.posicao in self.posicao_peao_en_passant
                    ):
                        self._adicionar_en_passant(candidatos)
                    
                    for destino, tipo in candidatos:
                        if self._testar_movimento(destino, tipo, (li, co), cor):
                            return True
                            
        return False
    

    def _contagem_material(self) -> dict:
        """
        Conta a quantidade de peças de cada cor.

        Returns:
            dict: Dicionário com a contagem de peças de cada cor.
        """
        brancas = 0
        pretas = 0
        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if p is not None:
                    if p.cor == Cor.BRANCO:
                        brancas += p.pontuacao
                    else:
                        pretas += p.pontuacao
        return {
            Cor.BRANCO: brancas,
            Cor.PRETO: pretas
        }


    @property
    def finalizado(self) -> bool:
        """Retorna True se o jogo acabou (Vitória ou Empate)."""
        return self.vitoria_brancas or self.vitoria_negras or self.empate


    def _verificar_xeque_mate_ou_afogamento(
        self,
        cor_atual: str
    ) -> bool:
        """
        Verifica xeque-mate ou afogamento.

        Args:
            cor_atual (str): Cor do jogador atual.

        Returns:
            bool: True se o jogo terminou.
        """
        if self._tem_movimentos_legais(cor_atual):
            return False

        if self.verificar_xeque(cor_atual):
            if cor_atual == Cor.BRANCO:
                self.vitoria_negras = True
                cor_vencedora = "Pretas"
            else:
                self.vitoria_brancas = True
                cor_vencedora = "Brancas"

            print(f"Xeque-Mate! Vitória das {cor_vencedora}.")
        else:
            self.empate = True
            print("Empate por afogamento (Stalemate).")

        return True


    def _verificar_empate_50_lances(self) -> bool:
        """
        Verifica empate pela regra dos 50 lances.

        Returns:
            bool: True se houver empate.
        """
        if self.halfmove_clock >= 100:
            self.empate = True
            print("Empate pela regra dos 50 lances.")
            return True

        return False


    def _verificar_empate_insuficiencia_material(self) -> bool:
        """
        Verifica empate por insuficiência de material.

        Returns:
            bool: True se houver empate.
        """
        if self._verificar_insuficiencia_material():
            self.empate = True
            print("Empate por insuficiência de material.")
            return True

        return False


    def _verificar_fim_de_jogo(self, cor_atual: str) -> None:
        """
        Agrega todas as checagens de fim de partida.
        """

        if self._verificar_xeque_mate_ou_afogamento(cor_atual):
            return

        if self._verificar_empate_insuficiencia_material():
            return

        if self._verificar_empate_50_lances():
            return


    def verificar_e_aplicar_roque(
        self,
        cor: Cor,
        distancia_c: int
    ) -> bool:
        lado = "curto" if distancia_c > 0 else "longo"

        if self.verificar_roque(cor, lado):
            self.executar_roque(cor, lado)
            return True

        return False


    def _casa_atacada(self, l: int, c: int, cor_rei: str) -> bool:
        """
        Método auxiliar para checar se uma casa específica está sob ataque.

        Args:
            l (int): Linha da casa.
            c (int): Coluna da casa.
            cor_rei (str): Cor do rei.

        Returns:
            bool: True se a casa estiver sob ataque, False caso contrário.
        """
        pos_original = self.achar_lc_rei(cor_rei)
        rei = self.matriz[pos_original[0], pos_original[1]]
        
        backup = self.matriz[l, c]
        self.matriz[pos_original[0], pos_original[1]] = None
        self.matriz[l, c] = rei
        
        atacada = self.verificar_xeque(cor_rei)
        
        self.matriz[l, c] = backup
        self.matriz[pos_original[0], pos_original[1]] = rei
        return atacada


    def verificar_roque(self, cor: Cor, lado: str) -> bool:
        """
        Retorna True se o roque pode ser realizado.

        Args:
            cor (str): Cor do rei.
            lado (str): "curto" ou "longo".

        Returns:
            bool: True se o roque pode ser realizado, False caso contrário.
        """
        dados = self.ROQUES[(cor, lado)]

        direito = getattr(self, dados["direito"])

        if not direito:
            return False

        if self.verificar_xeque(cor):
            return False

        if not self._caminho_livre(
            origem=dados["origem_rei"],
            destino=dados["origem_torre"]
        ):
            return False

        for l, c in dados["casas_seguras"]:
            if self._casa_atacada(l, c, cor):
                return False

        return True


    def executar_roque(self, cor: Cor, lado: str) -> None:
        """
        Executa um roque.

        Args:
            cor (str): Cor do rei.
            lado (str): "curto" ou "longo".
        """
        dados = self.ROQUES[(cor, lado)]

        # Move rei
        self.executar_movimento(
            mov=Movimento(
                origem=dados["origem_rei"],
                destino=dados["destino_rei"]
            ),
            interno=True
        )

        # Move torre
        self.executar_movimento(
            mov=Movimento(
                origem=dados["origem_torre"],
                destino=dados["destino_torre"]
            ),
            interno=True
        )


    def mudar_turno(self) -> None:
        """
        Alterna o turno atual entre branco ('w') e preto ('b').
        """
        if self.turno == Cor.BRANCO:
            self.turno = Cor.PRETO
        else:
            self.turno = Cor.BRANCO


    def carregar_posicao_fen(self, fen: str) -> None:
        """
        Carrega uma posição completa no padrão FEN, atualizando o tabuleiro,
        turno, direitos de roque e estado de en passant.
        """
        partes = fen.strip().split()
        if len(partes) < 6:
            raise ValueError(
                "FEN inválida: deve conter pelo menos os 4 campos iniciais."
            )

        (
            tabuleiro_str,
            turno,
            roques,
            ep_square,
            halfmove_clock,
            fullmove_number
        ) = partes[:6]

        self.matriz.fill(None)

        ranks = tabuleiro_str.split('/')
        if len(ranks) != 8:
            raise ValueError(
                "FEN inválida: piece placement deve ter 8 ranks."
            )

        for i, rank in enumerate(ranks):
            j = 0
            for ch in rank:
                if ch.isdigit():
                    j += int(ch)
                else:
                    cor = Cor.BRANCO if ch.isupper() else Cor.PRETO
                    tipo = ch.lower()
                    self.matriz[i, j] = self.criar_peca(
                        tipo=tipo,
                        cor=cor,
                        pos=[i, j]
                    )

                    j += 1

        self.turno = turno

        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)

        self.roque_curto_branco = 'K' in roques
        self.roque_longo_branco = 'Q' in roques
        self.roque_curto_preto  = 'k' in roques
        self.roque_longo_preto  = 'q' in roques

        self.en_passant = None
        self.posicao_alvo_en_passant = None
        self.posicao_peao_en_passant = []

        if ep_square != '-':
            coluna_ep = ord(ep_square[0]) - ord('a')
            linha_ep = 8 - int(ep_square[1])
            
            self.en_passant = [(linha_ep, coluna_ep), TipoMov.CAPTURA]
            
            direcao = 1 if linha_ep == 2 else -1
            self.posicao_alvo_en_passant = (linha_ep + direcao, coluna_ep)

            for dc in [-1, 1]:
                c_vizinho = coluna_ep + dc
                l_vizinho = linha_ep + direcao
                if self.lc_valido(l_vizinho, c_vizinho):
                    p = self.matriz[l_vizinho, c_vizinho]
                    if (
                        isinstance(p, Peao) and
                        p.cor != self.matriz[self.posicao_alvo_en_passant].cor
                    ):
                        self.posicao_peao_en_passant.append((
                            l_vizinho,
                            c_vizinho
                        ))


    def exportar_posicao_fen(self) -> str:
        """
        Exporta a posição atual no padrão FEN.

        Returns:
            str: String FEN da posição atual.
        """

        ranks = []

        for linha in self.matriz:
            rank = ""
            vazias = 0

            for peca in linha:
                if peca is None:
                    vazias += 1
                    continue

                if vazias > 0:
                    rank += str(vazias)
                    vazias = 0

                simbolo = peca.tipo.value

                if peca.cor == Cor.BRANCO:
                    simbolo = simbolo.upper()

                rank += simbolo

            if vazias > 0:
                rank += str(vazias)

            ranks.append(rank)

        tabuleiro_str = "/".join(ranks)

        turno = self.turno

        roques = ""

        if self.roque_curto_branco:
            roques += "K"

        if self.roque_longo_branco:
            roques += "Q"

        if self.roque_curto_preto:
            roques += "k"

        if self.roque_longo_preto:
            roques += "q"

        if roques == "":
            roques = "-"

        ep_square = "-"

        if self.en_passant is not None:
            linha, coluna = self.en_passant[0]

            arquivo = chr(ord("a") + coluna)
            rank = str(8 - linha)

            ep_square = f"{arquivo}{rank}"

        halfmove_clock = self.halfmove_clock
        fullmove_number = self.fullmove_number

        return (
            f"{tabuleiro_str} "
            f"{turno} "
            f"{roques} "
            f"{ep_square} "
            f"{halfmove_clock} "
            f"{fullmove_number}"
        )


    def criar_peca(self, tipo: str, cor: str, pos: list[int]) -> Peca:
        """
        Instancia uma peça baseada no tipo e cor fornecidos.

        Args:
            tipo (str): Caractere representando o tipo da peça.
            cor (str): 'w' para branco, 'b' para preto.
            pos (list[int]): Coordenadas [linha, coluna].

        Returns:
            Peca: Instância da classe da peça correspondente.
        """
        return self.MAPA_PECAS[tipo](
            cor=cor,
            posicao=pos
        )


    def achar_lc_peca(self, peca: Peca) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            tuple[int, int] | None: (linha, coluna) ou None se não encontrada.
        """
        for li in range(8):
            for co in range(8):
                if self.matriz[li, co] == peca:
                    return (li, co)
        return None


    def achar_lc_rei(self, cor: Cor) -> tuple[int, int] | None:
        """
        Encontra a linha e coluna de uma instância de peça na matriz.

        Args:
            peca (Peca): Instância da peça a ser localizada.

        Returns:
            tuple[int, int] | None: (linha, coluna) ou None se não encontrada.
        """
        for li in range(8):
            for co in range(8):
                p = self.matriz[li, co]
                if isinstance(p, Rei):
                    if p.cor == cor:
                        return (li, co)
        return None 


    def gerar_mov_peca(self, p: Peca) -> None:
        """
        Gera os movimentos possíveis de uma peça.

        Args:
            p (Peca): Instância da peça a ser movimentada.
        """
        origem = self.achar_lc_peca(peca=p)
        if origem is None:
            self.movimentos_possiveis = []
            self.pseudo_movimentos = []
            return

        self.pseudo_movimentos = p.gerar_pseudo_movimentos(lc=origem)
        
        candidatos = self._classificar_movimentos(
            peca=p,
            origem=origem,
            movimentos=self.pseudo_movimentos
        )

        if isinstance(p, Rei):
            self._adicionar_roques(self.turno, candidatos)
        
        if isinstance(p, Peao):
            if p.posicao in self.posicao_peao_en_passant:
                self._adicionar_en_passant(candidatos)
        
        movimentos_validos = []
        for destino, tipo in candidatos:
            if self._testar_movimento(destino, tipo, origem, self.turno):
                movimentos_validos.append((destino, tipo))
        
        self.movimentos_possiveis = movimentos_validos

        # if DEBUG:
        #     print(self.movimentos_possiveis)


    def _testar_movimento(
        self,
        mov_destino: tuple[int, int],
        tipo: TipoMov,
        origem: tuple[int, int],
        cor: str
    ) -> bool:
        """
        Simula um movimento para verificar se ele resultaria no próprio rei em xeque.

        Args:
            mov_destino (tuple[int, int]): (linha, coluna) do destino.
            tipo (TipoMov): Tipo de movimento.
            origem (tuple[int, int]): (linha, coluna) da origem.
            cor (str): 'w' para branco, 'b' para preto.

        Returns:
            bool: True se o movimento resultar em xeque, False caso contrário.
        """
        backup_destino = self.matriz[mov_destino[0], mov_destino[1]]
        peca_movendo = self.matriz[origem[0], origem[1]]
        
        backup_en_passant_peao = None
        pos_peao_en_passant = None
        
        is_en_passant = (
            isinstance(peca_movendo, Peao)
            and
            tipo == TipoMov.CAPTURA
            and
            backup_destino is None
        )

        if is_en_passant:
            pos_peao_en_passant = self.posicao_alvo_en_passant
            backup_en_passant_peao = self.matriz[pos_peao_en_passant]
            self.matriz[pos_peao_en_passant] = None

        self.matriz[mov_destino[0], mov_destino[1]] = peca_movendo
        self.matriz[origem[0], origem[1]] = None

        em_xeque = self.verificar_xeque(cor)

        self.matriz[origem[0], origem[1]] = peca_movendo
        self.matriz[mov_destino[0], mov_destino[1]] = backup_destino
        
        if is_en_passant:
            self.matriz[pos_peao_en_passant] = backup_en_passant_peao

        return not em_xeque


    def _adicionar_en_passant(self, mov: list) -> None:
        """
        Adiciona as casas de en passant na lista de movimentos possíveis.

        Args:
            mov (list): Lista de movimentos.

        Returns:
            list: Lista de movimentos com os movimentos de en passant adicionados.
        """
        mov.append(self.en_passant)


    def _adicionar_roques(
        self,
        cor: str,
        mov: list
    ) -> list[tuple[int, int], TipoMov]:
        if self.verificar_roque(cor, "curto"):
            destino = (
                self.ROQUES[(cor, "curto")]["destino_rei"]
            )

            mov.append((destino, TipoMov.ROQUE_CURTO))

        if self.verificar_roque(cor, "longo"):
            destino = (
                self.ROQUES[(cor, "longo")]["destino_rei"]
            )

            mov.append((destino, TipoMov.ROQUE_LONGO))

        return mov


    def limpar_movimentos(self) -> None:
        """
        Limpa os movimentos pseudo-legais e movimentos possíveis.
        """
        self.limpar_pseudo_movimentos()
        self.limpar_movimentos_possiveis()
    

    def limpar_pseudo_movimentos(self) -> None:
        """
        Limpa APENAS os movimentos pseudo-legais.
        """
        self.pseudo_movimentos.clear()
    
    
    def limpar_movimentos_possiveis(self) -> None:
        """
        Limpa APENAS os movimentos possíveis.
        """
        self.movimentos_possiveis.clear()


    def _classificar_movimentos(
        self,
        peca: Peca,
        origem: tuple[int, int],
        movimentos: list[tuple[int, int]]
    ) -> list[tuple[tuple[int, int], TipoMov]]:
        """
        Classifica movimentos pseudo-legais como normais ou de captura.

        Args:
            peca (Peca): A peça que está se movendo.
            origem (tuple[int, int]): Casa de origem.
            movimentos (list[tuple[int, int]]): Lista de destinos pseudo-legais.

        Returns:
            list[tuple[tuple[int, int], TipoMov]]: Destinos validados com seu tipo.
        """
        movs: list[tuple[tuple[int, int], TipoMov]] = []
        for casa in movimentos:
            tipo = self._classificar_movimento(
                peca=peca,
                origem=origem,
                destino_lc=casa
            )
            if tipo is not None:
                movs.append((casa, tipo))
        return movs


    def _classificar_movimento(
        self,
        peca: Peca,
        origem: tuple[int, int],
        destino_lc: tuple[int, int]
    ) -> TipoMov | None:
        """
        Valida logicamente se um movimento pode ser realizado.

        Args:
            peca (Peca): Peça em movimento.
            origem (tuple[int, int]): Coordenada de origem.
            destino_lc (tuple[int, int]): Coordenada de destino.

        Returns:
            TipoMov | None: Tipo do movimento se válido, None caso contrário.
        """
        destino = self.matriz[destino_lc[0], destino_lc[1]]

        if isinstance(peca, Peao):
            delta = (destino_lc[0] - origem[0], destino_lc[1] - origem[1])
            if peca.cor == Cor.BRANCO:
                forward = (-1, 0)
                double_forward = (-2, 0)
                captures = [(-1, -1), (-1, 1)]
            else:
                forward = (1, 0)
                double_forward = (2, 0)
                captures = [(1, -1), (1, 1)]

            if delta == forward:
                return TipoMov.NORMAL if destino is None else None

            if delta == double_forward:
                meio = (origem[0] + forward[0], origem[1])
                if destino is None and self.matriz[meio[0], meio[1]] is None:
                    return TipoMov.NORMAL
                return None

            if delta in captures:
                if destino is not None and destino.cor != peca.cor:
                    return TipoMov.CAPTURA
                return None

            return None

        if isinstance(peca, (Bispo, Dama, Torre)):
            if not self._caminho_livre(origem=origem, destino=destino_lc):
                return None

        if destino is not None:
            if destino.cor == peca.cor:
                return None
            return TipoMov.CAPTURA

        return TipoMov.NORMAL


    def _caminho_livre(
            self,
            origem: tuple[int, int],
            destino: tuple[int, int]
    ) -> bool:
        """
        Verifica se há obstáculos entre duas casas para peças deslizantes.

        Args:
            origem (tuple[int, int]): Casa inicial.
            destino (tuple[int, int]): Casa final.

        Returns:
            bool: True se o caminho estiver vazio, False caso contrário.
        """
        delta = (destino[0] - origem[0], destino[1] - origem[1])
        passo_l = 0 if delta[0] == 0 else (1 if delta[0] > 0 else -1)
        passo_c = 0 if delta[1] == 0 else (1 if delta[1] > 0 else -1)

        if passo_l == 0 and passo_c == 0:
            return False

        atual = (origem[0] + passo_l, origem[1] + passo_c)
        while atual != destino:
            if self.matriz[atual[0], atual[1]] is not None:
                return False
            atual = (atual[0] + passo_l, atual[1] + passo_c)
        return True


    def verificar_xeque(self, cor: str) -> bool:
        """
        Verifica se o rei da cor informada está sob ataque.

        Args:
            cor (str): Cor do rei a ser verificado.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        cor = cor.lower()
        if cor not in (Cor.PRETO, Cor.BRANCO):
            raise ValueError('Cor precisa ser "w" ou "b"')
        
        lc_rei = self.achar_lc_rei(cor=cor)
        if lc_rei is None:
            return False

        horizontais =   self._verificar_horizontais(lc_rei=lc_rei, cor=cor)
        diagonais   =   self._verificar_diagonais(lc_rei=lc_rei, cor=cor)
        cavalo      =   self._verificar_cavalo(lc_rei=lc_rei, cor=cor)
        rei         =   self._verificar_rei(lc_rei=lc_rei, cor=cor)
        peao        =   self._verificar_peao(lc_rei=lc_rei, cor=cor)

        return horizontais or diagonais or cavalo or rei or peao
    

    def _verificar_horizontais(self, lc_rei: tuple[int, int], cor: str) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças horizontais.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcoes_horizontais = ((0, 1), (0, -1), (1, 0), (-1, 0))
        for direcao in direcoes_horizontais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.lc_valido(linha=l, coluna=c):
                    break
                destino = self.matriz[l, c]
                if destino is None:
                    continue
                if destino.cor != cor and isinstance(destino, (Torre, Dama)):
                    return True
                break
        return False
    

    def _verificar_diagonais(self, lc_rei: tuple[int, int], cor: str) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças diagonais.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcoes_diagonais = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        for direcao in direcoes_diagonais:
            l, c = lc_rei
            while True:
                l += direcao[0]
                c += direcao[1]
                if not self.lc_valido(linha=l, coluna=c): break
                destino = self.matriz[l, c]
                if destino is None: continue
                if destino.cor != cor and isinstance(destino, (Bispo, Dama)):
                    return True
                break
        return False


    def _verificar_cavalo(self, lc_rei: tuple[int, int], cor: str) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de cavalo.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        offsets_cavalo = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (2, -1),
            (2, 1),
            (1, -2),
            (1, 2)
        ]
        for offset in offsets_cavalo:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Cavalo) and destino.cor != cor:
                    return True
        return False


    def _verificar_rei(self, lc_rei: tuple[int, int], cor: str) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de rei.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        offsets_rei = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, -1),
            (0, 1)
        ]
        for offset in offsets_rei:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Rei) and destino.cor != cor:
                    return True
        return False


    def _verificar_peao(self, lc_rei: tuple[int, int], cor: str) -> bool:
        """
        Verifica se o rei estiver sob ataque por peças de peão.

        Args:
            lc_rei (tuple[int, int]): Posição do rei.
            cor (str): Cor do rei.

        Returns:
            bool: True se estiver em xeque, False caso contrário.
        """
        direcao = -1 if cor == Cor.BRANCO else 1
        offsets_peao = [(direcao, -1), (direcao, 1)]
        for offset in offsets_peao:
            l, c = lc_rei[0] + offset[0], lc_rei[1] + offset[1]
            if self.lc_valido(linha=l, coluna=c):
                destino = self.matriz[l, c]
                if destino and isinstance(destino, Peao) and destino.cor != cor:
                    return True
        return False


    @staticmethod
    def lc_valido(linha: int, coluna: int) -> bool:
        """
        Verifica se a coordenada informada está dentro dos limites do tabuleiro.

        Returns:
            bool: True se válida, False caso contrário.
        """
        return 0 <= linha < 8 and 0 <= coluna < 8 

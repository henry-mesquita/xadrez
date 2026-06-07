from constantes import *
from pecas.peca import Peca, Cor, TipoPeca
from pecas.bispo import Bispo
from pecas.cavalo import Cavalo
from pecas.dama import Dama
from pecas.peao import Peao
from pecas.rei import Rei
from pecas.torre import Torre
from .move import *
from .judge import Judge
from .generator import Generator
from .fen_parser import *
from .state import GameState
from .factory import criar_peca


class Engine:
    """
    Gerenciador de lógica e estado do jogo de xadrez.

    Controla o tabuleiro, valida movimentos, gera movimentos possíveis, gerencia
    turnos e verifica condições de xeque. Totalmente desacoplada da camada visual.
    """

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
        self.state: GameState       = GameState()
        self.generator: Generator   = Generator(self.state.board)
        self.judge: Judge           = Judge(self.generator)

        self.movimentos_possiveis:  list[tuple[tuple[int, int], TipoMov]]   = []
        self.pseudo_movimentos:     list[tuple[tuple[int, int], TipoMov]]   = []

        carregar_posicao_fen(
            state=self.state,
            fen=FEN_INICIAL,
            board=self.state.board
        )

        self.posicoes_jogadas: list[str] = []

        self.casa_promocao: tuple[int, int] | None = None
        self.aguardando_promocao = False
        self.ultimo_mov: Movimento | None = None

        self.historico: list[EstadoHistorico] = []


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
        Verifica se a posição é um empate por insuficiência de material (Dead Position).
        Regras FIDE (Artigo 5.2.2): O jogo está empatado quando surge uma posição 
        onde nenhum xeque-mate pode ocorrer por qualquer série de lances legais.
        """
        pecas_brancas = []
        pecas_pretas = []
        
        for r in range(8):
            for c in range(8):
                peca = self.state.board.matriz[r, c]
                if peca is None or isinstance(peca, Rei):
                    continue
                
                if isinstance(peca, (Peao, Torre, Dama)):
                    return False
                
                info = (type(peca), (r + c) % 2)
                
                if peca.cor == Cor.BRANCO:
                    pecas_brancas.append(info)
                else:
                    pecas_pretas.append(info)

        total_menores = len(pecas_brancas) + len(pecas_pretas)

        # Rei vs Rei
        if total_menores == 0:
            return True

        # Rei e Peça Menor
        if total_menores == 1:
            return True

        # Rei e Bispo vs Rei e Bispo (Bispos na mesma cor de casa)
        if all(tipo == Bispo for tipo, _ in pecas_brancas + pecas_pretas):
            cor_da_casa_referencia = (pecas_brancas + pecas_pretas)[0][1]
            if all(cor_casa == cor_da_casa_referencia for _, cor_casa in pecas_brancas + pecas_pretas):
                return True

        return False


    def executar_movimento(
        self,
        mov: Movimento,
        interno: bool = False,
        promocao_alvo: TipoPeca | None = None
    ) -> bool:
        """
        Executa um movimento.

        Args:
            mov (Movimento): Objeto contendo as coordenadas de origem e destino.
            interno (bool): True se o movimento foi executado internamente, False caso contrário.
            promocao_alvo (TipoPeca): Tipo da peça para promoção automática em testes.

        Returns:
            bool: True se o movimento foi executado, False caso contrário.
        """
        p = self.state.board.matriz[mov.origem[0], mov.origem[1]]
        if p is None:
            return False
        
        peca_destino = self.state.board.matriz[mov.destino[0], mov.destino[1]]
        peca_capturada = peca_destino
        pos_captura = mov.destino

        if isinstance(p, Peao):
            if self.state.en_passant is not None:
                if mov.destino == self.state.en_passant[0]:
                    pos_captura = self.state.posicao_alvo_en_passant
                    peca_capturada = self.state.board.matriz[pos_captura[0], pos_captura[1]]

        foi_promocao = False
        if isinstance(p, Peao):
            if mov.destino[0] == 0 or mov.destino[0] == 7:
                foi_promocao = True

        self.historico.append(EstadoHistorico(
            movimento=mov,
            peca_movida=p,
            peca_capturada=peca_capturada,
            pos_peca_capturada=pos_captura,
            roque_curto_branco=self.state.roque_curto_branco,
            roque_longo_branco=self.state.roque_longo_branco,
            roque_curto_preto=self.state.roque_curto_preto,
            roque_longo_preto=self.state.roque_longo_preto,
            en_passant=self.state.en_passant,
            posicao_peao_en_passant=self.state.posicao_peao_en_passant.copy(),
            posicao_alvo_en_passant=self.state.posicao_alvo_en_passant,
            halfmove_clock=self.state.halfmove_clock,
            ultimo_mov=self.ultimo_mov,
            foi_promocao=foi_promocao
        ))

        if peca_capturada is not None:
            self.state.board.matriz[pos_captura[0], pos_captura[1]] = None

        if not interno:
            self.limpar_movimentos()

        self.state.en_passant = None
        self.state.posicao_peao_en_passant = []
        self.state.posicao_alvo_en_passant = None

        if isinstance(p, Torre):
            self._remover_direito_roque(p.cor, mov.origem[1])
        
        if mov.destino == (7, 7):   self.state.roque_curto_branco = False
        elif mov.destino == (7, 0): self.state.roque_longo_branco = False
        elif mov.destino == (0, 7): self.state.roque_curto_preto  = False
        elif mov.destino == (0, 0): self.state.roque_longo_preto  = False

        if isinstance(p, Rei):
            distancia_c = mov.destino[1] - mov.origem[1]
            if abs(distancia_c) == 2:
                self._mover_torre_roque(p.cor, distancia_c)
            
            if p.cor == Cor.BRANCO:
                self.state.roque_curto_branco = False
                self.state.roque_longo_branco = False
            else:
                self.state.roque_curto_preto = False
                self.state.roque_longo_preto = False

        if isinstance(p, Peao):
            distancia_l = mov.destino[0] - mov.origem[0]
            if abs(distancia_l) == 2:
                linha, coluna = mov.destino
                if p.cor == Cor.BRANCO:
                    direcao = 1
                else:
                    direcao = -1
                
                self.state.en_passant = [(linha + direcao, coluna), TipoMov.CAPTURA]
                self.state.posicao_alvo_en_passant = mov.destino
                for dc in (-1, 1):
                    c_viz = coluna + dc
                    if self.state.board.lc_valido(linha, c_viz):
                        v = self.state.board.matriz[linha, c_viz]
                        if isinstance(v, Peao):
                            if v.cor != p.cor:
                                self.state.posicao_peao_en_passant.append((linha, c_viz))

        self.state.board.matriz[mov.destino[0], mov.destino[1]] = p
        self.state.board.matriz[mov.origem[0], mov.origem[1]] = None
        p.posicao = (mov.destino[0], mov.destino[1])
        self.ultimo_mov = mov

        if foi_promocao:
            tipo_para_promover = promocao_alvo
            if tipo_para_promover is None:
                if interno:
                    tipo_para_promover = TipoPeca.DAMA
            
            if tipo_para_promover is not None:
                self.state.board.matriz[mov.destino[0], mov.destino[1]] = criar_peca(
                    tipo=tipo_para_promover.value,
                    cor=p.cor,
                    pos=[mov.destino[0], mov.destino[1]]
                )
            else:
                self.aguardando_promocao = True
                self.casa_promocao = mov.destino
                return True 

        self._finalizar_turno(
            captura=(peca_capturada is not None),
            peao=isinstance(p, Peao),
            interno=interno
        )
        return True


    def desfazer_movimento(self, interno: bool = False) -> None:
        """
        Reverte o último movimento realizado, restaurando o estado anterior.

        Args:
            interno (bool): True se o movimento a ser desfeito foi uma simulação interna.
        """
        if len(self.historico) == 0:
            return

        if not interno and self.posicoes_jogadas:
            self.posicoes_jogadas.pop()

        estado = self.historico.pop()
        mov = estado.movimento

        if self.state.turno == Cor.BRANCO:
            self.state.fullmove_number -= 1
        self.mudar_turno()

        self.state.roque_curto_branco = estado.roque_curto_branco
        self.state.roque_longo_branco = estado.roque_longo_branco
        self.state.roque_curto_preto = estado.roque_curto_preto
        self.state.roque_longo_preto = estado.roque_longo_preto
        self.state.en_passant = estado.en_passant
        self.state.posicao_peao_en_passant = estado.posicao_peao_en_passant
        self.state.posicao_alvo_en_passant = estado.posicao_alvo_en_passant
        self.state.halfmove_clock = estado.halfmove_clock
        self.ultimo_mov = estado.ultimo_mov
        self.aguardando_promocao = False

        p = estado.peca_movida

        self.state.board.matriz[mov.destino[0], mov.destino[1]] = None
        self.state.board.matriz[mov.origem[0], mov.origem[1]] = p
        p.posicao = (mov.origem[0], mov.origem[1])

        if estado.peca_capturada is not None:
            pos_cap = estado.pos_peca_capturada
            self.state.board.matriz[pos_cap[0], pos_cap[1]] = estado.peca_capturada
            estado.peca_capturada.posicao = (pos_cap[0], pos_cap[1])

        if isinstance(p, Rei):
            distancia_c = mov.destino[1] - mov.origem[1]
            if abs(distancia_c) == 2:
                l = mov.origem[0]
                if mov.destino[1] == 6:
                    torre = self.state.board.matriz[l, 5]
                    self.state.board.matriz[l, 7] = torre
                    self.state.board.matriz[l, 5] = None
                    if torre:
                        torre.posicao = (l, 7)
                else:
                    torre = self.state.board.matriz[l, 3]
                    self.state.board.matriz[l, 0] = torre
                    self.state.board.matriz[l, 3] = None
                    if torre:
                        torre.posicao = (l, 0)


    def _testar_movimento(
        self,
        mov_destino: tuple[int, int],
        origem: tuple[int, int],
        cor: str
    ) -> bool:
        """
        Verifica se um movimento dado eh valido.

        Args:
            mov_destino (tuple[int, int]): Coordenadas de destino.
            tipo (TipoMov): Tipo de movimento.
            origem (tuple[int, int]): Coordenadas de origem.
            cor (str): Cor do jogador.

        Returns:
            bool: True se o movimento for valido, False caso contrário.
        """
        self.executar_movimento(Movimento(origem=origem, destino=mov_destino), interno=True)
        em_xeque = self.verificar_xeque(cor)
        self.desfazer_movimento(interno=True)

        return not em_xeque


    def _remover_direito_roque(self, cor: Cor, coluna: int) -> None:
        """
        Auxiliar para tirar roque se a torre mover ou morrer.

        Args:
            cor (Cor): Cor do jogador.
            coluna (int): Coluna da torre.
        """
        if cor == Cor.BRANCO:
            if coluna == 0: self.state.roque_longo_branco = False
            if coluna == 7: self.state.roque_curto_branco = False
        else:
            if coluna == 0: self.state.roque_longo_preto = False
            if coluna == 7: self.state.roque_curto_preto = False


    def _mover_torre_roque(self, cor: Cor, distancia_c: int) -> None:
        """
        Move a torre durante o roque sem chamar finalizar_turno.

        Args:
            cor (Cor): Cor do jogador.
            distancia_c (int): Diferença de colunas entre a torre e o rei.
        """
        l = 7 if cor == Cor.BRANCO else 0
        if distancia_c > 0: # Curto
            torre = self.state.board.matriz[l, 7]
            self.state.board.matriz[l, 5] = torre
            self.state.board.matriz[l, 7] = None
            if torre: torre.posicao = (l, 5)
        else: # Longo
            torre = self.state.board.matriz[l, 0]
            self.state.board.matriz[l, 3] = torre
            self.state.board.matriz[l, 0] = None
            if torre: torre.posicao = (l, 3)


    def _finalizar_turno(self, captura: bool, peao: bool, interno: bool) -> None:
        """
        Método auxiliar para concluir a lógica de fim de turno.

        Args:
            captura (bool): True se houver captura, False caso contrário.
            peao (bool): True se houver peão, False caso contrário.
            interno (bool): True se o movimento foi executado pela engine.
        """
        if peao or captura:
            self.state.halfmove_clock = 0
        else:
            self.state.halfmove_clock += 1

        self.mudar_turno()
        if self.state.turno == Cor.BRANCO:
            self.state.fullmove_number += 1
        
        if not interno:
            self.posicoes_jogadas.append(exportar_posicao_fen(self.state))
            self._verificar_fim_de_jogo(cor_atual=self.state.turno)


    def promover_peao(self, novo_tipo: TipoPeca):
        """
        Substitui o peão e finaliza turno.

        Args:
            novo_tipo (TipoPeca): Novo tipo de peão.
        """
        l, c = self.casa_promocao
        peao = self.state.board.matriz[l, c]

        self.state.board.matriz[l, c] = criar_peca(tipo=novo_tipo, cor=peao.cor, pos=[l, c])
        self.casa_promocao = None
        self.aguardando_promocao = False

        self._finalizar_turno(captura=False, peao=True, interno=False)


    def _tem_movimentos_legais(self, cor: str) -> bool:
        """
        Verifica se o jogador da cor atual possui pelo menos um movimento legal.

        Args:
            cor (str): Cor do jogador.

        Returns:
            bool: True se o jogador possui pelo menos um movimento legal.
        """
        for li in range(8):
            for co in range(8):
                p = self.state.board.matriz[li, co]
                if p is not None and p.cor == cor:
                    pseudo = p.gerar_pseudo_movimentos(lc=(li, co))
                    candidatos = self._classificar_movimentos(p, (li, co), pseudo)
                    
                    if isinstance(p, Rei):
                        self._adicionar_roques(cor, candidatos)
                    if isinstance(p, Peao) and p.posicao in self.state.posicao_peao_en_passant:
                        self._adicionar_en_passant(candidatos)
                    
                    for destino, _ in candidatos:
                        if self._testar_movimento(destino, (li, co), cor):
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
                p = self.state.board.matriz[li, co]
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
        return self.state.vitoria_brancas or self.state.vitoria_negras or self.state.empate


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
                self.state.vitoria_negras = True
                cor_vencedora = "Pretas"
            else:
                self.state.vitoria_brancas = True
                cor_vencedora = "Brancas"

            print(f"Xeque-Mate! Vitória das {cor_vencedora}.")
        else:
            self.state.empate = True
            print("Empate por afogamento (Stalemate).")

        return True


    def _verificar_empate_50_lances(self) -> bool:
        """
        Verifica empate pela regra dos 50 lances.

        Returns:
            bool: True se houver empate.
        """
        if self.state.halfmove_clock >= 100:
            self.state.empate = True
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
            self.state.empate = True
            print("Empate por insuficiência de material.")
            return True

        return False


    def _verificar_empate_por_repeticao(self) -> bool:
        """
        Verifica empate por tripla repetição de posição.

        Returns:
            bool: True se houver empate.
        """
        posicoes = {}

        for fen in self.posicoes_jogadas:
            chave = " ".join(fen.split()[:4])

            if chave not in posicoes:
                posicoes[chave] = 0

            posicoes[chave] += 1

            if posicoes[chave] >= 3:
                self.state.empate = True
                print("Empate por tripla repetição.")
                return True

        return False


    def _verificar_fim_de_jogo(self, cor_atual: str) -> bool:
        """
        Agrega todas as checagens de fim de partida.

        Args:
            cor_atual (str): Cor do jogador atual.

        Returns:
            bool: True se o jogo terminou.
        """
        if self._verificar_xeque_mate_ou_afogamento(cor_atual):
            return False

        if self._verificar_empate_insuficiencia_material():
            return False

        if self._verificar_empate_50_lances():
            return False
        
        if self._verificar_empate_por_repeticao():
            return False
        return True


    def verificar_e_aplicar_roque(
        self,
        cor: Cor,
        distancia_c: int
    ) -> bool:
        """
        Verifica se o jogador pode realizar um roque.

        Args:
            cor (Cor): Cor do jogador.
            distancia_c (int): Diferença de colunas entre a torre e o rei.

        Returns:
            bool: True se o jogador pode realizar um roque, False caso contrário.
        """
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
        pos_original = self.state.board.achar_lc_rei(
            cor=cor_rei,
            matriz=self.state.board.matriz
        )
        self.executar_movimento(Movimento(
            origem=pos_original,
            destino=(l, c)),
            interno=True
        )
        atacada = self.verificar_xeque(cor_rei)
        self.desfazer_movimento(interno=True)
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

        direito = getattr(self.state, dados["direito"])

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
        if self.state.turno == Cor.BRANCO:
            self.state.turno = Cor.PRETO
        else:
            self.state.turno = Cor.BRANCO


    def gerar_mov_peca(self, p: Peca) -> None:
        """
        Gera os movimentos possíveis de uma peça.

        Args:
            p (Peca): Instância da peça a ser movimentada.
        """
        origem = self.state.board.achar_lc_peca(
            peca=p,
            matriz=self.state.board.matriz
        )
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
            self._adicionar_roques(self.state.turno, candidatos)
        
        if isinstance(p, Peao):
            if p.posicao in self.state.posicao_peao_en_passant:
                self._adicionar_en_passant(candidatos)
        
        movimentos_validos = []
        for destino, tipo in candidatos:
            if self._testar_movimento(destino, origem, self.state.turno):
                movimentos_validos.append((destino, tipo))
        
        self.movimentos_possiveis = movimentos_validos

        # if DEBUG:
        #     print(self.movimentos_possiveis)


    def _adicionar_en_passant(self, mov: list) -> None:
        """
        Adiciona as casas de en passant na lista de movimentos possíveis.

        Args:
            mov (list): Lista de movimentos.

        Returns:
            list: Lista de movimentos com os movimentos de en passant adicionados.
        """
        mov.append(self.state.en_passant)


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
        destino = self.state.board.matriz[destino_lc[0], destino_lc[1]]

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
                if destino is None and self.state.board.matriz[meio[0], meio[1]] is None:
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
            if self.state.board.matriz[atual[0], atual[1]] is not None:
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
        
        lc_rei = self.state.board.achar_lc_rei(
            cor=cor,
            matriz=self.state.board.matriz
        )
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
                if not self.state.board.lc_valido(linha=l, coluna=c):
                    break
                destino = self.state.board.matriz[l, c]
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
                if not self.state.board.lc_valido(linha=l, coluna=c): break
                destino = self.state.board.matriz[l, c]
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
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
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
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
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
            if self.state.board.lc_valido(linha=l, coluna=c):
                destino = self.state.board.matriz[l, c]
                if destino and isinstance(destino, Peao) and destino.cor != cor:
                    return True
        return False

from constantes import *
from pecas.peca import Peca, Cor
from pecas.peao import Peao
from pecas.rei import Rei
from pecas.torre import Torre
from .move import *
from .judge import Judge
from .fen_parser import *
from .state import GameState
from .factory import criar_peca


class Controller:
    """
    Gerenciador de lógica e estado do jogo de xadrez.

    Controla o tabuleiro, valida movimentos, gera movimentos possíveis, gerencia
    turnos e verifica condições de xeque. Totalmente desacoplada da camada visual.
    """

    def __init__(self) -> None:
        """
        Inicializa o controller com o tabuleiro vazio e carrega a posição inicial.
        """
        self.state: GameState   = GameState()
        self.judge: Judge       = Judge(self.state)

        self.movimentos_possiveis: JogadasPossiveis = []

        carregar_posicao_fen(
            state=self.state,
            fen=FEN_INICIAL,
            board=self.state.board
        )

        self.casa_promocao: Pos | None = None
        self.aguardando_promocao: bool = False
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


    def executar_movimento(
        self,
        mov: Movimento,
        interno: bool = False,
        promocao_alvo: TipoPeca | None = None
    ) -> bool:
        """
        Executa um movimento.

        Args:
            mov (Movimento):
                Objeto contendo as coordenadas de origem e destino.
            interno (bool):
                True se o movimento foi executado internamente, False caso contrário.
            promocao_alvo (TipoPeca | None):
                Tipo da peça para promoção automática em testes.

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
            foi_promocao=foi_promocao,
            vitoria_brancas=self.state.vitoria_brancas,
            vitoria_negras=self.state.vitoria_negras,
            empate=self.state.empate
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

                self.state.en_passant = ((linha + direcao, coluna), TipoMov.CAPTURA)
                self.state.posicao_alvo_en_passant = mov.destino
                for dc in (-1, 1):
                    c_viz = coluna + dc
                    if lc_valido(linha, c_viz):
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

        if not interno and self.state.posicoes_jogadas:
            self.state.posicoes_jogadas.pop()

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
        self.state.vitoria_brancas = estado.vitoria_brancas
        self.state.vitoria_negras = estado.vitoria_negras
        self.state.empate = estado.empate

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
        mov_destino: Pos,
        origem: Pos,
        cor: Cor
    ) -> bool:
        """
        Verifica se um movimento dado eh valido.

        Args:
            mov_destino (Pos): Coordenadas de destino.
            origem (Pos): Coordenadas de origem.
            cor (Cor): Cor do jogador.

        Returns:
            bool: True se o movimento for valido, False caso contrário.
        """
        self.executar_movimento(Movimento(origem=origem, destino=mov_destino), interno=True)
        em_xeque = self.judge.verificar_xeque(cor=cor)
        self.desfazer_movimento(interno=True)

        return not em_xeque


    def _tem_movimentos_legais(self, cor: Cor) -> bool:
        """
        Verifica se o jogador da cor atual possui pelo menos um movimento legal.

        Args:
            cor (Cor): Cor do jogador.

        Returns:
            bool: True se o jogador possui pelo menos um movimento legal.
        """
        for l in range(8):
            for c in range(8):
                p = self.state.board.matriz[l, c]
                if p is not None and p.cor == cor:
                    candidatos = self.judge.buscar_candidatos(p, (l, c))
                    
                    for destino, _ in candidatos:
                        if self._testar_movimento(destino, (l, c), cor):
                            return True
        return False


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
        if cor == Cor.BRANCO:
            l = 7
        else:
            l = 0

        if distancia_c > 0: # Curto
            torre = self.state.board.matriz[l, 7]
            self.state.board.matriz[l, 5] = torre
            self.state.board.matriz[l, 7] = None
            if torre:
                torre.posicao = (l, 5)
        else: # Longo
            torre = self.state.board.matriz[l, 0]
            self.state.board.matriz[l, 3] = torre
            self.state.board.matriz[l, 0] = None
            if torre:
                torre.posicao = (l, 3)


    def _finalizar_turno(
        self,
        captura: bool,
        peao: bool,
        interno: bool
    ) -> None:
        """
        Método auxiliar para concluir a lógica de fim de turno.

        Args:
            captura (bool): True se houver captura, False caso contrário.
            peao (bool): True se houver peão, False caso contrário.
            interno (bool): True se o movimento foi executado pelo controller.
        """
        if peao or captura:
            self.state.halfmove_clock = 0
        else:
            self.state.halfmove_clock += 1

        self.mudar_turno()
        if self.state.turno == Cor.BRANCO:
            self.state.fullmove_number += 1
        
        if not interno:
            self.state.posicoes_jogadas.append(exportar_posicao_fen(self.state))
            self.judge.verificar_fim_de_jogo(
                cor_atual=self.state.turno,
                tem_mov_legais=self._tem_movimentos_legais(self.state.turno)
            )


    def promover_peao(self, novo_tipo: TipoPeca):
        """
        Substitui o peão e finaliza turno.

        Args:
            novo_tipo (TipoPeca): Novo tipo de peão.
        """
        l, c = self.casa_promocao
        peao = self.state.board.matriz[l, c]

        self.state.board.matriz[l, c] = criar_peca(
            tipo=novo_tipo,
            cor=peao.cor,
            pos=[l, c]
        )
        self.casa_promocao = None
        self.aguardando_promocao = False

        self._finalizar_turno(captura=False, peao=True, interno=False)


    @property
    def finalizado(self) -> bool:
        """
        Retorna True se o jogo acabou (Vitória ou Empate).
        """
        return any((
            self.state.vitoria_brancas,
            self.state.vitoria_negras,
            self.state.empate
        ))


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

        if self.judge.verificar_roque(
            cor,
            lado,
            self.judge.verificar_xeque(cor)
        ):
            self.executar_roque(cor, lado)
            return True

        return False


    def executar_roque(self, cor: Cor, lado: str) -> None:
        """
        Executa um roque.

        Args:
            cor (str): Cor do rei.
            lado (str): "curto" ou "longo".
        """
        dados = self.judge.ROQUES[(cor, lado)]

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
        Alterna o turno atual entre Cor.BRANCO ('w') e Cor.PRETO ('b').
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
        origem = p.posicao

        candidatos = self.judge.buscar_candidatos(p, origem)
        
        movimentos_validos = []
        for destino, tipo in candidatos:
            if self._testar_movimento(destino, origem, self.state.turno):
                # Adiciona apenas se o movimento não deixar o proprio rei em xeque
                movimentos_validos.append((destino, tipo))
        
        self.movimentos_possiveis = movimentos_validos


    def limpar_movimentos(self) -> None:
        """
        Limpa os movimentos movimentos possíveis.
        """
        self.movimentos_possiveis.clear()


    def obter_todos_lances_legais_do_turno(self) -> list[Movimento]:
            """
            Varre o tabuleiro usando a mesma lógica de validação do jogo humano
            e coleta todos os Movimentos válidos para o turno atual.
            """
            lances_legais = []
            turno_atual = self.state.turno
            matriz = self.state.board.matriz

            for l in range(8):
                for c in range(8):
                    peca = matriz[l, c]
                    if peca and peca.cor == turno_atual:
                        self.gerar_mov_peca(peca)
                        
                        for destino, _ in self.movimentos_possiveis:
                            lances_legais.append(Movimento(origem=(l, c), destino=destino))
                            
            self.limpar_movimentos()
            return lances_legais

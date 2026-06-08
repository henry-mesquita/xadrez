from xadrez import Xadrez

def main() -> None:
    """
    Ponto de entrada do programa. Instancia e inicia o jogo.
    """
    jogo = Xadrez()
    jogo.run()

    print(jogo.engine.judge._contagem_material())


if __name__ == '__main__':
    main()

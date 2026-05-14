from xadrez import Xadrez

def main() -> None:
    """
    Ponto de entrada do programa. Instancia e inicia o jogo.
    """
    jogo = Xadrez()
    jogo.run(debug=True)


if __name__ == '__main__':
    main()

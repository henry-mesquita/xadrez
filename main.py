from xadrez import Xadrez

def main() -> None:
    """
    Inicia o jogo de xadrez.
    """
    jogo = Xadrez()
    jogo.run(mostrar_fps=False)

if __name__ == '__main__':
    main()

from pathlib import Path
import cairosvg


BASE_DIR = Path(__file__).parent

PASTA_SVG = BASE_DIR / "img" / "svg"
PASTA_PNG = BASE_DIR / "img" / "png"

PASTA_PNG.mkdir(exist_ok=True)


for pasta_estilo in PASTA_SVG.iterdir():

    if not pasta_estilo.is_dir():
        continue

    pasta_saida = PASTA_PNG / pasta_estilo.name
    pasta_saida.mkdir(exist_ok=True)

    for arquivo_svg in pasta_estilo.glob("*.svg"):

        try:
            if arquivo_svg.stat().st_size == 0:
                print(f"ARQUIVO VAZIO: {arquivo_svg}")
                continue

            arquivo_png = pasta_saida / f"{arquivo_svg.stem}.png"

            cairosvg.svg2png(
                url=str(arquivo_svg),
                write_to=str(arquivo_png),
                output_width=128,
                output_height=128
            )

            print(f"Convertido: {arquivo_png}")

        except Exception as e:
            print(f"ERRO EM: {arquivo_svg}")
            print(e)
            print("-" * 50)

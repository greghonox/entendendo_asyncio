from asyncio import Queue, Semaphore, create_task, gather, run, sleep
from os import remove, system, walk
from os.path import basename, exists
from re import findall

CAMINHO_PDFS = "/tmp/entrada"


class ExtrairPdfTxt:
    def __init__(self, arq_entrada):
        self.arq_entrada = arq_entrada
        self.arq_saida = arq_entrada.replace(".pdf", ".txt")
        self.txt = False
        print(
            f"CONVERTENDO ARQUIVO {basename(self.arq_entrada)} -> {basename(self.arq_saida)}"
        )

        if self.conveter_pdf_txt():
            self.ler_txt()

    def conveter_pdf_txt(self):
        if exists(self.arq_entrada):
            system(f"pdftotext {self.arq_entrada} -layout {self.arq_saida}")
            return True
        print(f"ARQUIVO {self.arq_entrada} NÃO EXISTE!")
        return False

    def ler_txt(self):
        if exists(self.arq_saida):
            with open(self.arq_saida, "r", encoding="utf-8") as f:
                self.txt = f.read()
                return True
        print(f"ARQUIVO DE SAIDA {self.arq_saida} NÃO EXISTE!")
        return False

    def __del__(self):
        try:
            if exists(self.arq_saida):
                remove(self.arq_saida)
                print(f"REMOVENDO {self.arq_saida}")
        except Exception as e:
            print(f"ARQUIOVO {self.arq_saida} NÃO FOI ENCONTRADO PARA SER REMOVIDO")


class Parse:
    def __init__(self, pdf):
        f = lambda x: findall(x, pdf["conteudo"], 2)
        s = lambda x, y: x.split("\n")[y] if len(x) > 0 else ""
        l = lambda x, y, z: x[-1].split(z)[y] if len(x) > 0 else ""

        moeda = "\n\[d*\.]*\d*,\d{2}"
        moedas = ["usd", "eur", "sek", "nok", "dkk", "gbp"]
        self.tipos_parse = (
            {
                "fornecedor": "VALVECO",
                "invoice": l(f("invoice\s\d+"), 1, " "),
                "moeda": l(f("EUR\sSubtotal.*"), 0, "\n"),
                "invoice date": f("\d{2}-\d{2}-\d{4}")[0],
                "subtotal": l(f("EUR\sSubtotal.*"), 1, " "),
            }
            if "VALVECO" in pdf["arquivo"]
            else {
                "fornecedor": "BERGLASER",
                "invoice": l(f("INVOICE\sNo\:.*?\n"), 2, " "),
                "moeda": l(f("Total\sfor\sME\sAIR\sCOOLER\:\s\w{3}\s\d*.\d*"), 4, " ")[
                    -3:
                ],
                "invoice date": f("Date\:\s\w{3}\.\s\d\d,\s\d{4}"),
                "subtotal": l(
                    f("Total\sfor\sME\sAIR\sCOOLER\:\s\w{3}\s\d*.\d*"), -1, " "
                ),
            }
            if "BERGLASER" in pdf["arquivo"]
            else {
                "fornecedor": "DANMARINEGROUP",
                "invoice": l(f("\n\w{3}\d*.\ninvoice"), 1, "\n"),
                "moeda": s(f("usd\n\d.\d*.\d*.\d*")[-1], 0),
                "invoice date": f("\d{4}-\d{2}-\d{2}")[0],
                "subtotal": s(f("usd\n\d.\d*.\d*.\d*")[-1], 1),
            }
            if "DANMARINEGROUP" in pdf["arquivo"]
            else {
                "fornecedor": "WESTRONIC",
                "invoice": s(f("AS\nDate\n.*")[0], 2),
                "moeda": l(f("\ntotal\s\w{3}"), 1, " "),
                "invoice date": f("\d{2}-\d{2}-\d{4}")[0],
                "subtotal": s(f("total\n\d*\,\d*")[0], 1),
            }
            if "WESTRONIC" in pdf["arquivo"]
            else {
                "fornecedor": "FAKTURA",
                "invoice": l(f("FAKTURA\s.*"), 1, " "),
                "moeda": s(f("\nKID|".join(moedas))[0], 0),
                "invoice date": f("\d{2,}\.\d{,2}\.\d{4}")[0],
                "subtotal": f("Nettobeløp\s.*"),
            }
            if "FAKTURA" in pdf["arquivo"]
            else {"fornecedor": "INDEFINIDO"}
        )

        print(f"TIPO DE DOCUMENTO {self.tipos_parse['fornecedor']}")

        if self.tipos_parse["fornecedor"] != "INDEFINIDO":
            print(f"INICIANDO O PARSE DO {self.tipos_parse}")


class ConverterPdf:
    def __init__(self):
        self.pdf_txt = []
        run(self.main())
        run(self.gravar_saida())

    async def main(self):
        pdfs = self.pegar_arqs_entrada()
        self.tasks = []
        for pdf in pdfs:
            self.tasks.append(create_task(self.converter(pdf)))
        await gather(*self.tasks)

    def pegar_arqs_entrada(self):
        return [x + "/" + i for x, y, z in walk(CAMINHO_PDFS) for i in z]

    async def converter(self, pdf_entrada):
        self.pdf_txt.append(
            {"conteudo": ExtrairPdfTxt(pdf_entrada).txt, "arquivo": pdf_entrada}
        )

    async def gravar_saida(self):
        for e, pdf in enumerate(self.pdf_txt):
            txt = Parse(pdf)
            with open("/tmp/saida.txt", "a", encoding="utf-8", errors="ignore") as f:
                f.write(f"{1+e:>^200}\n")
                f.write(str(txt.tipos_parse))


ConverterPdf()

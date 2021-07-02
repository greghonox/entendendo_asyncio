from asyncio import create_task, gather, get_event_loop, run, sleep
from random import randint, choice
from datetime import datetime
from requests import get
from time import time


async def gravar_arquivo_txt(msg: str, tarefa: str, e: bool = True):
    t = randint(1, 10) if e else 0
    await sleep(t)
    print(f"INICIANDO TAREFA {tarefa} E ESPERANDO {t}")
    with open("/tmp/arq.txt", "a") as f:
        f.write(
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            + f" {tarefa:0>3}:{t:0>3} -- "
            + msg
            + "\n"
        )


async def txt(tam_len, qtde_tarefas=5):
    for t in range(qtde_tarefas):
        exec(
            "t_{} = create_task(gravar_arquivo_txt(''.join([chr(randint(65, 90)) for _ in range({})]), {}))".format(
                t, tam_len, t
            )
        )
    for t in range(qtde_tarefas):
        await eval(f"t_{t}")


async def limpar(tarefa: str):
    print(f"FAZENDO LIMPEZA {tarefa}\n")
    await sleep(0.1)


async def worker(tarefa: str):
    tempo = randint(1, 5)
    await sleep(tempo)
    print(f"TAREFA: {tarefa}, TEMPO PARA CONCLUIR: {tempo}")
    await limpar(tarefa)


async def t_coperative():
    print("TAREFAS COPERATIVAS, PERCEBA QUE A PRIMEIRA SEMPRE RODA PRIMEIRO!")
    print("-" * 100)
    t1 = create_task(worker(1))
    t2 = create_task(worker(2))

    await t1
    await t2


async def ex_serie(coroutine_tasks):
    print("RODANDO MODO SERIE")
    for task in coroutine_tasks:
        await task


async def ex_paralelo(coroutine_tasks):
    print("RODANDO MODO PARALELO")
    workers = []
    for task in coroutine_tasks:
        workers.append(create_task(task))

    await gather(*workers)


class CoorepadoraNET:
    def __init__(self, qtde_tasks: int):
        run(self.run(qtde_tasks))

    async def run(self, qtde_tasks: int):
        for t in range(qtde_tasks):
            exec("t_{} = create_task(self.pegar_dados({}))".format(t, t))
        for t in range(qtde_tasks):
            await eval(f"t_{t}")

    async def pegar_dados(self, task):
        print(await self.get(task))

    async def get(self, task):
        URL = "https://www.planoalgartelecom.com.br"
        print(f"PEGANDO DADOS {URL} TAREFA:{task}")
        try:
            return get(URL)
        except Exception as e:
            print(f"ERRO OCORRIDO NA TAREFA {task}: {e}")


TOTAL = 5
tarefas = [
    "CORRER",
    "ORAR",
    "TRABALHAR",
    "MORDER",
    "LUTAR",
    "TRABALHAR",
    "COISAR",
    "VOAR",
    "REALIZAR",
]

f = lambda x: worker(choice(tarefas) + f" {x}")

t_ini = time()


def main():
    print("-" * 500)
    if TIPO_RODAR == "run_cooperative":
        run(t_coperative())

    elif TIPO_RODAR == "run_cooperative_net":
        CoorepadoraNET(5)

    elif TIPO_RODAR == "run_cooperative_txt":
        run(txt(5000, 500))
        run(gravar_arquivo_txt(f"TEMPO CORRIDO: {time() - t_ini} ", "FIM", False))

        t_in = time()
        for t in range(5000):
            run(txt(5000, t))
        run(gravar_arquivo_txt(f"TEMPO CORRIDO SERIE: {time() - t_in} ", "FIM", False))

    elif TIPO_RODAR == "run_serie":
        run(ex_serie([f(x) for x in range(TOTAL)]))
        run(ex_paralelo([f(x) for x in range(TOTAL)]))

    elif TIPO_RODAR == "run_paralelo":
        loop = get_event_loop()
        loop.run_until_complete(ex_serie([f(x) for x in range(TOTAL)]))
        loop.close()

    elif TIPO_RODAR == "loop_paralelo":
        loop = get_event_loop()
        loop.run_until_complete(ex_paralelo([f(x) for x in range(TOTAL)]))
        loop.close()


TIPO_RODAR = "run_cooperative_net"
main()

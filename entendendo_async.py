from asyncio import Queue, Semaphore, create_task, gather, run, sleep
from datetime import datetime
from itertools import repeat
from random import choice, randint
from time import time

from requests import get

# https://realpython.com/async-io-python/


async def gravar_arquivo_txt(msg: str, tarefa: str, e: bool = True):
    t = randint(1, 10) if e else 0
    await sleep(t)
    print(f"INICIANDO TAREFA {tarefa} E ESPERANDO {t}")
    with open("/tmp/arq.txt", "a") as f:
        f.write(
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            + f" {tarefa:0>9}:{t:0>9} -- "
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


async def semaforo(sem, t):
    await sem.acquire()
    m = randint(5, 10)
    print(f"INICIANDO TAREFA: {t}, TEMPO PARA CONCLUIR: {m}")
    print(f"ESPERANDO TAREFA: {t}")
    await sleep(m)
    sem.release()
    print(f"TERMINANDO TAREFA: {t}")


async def run_semaforo_paralelo(qtde_task: int):
    qtde_paradas = randint(1, 5)
    print(f"INICIANDO SEMAFORO C/ {qtde_paradas} PARADAS PARALELO")
    semaphore = Semaphore(value=qtde_paradas)
    await gather(*[create_task(semaforo(semaphore, x)) for x in range(qtde_task)])


async def run_semaforo(qtde_tasks: int):
    qtde_paradas = randint(1, 5)
    print(f"INICIANDO SEMAFORO C/ {qtde_paradas} PARADAS")
    semaphore = Semaphore(value=qtde_paradas)
    for t in range(qtde_tasks):
        exec("t_{} = create_task(semaforo(semaphore, {}))".format(t, t))

    for t in range(qtde_tasks):
        await eval(f"t_{t}")
    print("FINALIZANDO SEMAFORO")


class Fabric:
    def __init__(self, tasks: dict, tam_con: int = 5, paralelo: bool = True):
        self.paralelo = paralelo
        self.tam_con = tam_con
        self.fila = Queue()
        self.tasks = tasks
        run(self.main())

    async def main(self):
        tasks_p = [
            create_task(self.produtor(x, e)) for e, x in enumerate(self.tasks.items())
        ]

        await self.fila.join()
        await gather(*tasks_p)

        print(
            f"TOTAL DE TAREFAS PARA CONSUMIR {self.fila.qsize()} PARA {self.tam_con} CONSUMIDORES"
        )
        tasks_c = [
            create_task(self.consumidor(f"CONSUMIDOR {x}")) for x in range(self.tam_con)
        ]
        await gather(*tasks_c, return_exceptions=True)

    async def worker(self, t: str):
        tempo = randint(1, 5)
        print(f"EXECUTANDO TAREFA '{t}' TEMPO {tempo}")
        await sleep(tempo)
        return f"FINALIZANDO TAREFA '{t}' TEMPO {tempo}"

    async def produtor(self, e: dict, t: str):
        n = randint(1, 5)
        print(f"PRODUTOR({t}) FILA DE '{e}' TAREFAS PARA FAZER")
        for _ in repeat(None, n):
            res = await self.worker(e)
            await self.fila.put(res)

    async def consumidor(self, con: str):
        tempo = randint(1, 5)
        while True:
            await sleep(tempo)
            res = await self.fila.get()
            print(f"({con}) '{res}' TAREFAS DA FILA TEMPO PARA CONSUMIR {tempo}")
            self.fila.task_done()


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


TOTAL = 5000
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
        SOLICITACOES = 100000
        run(txt(1000, SOLICITACOES))
        run(gravar_arquivo_txt(f"TEMPO CORRIDO: {time() - t_ini} ", "FIM", False))
        print("INICIANDO MODO SERIE")
        t_in = time()
        for t in range(SOLICITACOES):
            run(txt(5000, t))
        run(gravar_arquivo_txt(f"TEMPO CORRIDO SERIE: {time() - t_in} ", "FIM", False))

    elif TIPO_RODAR == "run_serie":
        run(ex_serie([f(x) for x in range(TOTAL)]))
        run(ex_paralelo([f(x) for x in range(TOTAL)]))

    elif TIPO_RODAR == "run_paralelo":
        # CHAMA EM PARALELO AS ATIVIDADES, C/ SINCRONIA
        run(ex_serie([f(x) for x in range(TOTAL)]))

    elif TIPO_RODAR == "loop_paralelo":
        # CHAMA EM PARALELO AS ATIVIDADES, C/ SINCRONIA
        run(ex_paralelo([f(x) for x in range(TOTAL)]))

    elif TIPO_RODAR == "run_semaphore":
        # ELE INICIA PELA QUANTIDADE DE PARADAS E DEPOIS QUE ELAS TERMINAREM ELE CHAMA AS PROXIMAS
        run(run_semaforo(10))

    elif TIPO_RODAR == "run_semaphore_paralelo":
        # FICA MUITO BAGUNÇADO, POIS ELES TRABALHANDO EM PARALELO
        run(run_semaforo_paralelo(10))

    elif TIPO_RODAR == "run_fila":
        Fabric({x: choice(tarefas) for x in range(TOTAL)}, 10000)


TIPO_RODAR = "run_cooperative_net"
main()

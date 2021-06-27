from asyncio import create_task, gather, get_event_loop, ensure_future, run, sleep
from random import randint, choice


async def limpar(tarefa):
    print(f"FAZENDO LIMPEZA {tarefa}\n")
    await sleep(0.1)


async def worker(tarefa):
    tempo = randint(1, 5)
    await sleep(tempo)
    print(f"Iteracao {tarefa}, tempo decorrido: {tempo}")
    await limpar(tarefa)


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


def ex_eterno(loop):
    print("Jesus")
    loop.call_later(1, ex_eterno, loop)


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


def main():
    print("-" * 100)
    if TIPO_RODAR == "run_serie":
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

    elif TIPO_RODAR == "loop_infinito":
        loop = get_event_loop()
        loop.call_soon(ex_eterno, loop)
        loop.run_forever()


TIPO_RODAR = "loop_infinito"
main()

from asyncio import create_task, gather, get_event_loop, ensure_future, run, sleep
from random import randint, choice


async def limpar(tarefa):
    print(f"FAZENDO LIMPEZA {tarefa}")
    await sleep(2)


async def worker(tarefa):
    tempo = randint(1, 5)
    await sleep(tempo)
    print(f"Iteracao {tarefa}, tempo decorrido: {tempo}")


async def ex_serie(coroutine_tasks):
    print("RODANDO MODO SERIE")
    for task in coroutine_tasks:
        await task


async def ex_paralelo(coroutine_tasks):
    print("RODANDO MODO PARALELO")
    workers = []
    for task in coroutine_tasks:
        workers.append(ensure_future(task))

    await gather(*workers)


TOTAL = 10
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

run(ex_serie([f(x) for x in range(TOTAL)]))
print("-" * 100)
run(ex_paralelo([f(x) for x in range(TOTAL)]))

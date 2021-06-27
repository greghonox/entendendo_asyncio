import asyncio


def print_and_repeat(n, loop):
    print(f"Hello World {n}")
    loop.call_later(2, print_and_repeat, 1, loop)


loop = asyncio.get_event_loop()
loop.call_soon(print_and_repeat, 1, loop)
loop.run_forever()

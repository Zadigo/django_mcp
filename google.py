import asyncio
import time


async def some_corouting(delay, text):
    for i in range(3):
        await asyncio.sleep(delay)
        print(f'Task with delay {delay}: {text} ({i})')


async def main():
    t1 = asyncio.create_task(some_corouting(3, 'hello'))
    t2 = asyncio.create_task(some_corouting(1, 'world'))

    await t1
    await t2


if __name__ == '__main__':
    asyncio.run(main())

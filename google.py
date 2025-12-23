import asyncio


async def long_task():
    await asyncio.sleep(3)
    return 'Long Task Complete'


async def another_long_task():
    await asyncio.sleep(1)
    return 'Another Long Task Complete'


async def main():
    t1 = asyncio.create_task(long_task())
    t2 = asyncio.create_task(another_long_task())

    async for completed_task in asyncio.as_completed([t1, t2]):
        print(completed_task.result())


if __name__ == '__main__':
    asyncio.run(main())

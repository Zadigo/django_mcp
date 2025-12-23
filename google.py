import asyncio


async def test1():
    print('Test1 started')
    await asyncio.sleep(3)
    print("Test1 completed")


async def test2():
    print('Test2 started')
    await asyncio.sleep(1)
    print("Test2 completed")


async def google():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(test1())
        task2 = tg.create_task(test2())
        print('All tasks completed')


if __name__ == "__main__":
    asyncio.run(google())

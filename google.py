import asyncio


async def long_task():
    await asyncio.sleep(10)
    return 'Task Complete'


async def main():
    try:
        await asyncio.wait_for(long_task(), timeout=5)
    except asyncio.TimeoutError:
        print('The task timed out!')

if __name__ == '__main__':
    asyncio.run(main())

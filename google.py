import asyncio


async def waiting_to_print():
    return 'Waited and printed!'


async def main():
    print('Starting wait...')
    value = await asyncio.sleep(3, result=await waiting_to_print())
    print('Finished waiting:', value)


if __name__ == '__main__':
    asyncio.run(main())

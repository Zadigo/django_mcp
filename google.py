import asyncio


class Database:
    def __init__(self, name):
        self.name = name
        print(f'Instanciated database {self.name}...')

    async def __call__(self, seconds):
        await asyncio.sleep(seconds)
        print(f'  - Database {self.name} initialized in {seconds} seconds.')


async def database_one():
    instance = Database('DB1')
    return await instance(5)


async def database_two():
    instance = Database('DB2')
    return await instance(2)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(database_one())
        tg.create_task(database_two())
        print('** Initializing databases...\n')
    print('Databases initialized.')


if __name__ == '__main__':
    asyncio.run(main())

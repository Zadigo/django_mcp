import asyncio
import time


class Database:
    def __init__(self, name, seconds):
        self.name = name
        print(f'  - Initializing database {self.name}, will take {seconds} seconds...')
        time.sleep(seconds)
        print(f'  - Database {self.name} initialized.\n')


async def database_one():
    print('\nStarting database one initialization...')
    return Database('DB1', 10)


async def database_two():
    print('\nStarting database two initialization...')
    return Database('DB2', 1)


async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(database_one())
        t2 = tg.create_task(database_two())
        print('Waiting for databases to initialize...\n')
    print('Databases initialized.')


if __name__ == '__main__':
    asyncio.run(main())

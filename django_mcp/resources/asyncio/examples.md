## Examples

### Cleaning HTML Content from Database Entries

The following example demonstrates how to clean HTML content stored in a SQLite database using BeautifulSoup. The script fetches entries from the database, removes HTML tags, and updates the cleaned text back into the database.

```python
import asyncio
import pathlib
import sqlite3
from bs4 import BeautifulSoup
import httpx
from numpy import maximum

IDS: asyncio.Queue[int] = asyncio.Queue()


async def request_url(tg: asyncio.TaskGroup, url: str):
    async with httpx.AsyncClient() as client:
        await asyncio.sleep(3)

        try:
            response = await client.get(url)
            response.raise_for_status()
        except Exception as e:
            print(f"\t- Error fetching {url}: {e}")
            return None

        # Save content to database concurrently with other tasks
        # using the provided TaskGroup
        save_task = tg.create_task(save_to_db(url, response.text))
        rowid = await save_task

        return rowid


async def database():
    conn = None

    path = pathlib.Path('.').absolute() / 'db.sqlite3'
    with sqlite3.connect(path, check_same_thread=False, timeout=10) as conn:
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn


async def create_table():
    conn = await database()

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                content TEXT NOT NULL
            );
        ''')
        conn.commit()
        print("\n\t- Table 'scrapping' created successfully.")


async def save_to_db(url: str, content: str) -> int:
    conn = await database()

    if conn is not None:
        cursor = conn.cursor()
        data = cursor.execute('''
            INSERT INTO scrapping (url, content)
            VALUES (?, ?);
        ''', (url, content))

        try:
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving to database: {e}")
        finally:
            rowid = data.lastrowid
            print(f"\t- Content from {url} saved to database. ID: {rowid}.")
            return rowid


async def clean_text():
    maximum_retries = 3
    retries = 0

    while True:
        # Process all IDs in the queue as long
        # as there are any urls to clean
        while not IDS.empty():
            rowid = await IDS.get()
            conn = await database()

            if conn is not None:
                cursor = conn.cursor()
                text = cursor.execute('''
                    SELECT content FROM scrapping WHERE id = ?;
                ''', (rowid,)).fetchone()

                if text:
                    soup = BeautifulSoup(text[0], 'html.parser')
                    cleaned_text = soup.text.strip()
                    cursor.execute('''
                        UPDATE scrapping SET content = ? WHERE id = ?;
                    ''', (cleaned_text, rowid))
                    conn.commit()
                    print(f"\t- Cleaned content for ID: {rowid}.")

            await asyncio.sleep(15)

        # Stop the long loop if no IDs to 
        # clean after several retries
        if IDS.empty():
            retries += 1
            if retries > maximum_retries:
                print(
                    "\t- No IDs to clean after multiple retries. Exiting cleaning task.")
                break

            print("\t- No IDs to clean. Waiting...")
        else:
            if retries > 0:
                retries = 0

        await asyncio.sleep(2)


async def main():
    try:
        print('🚀 Connecting to the database...')
        task = asyncio.create_task(create_table())
        # Wait for table creation with timeout
        done, pending = await asyncio.wait([task], timeout=10)
    except asyncio.CancelledError:
        raise Exception("Table creation timed out")
    else:
        urls = [
            'https://example.com',
            'https://example.fr',
            'https://example.org'
        ]

        async with asyncio.TaskGroup() as tg:
            # Start the cleaning task
            cleaning_task = tg.create_task(clean_text())

            for url in urls:
                # Fetch and save URL content concurrently
                url_task = tg.create_task(request_url(tg, url))
                rowid = await url_task
                await IDS.put(rowid)

        # Cancel the cleaning task if still running
        cleaning_task.cancel()
        print("\nAll tasks completed.")


if __name__ == '__main__':
    asyncio.run(main())
```

import asyncio
import json
import logging
from typing import Any, Union

import httpx
from mcp.server.fastmcp import FastMCP

from django_mcp import BASE_DIR
from django_mcp.utils import create_redis_connection, list_resources

mcp = FastMCP('Django MCP', dependencies=['httpx'])


REDIS_KEY = 'django_mcp:documentation'


async def cache_content(key: str, content: Union[str, dict]):
    """Cache content to Redis under a specific key.
    Args:
        content: The content to cache (string or dictionary).
        key: The Redis key under which to store the content.
    """
    conn = await create_redis_connection()

    if conn is not None:
        try:
            if isinstance(content, dict):
                content = json.dumps(content)

            await conn.hset(REDIS_KEY, key, content)
        except Exception as e:
            logging.error(f"Error caching content to Redis: {e}")


@mcp.resource('documentation://resources')
async def get_documentation_resources() -> str:
    """Get a list of available documentation resources.

    Returns:
        A formatted string listing all available documentation resources.
    """
    resources = await list_resources('resources', names_only=True)
    return f'''# Avaiable Documentation Resources:\n {'\n- '.join(resources)}'''


@mcp.resource('documentation://{topic}')
async def get_documentation_content(topic: str) -> str:
    """Get the content of a specific documentation topic.

    Args:
        topic: The topic name to retrieve documentation for.

    Returns:
        The content of the documentation topic as a string.
    """
    conn = await create_redis_connection()

    hash_key = 'topic_library'
    if conn is not None:
        try:
            library = await conn.hget(REDIS_KEY, hash_key)
        except Exception as e:
            logging.error(f"Error fetching from Redis: {e}")
            return "Error fetching documentation."
        else:
            if library is not None:
                try:
                    # This is the JSON file that references all documentation elements
                    # in order to make them easily accessible
                    library = BASE_DIR / 'resources' / 'library.json'
                    with open(library, 'r') as f:
                        data = json.load(f)
                        await cache_content(hash_key, data)
                except Exception as e:
                    logging.error(f"Error loading library JSON: {e}")
                    return "Error fetching library files."

                library = json.loads(library)
                filtered_topics = [
                    item for item in library
                    if item['topic'] == topic
                ]

                async with asyncio.TaskGroup() as tg:
                    t1 = tg.create_task(
                        cache_content(
                            'library_files', 
                            library
                        )
                    )

                    content = f"""# Documentation on {topic} \n\n"""
                    content += f"""## Available Files: {len(filtered_topics)}"""
                    return content


async def main() -> None:
    mcp.run_stdio_async()


if __name__ == '__main__':
    asyncio.run(main())

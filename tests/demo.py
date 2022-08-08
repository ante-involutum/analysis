import asyncio

from src.utils.helper import KFConsumer

# sync consumer
# c = KFConsumer('test-1')
# while True:
#     c.subscribe(pattern='^demo-*')
#     c.close()
#     time.sleep(1)


# async consumer
async def con(no):
    c = KFConsumer(f'test-{no}')
    while True:
        c.subscribe(pattern='^demo-*')
        await asyncio.sleep(1)
    # c.close()
    # return result


async def main():
    L = await asyncio.gather(
        con("A"),
        con("B"),
    )

asyncio.run(main())

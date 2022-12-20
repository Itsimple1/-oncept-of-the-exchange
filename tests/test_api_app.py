import asyncio


async def output1():
    print(1)
    await asyncio.sleep(3)
    print("finish")


async def output2():
    print(2)
    await asyncio.sleep(3)
    print("finish")


async def main():
    task1 = asyncio.create_task(output1())
    task2 = asyncio.create_task(output2())

    await task1
    await task2



if __name__ == "__main__":
    asyncio.run(main())

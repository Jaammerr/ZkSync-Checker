import asyncio
import os.path

from loguru import logger
from main import ZKChecker


semaphore = asyncio.Semaphore(5)  # threads


async def run_safe(address: str) -> tuple[bool, str]:
    async with semaphore:
        checker = ZKChecker(address)
        checker.setup_session()
        amount = await checker.check()
        return amount, address


async def run():
    if not os.path.exists("wallets.txt"):
        logger.error(f"File wallets.txt not found")
        exit(1)

    with open("wallets.txt", "r") as file:
        addresses = [line.strip() for line in file.readlines()]

    if not addresses:
        logger.error(f"No addresses found in wallets.txt")
        exit(1)

    tasks = [asyncio.create_task(run_safe(address)) for address in addresses]
    results = await asyncio.gather(*tasks)

    logger.success(f"Checked {len(addresses)} addresses")
    with open("results.txt", "w") as file:
        for amount, address in results:
            if amount:
                file.write(f"{address} - {amount} ZK\n")
            else:
                file.write(f"{address} - Not eligible\n")



if __name__ == "__main__":
    asyncio.run(run())


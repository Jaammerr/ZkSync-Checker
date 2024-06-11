import httpx
from loguru import logger


class ZKChecker(httpx.AsyncClient):
    URL = "https://api.zknation.io/eligibility"

    def __init__(self, address: str):
        super().__init__()
        self.timeout = 10
        self.address = address

    def setup_session(self):
        self.timeout = 10
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://claim.zknation.io',
            'referer': 'https://claim.zknation.io/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'x-api-key': '46001d8f026d4a5bb85b33530120cd38',
        }

    async def check(self) -> bool | int:
        async with self as client:
            try:
                response = await client.get(self.URL, params={
                    'id': self.address,
                })
                response.raise_for_status()
                data = response.json()

                if not data.get("allocations"):
                    logger.warning(f"Address {self.address} is not eligible for ZKClaim")
                    return False
                else:
                    amount = int(data["allocations"][0]["tokenAmount"])
                    amount /= 10 ** 18
                    logger.success(f"Address {self.address} is eligible for ZKClaim with {amount} ZK")
                    return amount

            except Exception as error:
                logger.error(f"Error while checking address {self.address}: {error}")
                return False




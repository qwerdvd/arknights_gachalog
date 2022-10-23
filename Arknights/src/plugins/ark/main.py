import asyncio
from ark_gachalog.get_gachalogs import save_gachalogs
# from utils.ark_api.get_ark_data import get_uid_by_cookie


async def main():
    uid = 646610432
    await save_gachalogs(uid)


if __name__ == '__main__':
    asyncio.run(main())

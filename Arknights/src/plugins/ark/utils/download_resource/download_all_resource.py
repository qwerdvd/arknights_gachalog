import asyncio

from .download_from_prts import download_all_file_from_prts


async def download_all_resource():
    ret = await asyncio.gather(download_all_file_from_prts())
    ret = [str(x) for x in ret if x]
    if ret:
        return '\n'.join(ret)
    return '全部资源下载完成!'

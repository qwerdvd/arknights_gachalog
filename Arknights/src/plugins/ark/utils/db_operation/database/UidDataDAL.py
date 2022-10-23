from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from Arknights.src.plugins.ark.utils.db_operation.database.models import UidData


class UidDataDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_user_data(self, userid: int) -> Optional[UidData]:
        """
        :说明:
          获取用户的绑定信息
        :参数:
          * userid (int): QQ号。
        :返回:
          * data[0] (UidData): 数据信息。
        """
        sql = select(UidData).where(UidData.USERID == userid)
        result = await self.db_session.execute(sql)  # type: ignore
        data = result.scalars().all()
        if data:
            return data[0]
        else:
            return None

    async def user_exists(self, userid: int) -> bool:
        """
        :说明:
          是否存在用户的绑定信息
        :参数:
          * userid (int): QQ号。
        :返回:
          * data (bool): True/False。
        """
        data = await self.get_user_data(userid)
        if data:
            return True
        else:
            return False

    async def get_all_uid_list(self) -> List[str]:
        """
        :说明:
          获得所有绑定的UID列表
        :返回:
          * uid_list (List[str]): 绑定的UID列表。
        """
        sql = select(UidData).where(UidData.UID != '')
        result = await self.db_session.execute(sql)  # type: ignore
        data = result.scalars().all()
        uid_list = []
        for item in data:
            uid_list.extend(item.UID.split("_"))
        return uid_list

    async def get_uid_list(self, userid: int) -> List[str]:
        """
        :说明:
          获得用户的绑定UID列表
        :参数:
          * userid (int): QQ号。
        :返回:
          * uid_list (List[str]): 绑定的UID列表。
        """
        data = await self.get_user_data(userid)
        if data:
            if data.UID:
                uid_list = data.UID.split("_")
                return uid_list
        return []

    async def get_uid(self, userid: int) -> str:
        """
        :说明:
          获得用户绑定的UID
        :参数:
          * userid (int): QQ号。
        :返回:
          * uid (str): 绑定的UID。
        """
        uid_list = await self.get_uid_list(userid)
        if uid_list:
            return uid_list[0]
        else:
            return '未找到绑定的UID~'

    async def get_anyid(self, userid: int) -> str:
        """
        :说明:
          获得用户绑定的ID信息
        :参数:
          * userid (int): QQ号。
        :返回:
          * _id (str): 绑定的UID。
        """
        uid = await self.get_uid(userid)
        if uid:
            return uid
        else:
            return '未找到绑定的ID信息~'

    async def bind_db(self, userid: int, data: dict) -> str:
        """
        :说明:
          绑定UID
        :参数:
          * userid (int): QQ号。
          * data (dict): 绑定的UID。
            data = {'UID': UID}
        :返回:
          * msg (str): 绑定文字信息。
        """
        _bind = ''
        if await self.user_exists(userid):
            uid_list = await self.get_uid_list(userid)
            if 'UID' in data:
                if data['UID'] is not None:
                    new_uid = data['UID']
                    if data['UID'] in uid_list:
                        return f'该UID{data["UID"]}已经绑定过了噢~'
                    uid_list.append(data['UID'])
                    data['UID'] = '_'.join(uid_list)
                    _bind += (
                        f'绑定UID{new_uid}成功~\n当前绑定UID列表为{",".join(uid_list)}'
                    )

        await self.db_session.flush()  # type: ignore
        return _bind

    async def delete_db(self, userid: int, data: Optional[dict]) -> str:
        """
        :说明:
          删除用户的绑定UID
        :参数:
          * userid (int): QQ号。
          * data (dict): 删除的UID。
              data = {'UID': UID}
        :返回:
            * msg (str): 删除文字信息。
        """
        if await self.user_exists(userid):
            uid_list = await self.get_uid_list(userid)
            _delete = ''
            if data:
                if 'UID' in data:
                    if data['UID'] is not None:
                        if data['UID'] in uid_list:
                            delete_uid = data['UID']
                            uid_list.remove(data['UID'])
                            data['UID'] = '_'.join(uid_list)
                        else:
                            return f'该UID{data["UID"]}没有绑定过噢~'
                    else:
                        delete_uid = uid_list[0]
                        uid_list.pop(0)
                        data['UID'] = '_'.join(uid_list)
                    _delete += (
                        f'删除UID{delete_uid}成功~\n当前绑定UID列表为{",".join(uid_list)}'
                    )
            await self.update_db(userid, data)
        else:
            return '你还没有绑定过UID噢~'
        await self.db_session.flush()  # type: ignore
        return _delete

    async def update_db(
            self,
            userid: int,
            data: Optional[dict],
    ):
        """
        :说明:
          更新数据库中的UID数据
        :参数:
          * userid (int): QQ号。
          * data (dict): 绑定的UID。
            data = {'UID': UID}
        :返回:
          无返回值。
        """
        q = update(UidData).where(UidData.USERID == userid)
        if data is not None:
            q = q.values(**data)
            q.execution_options(synchronize_session="fetch")
            await self.db_session.execute(q)  # type: ignore

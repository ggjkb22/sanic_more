# Author: Q
# Date:   2023-5-9
# Desc:   用户登录验证失败锁定

from typing import Union, Tuple, Optional
from sanic import Sanic, Request
from app.conf import LoginFieldLockPolicy
from app.orm.models.system import SystemSetting


class LoginFailedLock:
    """用户登录失败锁定处理器"""

    @classmethod
    async def auto_init(cls, request: Request, username: str) -> Union["LoginFailedLock", bool]:
        """
        异步初始化, 该类都应该通过这个方法进行实例化
        如果返回False, 则说明锁定策略未开启
        """
        system_settings = await SystemSetting.auto_get_settings()
        lock_policy = system_settings.get("login_failed_lock_policy")
        # 判断锁定策略是否开启
        if lock_policy == LoginFieldLockPolicy.no_lock.value:
            return False
        # 如果锁定策略开启才对该类进行实例化等操作
        _self = cls()
        cache_redis = Sanic.get_app().ctx.cache_redis
        real_ip = request.remote_addr if request.remote_addr else request.ip
        username = username

        # 根据具体的锁定策略进行判断
        _self.lock_number = system_settings.get("login_failed_lock_number")
        lock_max_age = system_settings.get("login_failed_lock_max_age")
        if lock_policy == LoginFieldLockPolicy.lock_ip_user.value:
            # 锁定ip和用户名的策略
            _self.cache_key = f"{real_ip}_{username}_lock_number"
            lock_num, _self.set_lock_num = await cache_redis.auto_cache(_self.cache_key, return_type="str")
            _self.will_lock_msg = "此用户名已尝试 {} 次，剩余 {} 次！"
            _self.validate_err_msg = f"当前IP对该用户的登录行为被限制，请 {lock_max_age} 分钟后再试!"
        elif lock_policy == LoginFieldLockPolicy.lock_ip.value:
            # 锁定ip的策略
            _self.cache_key = f"{real_ip}_lock_number"
            lock_num, _self.set_lock_num = await cache_redis.auto_cache(_self.cache_key, return_type="str")
            _self.will_lock_msg = "已尝试 {} 次，剩余 {} 次！"
            _self.validate_err_msg = f"当前IP的登录行为被限制，请{lock_max_age}分钟后再试!"

        _self.lock_num = int(lock_num) if lock_num is not None else 0
        _self.lock_max_age = lock_max_age * 60
        _self.cache_redis = cache_redis
        return _self

    async def validate_lock(self) -> Tuple[bool, Optional[str]]:
        """
        用户登录失败锁定验证
        如果当前错误次数>=系统设置的次数则返回True, 表示该用户已锁定
        """
        if self.lock_num >= self.lock_number:
            return True, self.validate_err_msg
        return False, None

    async def update_lock_num(self) -> str:
        """用户登录失败锁定缓存更新"""
        new_lock_num = self.lock_num + 1
        new_cache = (new_lock_num, self.lock_max_age)
        await self.set_lock_num(new_cache)
        return self.will_lock_msg.format(new_lock_num, self.lock_number - new_lock_num)

    async def delete_lock_num(self):
        """
        删除缓存中对应键的锁定数
        在登录成功后使用
        """
        await self.cache_redis.del_cache(self.cache_key)

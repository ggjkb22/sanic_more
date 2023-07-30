# Author: Q
# Date:   2023-7-5
# Desc:   Arq异步队列自定义类


import msgpack


class MsgpackWorkerSettings:
    """使用Msgpack进行序列化的工作者类"""
    job_serializer = msgpack.packb
    # refer to MsgPack's documentation as to why raw=False is required
    job_deserializer = lambda b: msgpack.unpackb(b, raw=False)

# Author: Q
# Date:   2023-6-7
# Desc:   数据导出模块

import io
import xlsxwriter
import asyncio
from typing import List, Dict, Any, Optional


class DataExport:
    """数据导出类"""

    def __init__(self, data: List[Dict[str, Any]], titles: List[str]):
        """
        Params:
            data: 需要导出的数据
        """
        self.data = data
        self.titles = titles
        self.dt_format_kws = ["时间", "日期", "dt", "datetime", "date", "time"]

    def export_xlsx(self) -> io.BytesIO:
        """
        导出为xlsx
        Return:
            返回数据流
        """
        byte_io = io.BytesIO()
        workbook = xlsxwriter.Workbook(byte_io, {"remove_timezone": True})
        dt_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
        worksheet = workbook.add_worksheet()
        # 写入标题
        worksheet.write_row("A1", self.titles)
        # 修改时间列的格式
        for col, title in enumerate(self.titles):
            for kw in self.dt_format_kws:
                if kw in title:
                    worksheet.set_column(col, col, None, dt_format)

        # 往每个单元格中写入数据
        for i, row in enumerate(self.data):
            for j, col in enumerate(row.values()):
                worksheet.write(i + 1, j, col)
        workbook.close()
        byte_io.seek(0)
        return byte_io


def data_export_xlsx(data: List[Dict[str, Any]], titles: List[str]) -> io.BytesIO:
    """快捷导出xlsx"""
    return DataExport(data, titles).export_xlsx()


async def async_data_export_xlsx(data: List[Dict[str, Any]], titles: List[str]) -> io.BytesIO:
    """异步化快捷导出xlsx"""
    coro = asyncio.to_thread(data_export_xlsx, data, titles)
    return await asyncio.create_task(coro)

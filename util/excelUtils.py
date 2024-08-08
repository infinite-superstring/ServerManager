import openpyxl
from openpyxl.styles import Font, Border, Side
from openpyxl.utils import get_column_letter
import os


class ColumnValidate(object):
    # 最小值，select有值时不生效
    min: int | None
    # 最大值，select有值时不生效
    max: int | None
    # 下拉选择
    select: dict[str, str] | None


class ExcelColumn(object):
    """表格列"""
    # 列名
    column_name: str
    # 列数据类型
    col_type: str
    # 模板长度，输出模板文件时使用
    template_length: int
    # 默认值，表格中的默认值，为None不插入默认值
    default: any
    # 校验规则
    validate: ColumnValidate | None


class ExcelRow(object):
    """表格行，用于存储表格数据信息，不包含表头"""
    # 表格数据
    data: list[any]
    # 校验错误，对应data列表，当错误时对应的bool为True
    error: list[bool]


class ExcelTable(object):
    """表格"""
    # 列
    cols: list[ExcelColumn]
    # 行
    rows: list[ExcelRow]

    def __init__(self, cols: list[ExcelColumn] = [], rows: list[ExcelRow] = []):
        self.cols = cols
        self.rows = rows


class ExcelUtils(object):
    tables: dict[str:ExcelTable]
    # 创建加粗字体样式
    font = Font(bold=True)
    # 创建边框样式
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    def __init__(self, tables=None):
        if tables is None:
            tables = {}
        self.tables = tables

    def createExcelTemplate(self, save_path):
        """
        创建Excel模板表格
        :param save_path: 输出文件路径
        """

        def _handle_table(work_book: openpyxl.Workbook, table_name: str, table_obj: ExcelTable):
            """
            处理工作表
            :param work_book: 工作簿对象
            :param table_name: 工作表名
            :param table_obj: 工作表对象
            """
            # 创建工作表
            work_table = work_book.create_sheet(title=table_name)
            # 创建表头
            for col_num, column in enumerate(table_obj.cols, start=1):
                print(col_num, column)
                cell = work_table.cell(row=1, column=col_num, value=column.col_type)
                cell.value = column.column_name
                cell.font = self.font
                cell.border = self.border

        wb = openpyxl.Workbook()
        for table_name, table in self.tables.items():
            print(table_name, table)
            _handle_table(wb, table_name, table)
            # # 创建表头
            # for col_num, column in enumerate(table.columns, start=1):
            #     cell = ws.cell(row=1, column=col_num, value=column.col_type)
            #     ws.column_dimensions[get_column_letter(col_num)].width = column.template_length
            #
            # # 插入默认值
            # for row_num, row in enumerate(table.rows, start=2):
            #     for col_num, value in enumerate(row.data, start=1):
            #         ws.cell(row=row_num, column=col_num, value=value)
        wb.save(save_path)

    def loadExcel(self, file_path):
        """
        读取Excel表格到对象并校验
        :param file_path: 要读取的文件
        """


if __name__ == '__main__':
    eutils = ExcelUtils({"表1": ExcelTable()})
    eutils.createExcelTemplate("file.xlsx")

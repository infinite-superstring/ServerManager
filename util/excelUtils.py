import openpyxl
from openpyxl.styles import Font, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from util.logger import Log
import os


class ColumnValidate(object):
    # 最小值，select有值时不生效
    min: int | None
    # 最大值，select有值时不生效
    max: int | None
    # 下拉选择
    select: list[str] | None
    # 错误标题
    error_title: str | None
    # 错误信息
    error_msg: str | None

    def __init__(self, min: int | None = None, max: int | None = None, select: list[str] | None = None, error_title: str | None = None, error_msg: str | None = None):
        """
        :param min: 最小值
        :param max: 最大值
        :param select: 选项
        :param error_title: 错误标题
        :param error_msg: 错误提示信息
        """
        self.min = min
        self.max = max
        self.select = select
        self.error_title = error_title
        self.error_msg = error_msg


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

    def __init__(self, column_name: str, col_type: str = 'str', template_length: int = 20, default: any = '', validate: ColumnValidate | None = None):
        """
        :param column_name: 列名
        :param col_type: 列数据类型
        :param template_length: 列模板长度（减去表头）
        :param default: 列默认值
        :param validate: 校验规则
        """
        self.column_name = column_name
        self.col_type = col_type
        self.template_length = template_length
        self.default = default
        self.validate = validate


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

        def _create_data_validation(data_type: str, rule: ColumnValidate) -> DataValidation:
            """
            创建数据校验规则
            """
            dv = DataValidation()

            if rule.error_msg:
                dv.error = rule.error_msg
            else:
                dv.error = "数据值校验失败，请检查是否填写无误"
            if rule.error_title:
                dv.error_title = rule.error_title
            else:
                dv.error_title = "数据校验失败"
            dv.showErrorMessage = True

            if rule.min and rule.max:
                dv.formula1 = rule.min
                dv.formula2 = rule.max
                dv.operator = "lessThanOrEqual"
            else:
                if rule.min:
                    dv.formula1 = rule.min
                    dv.operator = "greaterThan"
                if rule.max:
                    dv.formula1 = rule.max
                    dv.operator = "lessThan"

            match data_type:
                case 'str':
                    dv.type = "textLength"
                    return dv
                case 'int':
                    dv.type = "whole"
                    return dv
                case 'float':
                    dv.type = "decimal"
                    return dv
                case 'bool':
                    dv.type = "list"
                    dv.allow_blank = True
                    dv.formula1 = '"True,False"'
                    dv.prompt = '请选择一个有效的选项'
                    dv.promptTitle = '输入提示'
                    return dv
                case 'select':
                    dv.type = "list"
                    dv.allow_blank = True
                    dv.formula1 = f'"{",".join(rule.select)}"'
                    dv.prompt = '请选择一个有效的选项'
                    dv.promptTitle = '输入提示'
                    return dv
                case _:
                    Log.warning(f"Unknown data type: {data_type}")

            return dv

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
                Log.debug(f"col index: {col_num}")
                Log.debug(f"column: {column.column_name}")
                cell = work_table.cell(row=1, column=col_num, value=column.col_type)
                cell.value = column.column_name
                cell.font = self.font
                cell.border = self.border
                col_letter = openpyxl.utils.get_column_letter(col_num)

                Log.debug(column.validate)

                if column.validate:
                    data_rule = _create_data_validation(column.col_type, column.validate)
                    work_table.add_data_validation(data_rule)
                    data_rule.add(f"{col_letter}2:{col_letter}{column.template_length}")

                for row in range(2, column.template_length + 1):
                    selected_cell = work_table[f"{col_letter}{row}"]
                    selected_cell.border = self.border  # 设置单元格边框
                    if column.default:
                        selected_cell.value = column.default



        wb = openpyxl.Workbook()
        for table_name, table in self.tables.items():
            Log.debug(f"table name: {table_name}")
            _handle_table(wb, table_name, table)
        wb.save(save_path)

    def loadExcel(self, file_path):
        """
        读取Excel表格到对象并校验
        :param file_path: 要读取的文件
        """


if __name__ == '__main__':
    number = ColumnValidate(3,10)
    string_length = ColumnValidate(3, 10)
    cols = [
        ExcelColumn("A1", default="111", validate=string_length),
        ExcelColumn("A2", 'int', validate=number),
        ExcelColumn("A3", 'float', validate=number),
        ExcelColumn("A4", 'bool', validate=ColumnValidate()),
        ExcelColumn("A5", 'select', validate=ColumnValidate(select=["测试1", "测试2", "测试3"])),
        ExcelColumn("A6"),
    ]
    eutils = ExcelUtils({"表1": ExcelTable(cols)})
    eutils.createExcelTemplate("file.xlsx")

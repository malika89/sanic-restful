#! usr/bin/env/python
# _*_ coding:utf-8 _*_


import xlrd
from django.http import FileResponse
from rest_framework.response import Response
import pandas as pd
import datetime
from urllib.parse import quote
import os

import_model = {
    'key': "some model",
}


def import_excel(fileUpload):
    """
    模板第一行为英文，对应model字段；第二行为中文；剩下行为数据
    :param fileUpload:
    :return: 返回字典list数据，可以用于直接创建、修改model实例
    """
    file_content = fileUpload.read()
    wb = xlrd.open_workbook(file_contents=file_content)
    table = wb.sheets()[0]
    first_row = table.row_values(0)
    max_row = table.nrows
    upload_list = []
    for i in range(2, max_row):
        row_data = table.row_values(i)
        upload_list.append(row_data)
    max_column = table.ncols
    if max_column == 1:
        return [i[0] for i in upload_list]
    import pandas as pd
    data = pd.DataFrame(upload_list, columns=first_row)
    return data.to_dict(orient='records')


def export_excel(data, model_name):
    """
    :param data: list [{"用户名"：'abc',"密码":'123'},{"用户名"：'xyz',"密码":'123'}]
    :return:
    """
    pd_data = pd.DataFrame(data)
    excel_name = f'{model_name}_{datetime.datetime.now().strftime("%Y-%m-%d")}.xls'
    pd_data.to_excel('/tmp/'+excel_name, index=False)
    response = FileResponse(open('/tmp/'+excel_name, 'rb'))
    response['content_type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = quote(excel_name)
    return response


def file_response(file_path, filename):
    download_file = os.path.join(file_path, filename)
    if not os.path.isfile(download_file):
        response = Response(code=100,message=f'{filename}不存在', status=100,content_type='application/json')
        return response
    response = FileResponse(open(os.path.join(file_path, filename), 'rb'))
    if str(filename).__contains__('xls'):
        response['Content-Type'] = 'application/vnd.ms-excel'
    elif str(filename).__contains__('zip'):
        response['Content-Type'] = 'application/zip '
    else:
        response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = quote(filename)
    return response
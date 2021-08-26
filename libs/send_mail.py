# -*- coding: utf-8 -*-

import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from io import BytesIO
import xlwt
from sanic.response import HTTPResponse,StreamingHTTPResponse
from json2html.jsonconv import json2html
from settings import *


RED_COLOR = '<strong><font color="#FF0000">{}</font></strong><br>'
BLUE_COLOR = '<strong><font color="#0000FF">{}</font></strong><br>'

msghead = "平台自动发送，请勿回复!"


class SendMail(object):
    def __init__(self, user=None, password=None, host='smtp.gmail.com', port=None,
                 smtp_ssl=True, debuglevel=0, encoding="utf-8", **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.kwargs = kwargs
        self.debuglevel = debuglevel
        self.smtp_ssl = smtp_ssl
        self.encoding = encoding

    def login(self):
        """
        Login to the SMTP server using password. `login` only needs to be manually run when the
        connection to the SMTP server was closed by the user.
        """
        smtp = smtplib.SMTP(timeout=10)
        smtp.connect(self.host, self.port)
        try:
            smtp.starttls()
        except smtplib.SMTPNotSupportedError:
            pass
        # if self.user and self.password:
        #     smtp.login(self.user, self.password)
        # ssl登录
        # smtp = smtplib.SMTP_SSL(
        #     self.host, self.port) if self.smtp_ssl else smtplib.SMTP(self.host, self.port)
        # smtp.set_debuglevel(self.debuglevel)
        # smtp.ehlo(self.host)
        # smtp.login(self.user, self.password)
        return smtp

    def send_email(self, to, subject, contents, sender=None, cc=None, text='plain'):
        """
        暂时未使用
        logger.infon smtp to send email
        :param to:
        :param subject:
        :param contents:
        :param sender:
        :param cc:
        :return:
       """
        if not cc: cc = ADMIN_EMAIL
        smtp = self.login()
        msg = MIMEText(contents, text, self.encoding)
        msg["Subject"] = Header(subject, 'utf-8')
        msg["From"] = sender if sender else self.user
        msg["To"] = to
        msg["Cc"] = cc
        msg["Bcc"] = ""
        smtp.sendmail(sender, [to, cc], msg.as_string())
        smtp.quit()

    def conn_email(self, to, subject, contents, sender='S',
                   cc='', bcc='', text='plain', filepath=None):
        """
        Connect smtp to send email
        :param to:
        :param subject:
        :param contents:
        :param sender:
        :param cc:
        :return:
        """
        # 环境判断
        if CURRENT_ENV != 'PROD':
            to = ['']
            cc = ['']
        if not cc: cc = ''
        smtp = self.login()
        msg = MIMEMultipart()
        msg_contents = MIMEText(contents, text, self.encoding)
        msg.attach(msg_contents)
        msg["Subject"] = Header(subject, 'utf-8')
        msg["From"] = sender if sender else self.user
        if isinstance(to, str):
            to = list(set(to.split(';')))
            msg["To"] = ';'.join(to)
        elif isinstance(to, list):
            msg["To"] = ';'.join(list(set(to)))
        if isinstance(cc, str):
            cc = list(set(cc.split(';')))
            msg["Cc"] = ';'.join(cc)
        elif isinstance(cc, list):
            msg["Cc"] = ';'.join(list(set(cc)))
        msg["Bcc"] = bcc
        if filepath and isinstance(filepath, list):
            for file in filepath:
                logger.info('{}读取file地址:{}{}'.format('*' * 30, file, '*' * 30))
                filename = os.path.basename(file)
                msg_attachment = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
                msg_attachment["Content-Type"] = 'application/octet-stream'
                msg_attachment.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(msg_attachment)
        bcc = [msg["Bcc"]]
        receivers = to + cc + bcc
        logger.debug('sender:{}, receivers:{}'.format(sender, receivers))
        smtp.sendmail(sender, receivers, msg.as_string())
        smtp.quit()
        logger.info('{}conn_email发送邮件----------结束{}'.format('*' * 30, '*' * 30))


smtp = SendMail(host=EMAIL_AUTH_HOST, user=EMAIL_USER, password=EMAIL_PASS, port=EMAIL_PORT, smtp_ssl=False, debuglevel=0)


def alert_head(username):
    if CURRENT_ENV in ("运营","PROD"):
        ENV = RED_COLOR.format(CURRENT_ENV)
        AUSER = RED_COLOR.format(username)
    else:
        ENV = BLUE_COLOR.format(CURRENT_ENV)
        AUSER = BLUE_COLOR.format(username)
    alertinfo = "{}</br></br> 环境: {} 操作人: {} 结果:</br>".format(
        msghead, ENV, AUSER)
    return alertinfo


def domain_alert(
        username, subject='域名系统通知',
        to=" ", cc='',
        message='', is_alert=True, filepath=None, text='plain', html_escape=True):
    try:
        # 通知邮件体
        if is_alert:
            messagebody = alert_head(username)
        else:
            messagebody = '{}</br></br>'.format(msghead)
        if message and isinstance(message, list):
            for msg in message:
                if isinstance(msg, dict or list):
                    messagebody += str(json2html.convert(json=msg, escape=html_escape))
                else:
                    messagebody += str(message)
        if message and isinstance(message, dict):
            messagebody += str(json2html.convert(json=message, escape=html_escape))
        elif message and isinstance(message, str):
            messagebody += str(message)
        smtp.conn_email(
            to=to, cc=cc,
            subject=subject, contents=messagebody, text=text,
            filepath=filepath if isinstance(filepath, list) else None,
        )
        logger.info("发送告警邮件成功: {}".format(subject))
    except Exception as e:
        err = e.__str__()

def send_expire_email(title, content, receivers, file=None):
    """
    发送证书过期邮件
    """
    sender = ''
    content_head = str(content).replace('\r\n', ' ')[0:30]
    if CURRENT_ENV not in ("PROD","运营"):
        DEBUG_EMAIL = True
        if DEBUG_EMAIL:
            receivers = ''
            title = title + '(debug)'
        else:
            return True

    content = content + "\r\n"
    content = content + "\r\n----------------------------------------------."
    content = content + "\r\n域名系统自动发送邮件，请勿回复."
    content = content + "\r\n环境: %s." % CURRENT_ENV
    content = content + "\r\n----------------------------------------------."

    try:
        message = MIMEMultipart()
        msg_contents = MIMEText(content, 'plain', 'utf-8')
        message.attach(msg_contents)
        message['Subject'] = title
        message['From'] = sender

        if isinstance(receivers, str):
            message['To'] = Header(receivers, 'utf-8')
            receivers_new = receivers
        else:
            # list 去重复邮件地址
            receivers_new = list()
            for r in receivers:
                if r not in receivers_new:
                    receivers_new.append(r)
            message['To'] = ";".join(receivers_new)
        # attach file
        if file is not None:
            filename = os.path.basename(file)
            msg_attachment = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
            msg_attachment["Content-Type"] = 'application/octet-stream'
            msg_attachment.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(msg_attachment)
        # sendmail
        smtp.conn_email('', "域名系统证书过期", message.as_string(), sender, receivers_new)
        logger.info('title: %r, mail: %r, send succeed' % (title, receivers_new))
    except Exception as e:
        logger.error('title: %s, mail: %r, Exception: %s' % (title, receivers, e))
        return False
    return True


def send_email_excel(table, head_dic, title, content, receivers, basefilename):
    """发送带excel附件的邮件"""
    filename = '/tmp/%s.xls' % basefilename
    # 保存 excel
    xls = XlsLoader()
    xls.skip_default = False
    xls.load(table=table, dic=head_dic, filename=filename)
    logger('save %s' % filename)
    send_expire_email(title, content, receivers, file=filename)


class XlsLoader(object):
    """从数据表结构体导入数据"""
    stringio = None
    skip_fields = None # 需要过滤的字段
    skip_default = True # 是否默认过滤不在‘列名’里面的字段
    dic = None  # 列名

    def load(self, table, dic, filename=None):
        """
        :param table: 需要保存数据的list对象
        :param dic: 字典key转义列头名称
        :param filename: 需要保存的文件名 (.xls) 如果空，则保存到stringio
        :return:
        """
        from datetime import date
        try:
            self.stringio = BytesIO()
            self.dic = dic
            wb = xlwt.Workbook()
            sheet = wb.add_sheet('sheet_export', cell_overwrite_ok=True)
            font = xlwt.Font()
            font.bold = True
            style = xlwt.XFStyle()
            style.font = font
            if len(table) <= 0:
                return self.failure(msg='无效的数据', detail="failure: table len<=0, %s" % self.__class__.__name__)
            # 写入列名
            col = 0
            for key in table[0].keys():
                if self.is_skip(key):
                    continue
                sheet.write(0, col, self._colname(dic, key), style)
                current_col = sheet.col(col)
                current_col.width = 250*26
                col = col + 1
            # 写入数据
            for row in range(0, len(table)):
                keys = table[row].keys()
                col = 0
                for key in table[row].keys():
                    if self.is_skip(key):
                        continue
                    v = table[row][key]
                    if isinstance(v, datetime):
                        v = v.strftime('%Y-%m-%d %H:%M:%S') # 转换时间字符串
                    elif isinstance(v, date):
                        v = str(v) # 转换时间字符串
                    elif v is None:
                        v = '--'
                    else:
                        v = str(v)
                    # logd(v)
                    sheet.write(row + 1, col, v)
                    col = col + 1
            if filename is not None: # 保存文件
                wb.save(filename)
            else: # 保存到 io, 用于无文件流式下载
                wb.save(self.stringio)
                self.stringio.seek(0)
            # logi(self.stringio.getvalue())
        except Exception as e:
            logger.info('Exception: ' + str(e), self.__class__.__name__)
            return self.failure(msg='无效的数据', detail=e)
        return True

    def _file_streaming(self, chunk_size=512):
        while True:
            c = self.stringio.read(chunk_size)
            if c:
                yield c
            else:
                break

    def _colname(self, dic, key):
        if type(dic) is dict:
            if key in dic.keys():
                return dic[key]
        return key

    def is_skip(self, key):
        if self.skip_default:
            if self.dic is not None and key in self.dic.keys():
                return False
        else:
            if self.skip_fields is not None and key in self.skip_fields:
                return True
        return self.skip_default

    def streaming_response(self):
        try:
            response_ = StreamingHTTPResponse(self._file_streaming())
            response_['Content-Type'] = 'application/octet-stream'
            response_['Content-Disposition'] = 'attachment;filename="export.xls"'
            return response_
        except FileNotFoundError as e:
            return HTTPResponse(e.__str__(),status=100)

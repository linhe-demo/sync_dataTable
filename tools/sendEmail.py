import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from tools.readFile import read_json_config
from tools.log import error
from tools.log import info


def sendEmail(title, content, receiver, fileName=None, filePath=None, DeleteStatus=False):
    # 获取邮箱配置信息
    config = read_json_config()  # 获取配置信息
    config = config['email']

    message = MIMEMultipart()
    message['From'] = "{}".format(config['fromAddress'])
    message['To'] = ",".join(receiver)
    message['Subject'] = title  # 邮件主题
    message.attach(MIMEText(content, 'plain', 'utf-8'))  # 内容, 格式, 编码
    if filePath is not None:
        file = MIMEText(open(filePath, 'rb').read(), 'base64', 'utf-8')
        file["Content-Type"] = 'application/octet-stream'
        file["Content-Disposition"] = 'attachment; filename="%s"' % fileName
        message.attach(file)
    try:
        mailserver = smtplib.SMTP_SSL(config['host'], config['port'])  # 启用SSL发信, 端口一般是465
        mailserver.login(config['user'], config['password'])  # 登录验证
        mailserver.sendmail(config['fromAddress'], receiver, message.as_string())  # 发送
        mailserver.quit()
        info("邮件发送成功 %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if DeleteStatus is True:
            if os.path.exists(filePath):
                os.remove(filePath)
                info("删除文件成功")
            else:
                error("删除文件失败")
    except smtplib.SMTPException as e:
        error(e)

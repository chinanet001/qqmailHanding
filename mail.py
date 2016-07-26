#!/usr/bin/python
# -*- coding:utf-8 -*-

import poplib, pprint, email, sys, time, email, time, smtplib, imaplib
from datetime import datetime, timedelta, date
from email.mime.text import MIMEText  
from email.header import Header
#设置命令窗口输出使用UTF-8编码
reload(sys)
sys.setdefaultencoding( "utf-8" )


# 第三方 SMTP 服务  注意这是企业邮箱  如果是个人邮箱，密码要用授权码，pop服务器地址没有exmail
mail_smtp_host= "smtp.exmail.qq.com"  		# 设置smtp服务器  
mail_pop_host= "pop.exmail.qq.com"			# 设置pop服务器
mail_user= ""    		# 用户名  
mail_pass= ""  				# 口令,QQ邮箱是输入授权码，在qq邮箱设置 里用验证过的手机发送短信获得，不含空格 

'''
/*DISCRIPTION
 *	Decoding charsert
 * ARGUMENTS
 * 	string need be Decodinged
 * RETURN
 * NOTES
 */
'''
def Decoding(str):
	if(str[0][1] == None): return unicode(str[0][0], 'gb18030')
	else: return unicode(str[0][0], str[0][1])
	
'''
/*DISCRIPTION
 *	Send the mail to the unsubmit
 * ARGUMENTS
 * 	string need be Decodinged
 * RETURN
 * NOTES
 */
'''
def  SendEmail():
	sender = ''  
	receivers = ['']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱  
  
	message = MIMEText('a test for python', 'plain', 'utf-8')  
	message['From'] = Header("ppyy", 'utf-8')  
	message['To'] =  Header("you", 'utf-8')  
  
	subject = 'my test'  
	message['Subject'] = Header(subject, 'utf-8')  
	try:  
  		smtpObj = smtplib.SMTP_SSL(mail_smtp_host, 465)   
  		smtpObj.login(mail_user,mail_pass)    
  		smtpObj.sendmail(sender, receivers, message.as_string()) 
  		smtpObj.quit()  
  		print u"邮件发送成功"  
	except smtplib.SMTPException,e:  
  		print e  


def GetEmail():
	try:
		pp = poplib.POP3_SSL(mail_pop_host)
		pp.user(mail_user)
		pp.pass_(mail_pass)
		ret =pp.stat()
		print u"登录成功"
	except:
		print "can't connect to mailserver"

	#遍历邮件的标题
	# emailMsgNum, emailSize = pp.stat()
	# for i in xrange(1, emailMsgNum+1):
	# 	ret = pp.retr(i)
	# 	mail = email.message_from_string("\n".join(ret[1]))
	# 	subject = email.Header.decode_header(mail['subject'])
	# 	MailSubject 	= Decoding(subject)
	# 	print MailSubject  
		                
	ret = pp.retr(2)
	msg = email.message_from_string("\n".join(ret[1]))
	print msg.get_payload()

	# down = pp.retr(1)
	# print 'lines:', len(down)
	# for line in down[1]:
	#  	print line

	pp.quit()

#保存文件方法（都是保存在指定的根目录下）
def savefile(filename, data, path):
    try:
        filepath = path + filename
        print 'Saved as ' + filepath
        f = open(filepath, 'wb')
    except:
        print('filename error')
        f.close()
    f.write(data)
    f.close()
   
#字符编码转换方法
def my_unicode(s, encoding):
    if encoding:
        return unicode(s, encoding)
    else:
        return unicode(s)

#获得字符编码方法
def get_charset(message, default="ascii"):
    #Get the message charset
    return message.get_charset()
    return default

#解析邮件方法（区分出正文与附件）
def parseEmail(msg, mypath):
    mailContent = None
    contenttype = None
    suffix =None
    for part in msg.walk():
        if not part.is_multipart():
            contenttype = part.get_content_type()   
            filename = part.get_filename()
            charset = get_charset(part)
            #是否有附件
            if filename:
                h = email.Header.Header(filename)
                dh = email.Header.decode_header(h)
                fname = dh[0][0]
                encodeStr = dh[0][1]
                if encodeStr != None:
                    if charset == None:
                        fname = fname.decode(encodeStr, 'gbk')
                    else:
                        fname = fname.decode(encodeStr, charset)
                data = part.get_payload(decode=True)
                print('Attachment : ' + fname)
                #保存附件
                if fname != None or fname != '':
                    savefile(fname, data, mypath)            
            else:
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                if contenttype in ['text/html']:
                    suffix = '.htm'
                if charset == None:
                    mailContent = part.get_payload(decode=True)
                else:
                    mailContent = part.get_payload(decode=True).decode(charset)         
    return  (mailContent, suffix)

#获取邮件方法
def getMail(mailhost, account, password, diskroot, port = 993, ssl = 1):
    mypath = diskroot + ':\\'
    #是否采用ssl
    if ssl == 1:
        imapServer = imaplib.IMAP4_SSL(mailhost, port)
    else:
        imapServer = imaplib.IMAP4(mailhost, port)
    imapServer.login(account, password)
    imapServer.select()
    #邮件状态设置，新邮件为Unseen
    #Message statues = 'All,Unseen,Seen,Recent,Answered, Flagged'
    resp, items = imapServer.search(None, "Unseen")
    number = 1
    for i in items[0].split():
       #get information of email
       resp, mailData = imapServer.fetch(i, "(RFC822)")   
       mailText = mailData[0][1]
       msg = email.message_from_string(mailText)
       ls = msg["From"].split(' ')
       strfrom = ''
       if(len(ls) == 2):
           fromname = email.Header.decode_header((ls[0]).strip('\"'))
           strfrom = 'From : ' + my_unicode(fromname[0][0], fromname[0][1]) + ls[1]
       else:
           strfrom = 'From : ' + msg["From"]
       strdate = 'Date : ' + msg["Date"]
       subject = email.Header.decode_header(msg["Subject"])
       sub = my_unicode(subject[0][0], subject[0][1])
       strsub = 'Subject : ' + sub
             
       mailContent, suffix = parseEmail(msg, mypath)
       #命令窗体输出邮件基本信息
       print '\n'
       print 'No : ' + str(number)
       print strfrom
       print strdate
       print strsub
       '''
       print 'Content:'
       print mailContent
       '''
       #保存邮件正文
       if (suffix != None and suffix != '') and (mailContent != None and mailContent != ''):
           savefile(str(number) + suffix, mailContent, mypath)
           number = number + 1
           
    imapServer.close()
    imapServer.logout()


if __name__ =="__main__":
    #邮件保存在e盘
    mypath ='e'
    print 'begin to get email...'
    getMail('pop.gmail.com', 'xxxxxxxx@gmail.com', 'xxxxxxxx', mypath, 993, 1)
    #126邮箱登陆没用ssl
    #getMail('imap.126.com', 'xxxxxxxxx@126.com', 'xxxxxxxxxx', mypath, 143, 0)
    print 'the end of get email.'
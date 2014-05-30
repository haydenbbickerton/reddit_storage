#!/usr/bin/env python
from __future__ import division
import sys,os,time,random,struct,hashlib,Tkinter
sys.modules['tkinter'] = Tkinter
from Tkinter import *
import tkFileDialog
from tkMessageBox import *
import tkMessageBox
import ttk
import praw
import re
import math
import binascii
import praw
from Crypto.Cipher import AES
from collections import defaultdict
import sqlite3
import encryption
r = praw.Reddit(user_agent='Reddit Storage')
db = sqlite3.connect(':memory:')
cursor = db.cursor()
cursor.execute('''CREATE TABLE files(id INTEGER PRIMARY KEY, url TEXT, title TEXT, filesize TEXT, size TEXT, filename TEXT)''')
db.commit()

class LoginScreen(Tkinter.Tk):

    def __init__(self, parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.infotext = StringVar()
        self.infotext.set("Please enter your information to continue.")
        self.initialize()
        

    def initialize(self):
        frame = ttk.Frame(borderwidth=5, relief="sunken", width=200, height=100)
        self.infolbl = ttk.Label(textvariable=self.infotext)
        self.sepline = ttk.Separator(orient=HORIZONTAL)
        self.rusernamelbl = ttk.Label(text="Reddit Username:")
        self.rusername = ttk.Entry(self)
        self.rpasswordlbl = ttk.Label(text="Reddit Password:")
        self.rpassword = ttk.Entry(self)
        self.passwordlbl = ttk.Label(text="Encryption Password:")
        self.password = ttk.Entry(self)
        self.ok = ttk.Button(text="Okay", command=self.login)
        self.exitbtn = ttk.Button(text="Exit", command=self.quit)

        
        self.infolbl.grid(column=0, row=0, columnspan=4, padx=10, pady=10)
        self.sepline.grid(column=0, row=1, columnspan=4, padx=0, pady=0, sticky="ew")
        self.rusernamelbl.grid(column=0, row=2, columnspan=1, padx=10, pady=10)
        self.rusername.grid(column=1, row=2, columnspan=1, padx=10, pady=10)
        self.rpasswordlbl.grid(column=0, row=3, columnspan=1, padx=10, pady=10)
        self.rpassword.grid(column=1, row=3, columnspan=1, padx=10, pady=10)
        self.passwordlbl.grid(column=0, row=4, columnspan=1, padx=10, pady=10)
        self.password.grid(column=1, row=4, columnspan=1, padx=10, pady=10)
        self.exitbtn.grid(column=0, row=5, padx=10, pady=10)
        self.ok.grid(column=1, row=5, padx=10, pady=10)


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def quit(self):                           
        self.destroy()
        
    def login(self):
        self.therusername = self.rusername.get()
        self.therpassword = self.rpassword.get()
        self.thepassword = self.password.get()
        subname = str(binascii.hexlify(self.therusername)[:10])                     
        try:
			
           r.login(self.therusername, self.therpassword)
           self.infotext.set("login successful")
           try:
               r.get_subreddit(subname, fetch=True).get_top(limit=10)
           except Exception, e:
               print e
               try:
                  r.create_subreddit(subname, title='Encrypted Storage Space', description='This is storage')
               except Exception, e:
                   print e
                   print "I guess I programmed this part wrong, sorry. Contact me please - haydenbbickerton@gmail.com"
           self.quit()
        except Exception, e:
            print e
            self.infotext.set("Reddit login unsuccessful, try again")
        
    
class BrowseScreen(Tkinter.Tk):
    
    def __init__(self, parent, rusername, rpassword, password):
        Tkinter.Tk.__init__(self,parent)
        self.key = hashlib.sha256(password).digest()
        self.parent = parent
        self.queue = Queue.Queue()
        self.geometry("400x500")
        self.infotext = StringVar()
        self.infotext.set("Please enter your information to continue.")
        r.login(rusername, rpassword)
        self.subname = str(binascii.hexlify(rusername)[:10])   
        self.initialize()

    def initialize(self):
        frame = ttk.Frame(borderwidth=5, relief="sunken")
        self.listbox = Listbox()
        self.s = ttk.Scrollbar(orient=VERTICAL, command=self.listbox.yview)
        self.selected = ttk.Label(textvariable=self.infotext)
        self.downloadbtn = ttk.Button(text="Download", command=self.downloadfile, state=NORMAL)
        self.deletebtn = ttk.Button(text="Delete", command=self.deletefile, state=NORMAL)
        self.progressbar = ttk.Progressbar(orient=HORIZONTAL, length=200, mode='determinate')
        self.listbox.bind('<<ListboxSelect>>', self.onselect) 
        self.downloadbtn.grid(column=2, row=1, sticky=(S,E))
        self.deletebtn.grid(column=1, row=1, sticky=(S,E))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.menubar = Menu(self)
        self.menubar.add_command(label="Upload", command=self.pickfile)
        self.menubar.add_command(label="Refresh", command=self.fetchfiles)
        self.menubar.add_command(label="Quit", command=self.quit)
        self.config(menu=self.menubar)
        
        self.listbox.grid(row=0, column=0, rowspan=4, columnspan=3, sticky=N+E+S+W, pady=(0,40))
        self.listbox.columnconfigure(0, weight=1)
        self.listbox.configure(yscrollcommand=self.s.set)
        self.s.grid(row=0, column=3, sticky=(N,S))
        self.selectedurl = ""
        self.selected.grid(column=0, row=1, columnspan=4, padx=10, pady=10, sticky=E+S+W)
        self.progressbar.grid(column=0, row=5, columnspan=4, sticky=N+E+S+W)
        self.fetchfiles()
        
    

    def fetchfiles(self):
        self.listbox.delete(0, END)
        cursor.execute('''DELETE FROM files''');
        db.commit()
        self.listbox.config(bg='gray')
        self.infotext.set("Loading...")
        self.update()
        time.sleep(0.25)
        self.submissions = r.get_subreddit(self.subname).get_new(limit=None)
        
        for x in self.submissions:
            post = x
            url = post.url
            filesize = post.selftext
            title = post.title
            size = "42.7kb"
            filename = title
            self.listbox.insert('end', "%s" % filename)
            cursor.execute('''INSERT INTO files(url, title, filesize, size, filename) VALUES(?,?,?,?,?)''', (url, title, filesize, size, filename))
            db.commit()
            
        self.listbox.config(bg='white')
        self.infotext.set("")        		

		        
    def onselect(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        filesizecursor = cursor.execute('''SELECT filesize FROM files WHERE filename=?''', (value,))
        filesize = cursor.fetchone()
        urlcursor = cursor.execute('''SELECT url FROM files WHERE filename=?''', (value,))
        url = cursor.fetchone()
        print 'You selected item %d: "%s"' % (index, value)
        self.infotext.set("%s" % (filesize))

    def deletefile(self):
        selection = self.listbox.get(self.listbox.curselection())
        filenamecursor = cursor.execute('''SELECT filename FROM files WHERE filename=?''', (selection,))
        filename = "".join(cursor.fetchone())
        urlcursor = cursor.execute('''SELECT url FROM files WHERE filename=?''', (selection,))
        posturl = cursor.fetchone()
        question = "Are you sure that you want to delete %s from reddit? Make sure you have a local copy of this file, because this action cannot be undone." % (selection)
        result = tkMessageBox.askquestion("Delete", question)
        if result == 'yes':
            self.progressbar.config(mode="indeterminate")
            self.progressbar.start(interval=50)
            fileurl = "".join(posturl)
            submission = r.get_submission(url=fileurl, comment_limit=None, comment_sort='new')
            submission.delete()
            self.progressbar.stop()
            self.progressbar.config(mode="determinate")
            showinfo('OK', '%s has been deleted from Reddit' % (selection))
        else:
            self.fetchfiles()
		

        
    def downloadfile(self):
        selection = self.listbox.get(self.listbox.curselection())
        filenamecursor = cursor.execute('''SELECT filename FROM files WHERE filename=?''', (selection,))
        filename = "".join(cursor.fetchone())
        encryptedfile = filename + ".enc"
        urlcursor = cursor.execute('''SELECT url FROM files WHERE filename=?''', (selection,))
        posturl = cursor.fetchone()
        question = "Are you sure you want to download %s?" % (selection)
        result = tkMessageBox.askquestion("Download", question)
        chunks = []
        if result == 'yes':
            self.progressbar.config(mode="indeterminate")
            self.progressbar.start(interval=50)
            fileurl = "".join(posturl)
            submission = r.get_submission(url=fileurl, comment_limit=None, comment_sort='new')

            flat_comments = praw.helpers.flatten_tree(submission.comments)
            for comment in flat_comments:
                chunks.extend(["".join(comment.body)])

            filestring = re.sub('0-', '', re.sub('-[0-9]*-', '', "-".join(chunks[::-1])))
            nohex = binascii.unhexlify(filestring)
            path = tkFileDialog.askdirectory(parent=self, title='Choose a directory to save the file in')
            if path:
                with open(path + "/" + encryptedfile, 'wb') as f:
                    f.write(nohex)
                encryption.decrypt_file(self.key, path + "/" + encryptedfile)
                os.remove(path + "/" + encryptedfile)
                self.progressbar.stop()
                self.progressbar.config(mode="determinate")
                showinfo('OK', 'Download successful!')
                self.fetchfiles()
            else:
                self.progressbar.stop()
                self.progressbar.config(mode="determinate")
                self.fetchfiles()


       

    def uploadfile(self, file, ufilesize):
        path, filename = os.path.split(file)
        encryption.encrypt_file(self.key, file)
        encryptedfile = file + ".enc"
        
        with open(encryptedfile, 'rb') as f:
            content = f.read()
            
        filedata = binascii.hexlify(content)    
        chunknum = 0      
        chunknum = 0
        filelength = int(math.ceil(len(filedata) / 9995))
        self.progressbar.config(maximum=filelength)
        newpost = r.submit(self.subname, filename, text=ufilesize)
        myurl = newpost.url
        mysubmission = r.get_submission(url=myurl)   
           
        for chunk in self.chunks(filedata, 9995):
            newchunk = str(chunknum) + "-" + chunk
            mysubmission.add_comment(newchunk)
            chunknum = chunknum + 1
            mynuma = chunknum + 1
            self.progressbar.config(value=chunknum)
            self.update_idletasks()
            
        os.remove(encryptedfile)
        showinfo('OK', '%s uploaded successfully!' % (filename))
        self.progressbar.config(value=0)
        self.fetchfiles()

    def pickfile(self):
        file = tkFileDialog.askopenfilename(parent=self, title='Choose a file')
        if file:
            if (os.path.getsize(file) > 1048576):
                showinfo('OK','This file is bigger than 1 Megabyte. Reddit Storage is just anexperiment, let\'s not bog down Reddit\'s servers. Please select a smaller file.')
            else:
                ufilesize = self.sizeof_fmt(os.path.getsize(file))
                self.uploadfile(file, ufilesize)

    def sizeof_fmt(self, num):
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if num < 1024.0 and num > -1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')
       
    def chunks(self, s, n):
        """Produce `n`-character chunks from `s`."""
        for start in range(0, len(s), n):
            yield s[start:start + n]


    def quit(self):                           
        self.destroy()
        
if __name__ == '__main__':   
    loginscreen = LoginScreen(None)
    loginscreen.title('Login')
    loginscreen.mainloop()
    rusername, rpassword, password = loginscreen.therusername, loginscreen.therpassword, loginscreen.thepassword
    browsescreen = BrowseScreen(None, rusername, rpassword, password)
    browsescreen.title('Browse Files')
    browsescreen.mainloop()

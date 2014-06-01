reddit_storage
============

Experimental program that uses reddit as encrypted cloud storage.

How it works in a nutshell:

1. It takes the file and a password you gave it, and encrypts the file with AES.
2. It hashes the encrypted file into a string of characters.
3. This string gets broken up into chunks that are 9995 characters long(Reddit comments can only be 10,000 characters long)
4. It creates a new post with the filename as the title and the filesize as the OP text.
5. It uploads each chunk of the encrypted file a separate comment, adding a "#-" at the beggining of each chunk so that we can put it back together in the right order.

When you want to download your file again, it just reverses this process. You can see an example of an uploaded file here - [SystemInfo.tar.gz](http://www.reddit.com/r/6861796465/comments/26wz23/systeminfotargz/).

The subreddit that your files get uploaded to depends on your username - the program hashes your username and then grabs the first 10 characters of that hash(Reddit has subreddit length limitations) as the name of your new subreddit.  

This is just an fun experiment, so don't use this for anything important. To avoid putting stress on Reddits servers over a little project, file uploads are capped at 1MB. This comes out to around 200 comments. Please don't bog down Reddits servers by trying to actually use this thing for serious cloud storage.

Thanks to [Eli Bendersky](http://eli.thegreenplace.net/) for the encryption part of the code!

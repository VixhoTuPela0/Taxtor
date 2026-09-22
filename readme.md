
# Taxtor

An app made for my dad so he can keep the receipts and organize them. Detects your position, if he thinks you bought something, gives you a notification and asks you to save it, you can do it all from the phone but also can go take a look from a webserver

## Funciones
- Account systems (Commit 1/2) Ready
- Save receipts (Commit 3) Ready
- upload photos, dates, which card... (Commit 3) Ready
- export a backup with excel and the receipts pics

All that is coming soon. At the momnt i'm writing this, (commit 2) The login system y think is finished, with a functional login and register, cookies, etc....
## Updates
### Commit 1
The register system is done, with a register fetch made with FastApi, a basic website for register, and storing all the data with SQLite
### Commit 2
hashed, after login in, there is a cookie that lives for 7 days. A basic home site for checking if cookies are still alive, even a logout for erasing the session id from your cookies and the db. Also I tried to comment all the codes for keeping this organized because I know how this goes and sooner all will be a mess xD.
### Commit 3
In the commit 3 I'm turning this a public repo so if other people want to use it or help, it would be my pleasure. I try to change all the lines to english but maybe i will forgot someone. The receipts is ready! I added more security, like you cant access sites as add receipts, list them... without login in. For that, i created a function in auth.py that every time a site loads in, it verifies the cookies and session_id. I added the html too so its a little more family friendly.
### Commit 4
Fixed problems with the verification of cookies and redirections. I tried my best and looked all the backend files, added new functions like categories for the receipts, add them, remove them and other new functions. The backend files should be done by now so i will upload this to github for saving my progress!! Next step will be doing the frontend.
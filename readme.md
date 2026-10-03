
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
### Commit 3 Oct
I dont know what commit im on so i will say the date instead. I started a new function the category, you can add categories for classifing and credit cards. If each time you add your receipt its different the db would have difficulties finding all the one that goes together. Instead created categories, each user has his categories and when you are creating the receipt you choose. Also, i created categories for credit cards, Im trying to do a system where you scan the receipt and it can directly pull the info. So for getting it organized i create a C.C category where you only says your last 4 numbers of your C.C and you can give the card a name so it would be easier to recognize and the OCT would assign it directly. This commit is basiclly working on the frontend, Did login register and invitations. Only people invited by mail can register. The css is not really fancy but it works. I will probably work the css and optimizing the code by the last commits.
from telethon import TelegramClient as Client
from telethon import events
from telethon import Button

import aiohttp
import aiofiles
from aiohttp_socks import ProxyConnector
from aioclient import MoodleClientAio
from yarl import URL
from bs4 import BeautifulSoup
from urllib.parse import quote
from random import randint

import asyncio
import os
import re
import time
import cryptg
import zipfile
import urllib
import json
import traceback
from pathlib import Path
from config import*
#aa
api_id = 10181262  #api id
api_hash = "f52b5a057b73b9974eaa7403e04907f0" #api hash
bot_token = Tokenconf
global_token = "88fb32875da08b12bee89d677bf8bca4" #Aqui el token de la uclv

CONFIGS = {}
OWNER = ["JAGB2021"]

def makeuser(usern):
	CONFIGS[usern] = {"user":"--",
	                "passw":"--",
	                "host":"https://eva.uo.edu.cu",
	                "repoid":"4",
	                "zips":"50",
	                "proxy":"❌",
	                "status":"❌"}
	                 
def getusern(usern):
	return CONFIGS[usern]

def outusern(usern):
	del CONFIGS[usern]

def savedata(usern,figs):
	CONFIGS[usern] = figs

def savedb():
	db = open("db.db","w")
	i = 0
	for user in CONFIGS:
		sep = ""
		if i < len(CONFIGS)-1:
			sep = "\n"
		db.write(str(user)+"="+str(CONFIGS[user])+sep)
		i += 1
	db.close()

def loaddb():
	db = open("db.db","r")
	lines = db.read().split("\n")
	db.close()
	for line in lines:
		splitline = line.split("=")
		user = splitline[0]
		data = json.loads(str(splitline[1]).replace("'",'"'))
		CONFIGS[user] = data
	
MSG_START = "Bienvenido\n"
DOWNLOAD_START = "💠Starting Download"
DOWNLOAD_COMPLETE = "✅Descarga Finalizada"
DOWNLOAD_CANCELLED = "Descarga Cancelada"
SPLIT_MSG = "🔃Cortando en partes de {}"
FINDING_TOKEN = "⏏Finding TOKEN"
FINDED_TOKEN = "✔TOKEN Finded "
LOGIN_IN = "❌Fallo al iniciar"
LOGIN_COMPLETED = "✅Login COMPLETED "
UPLOAD_MSG = "⬆ Subiendo...\n\n Nombre: {}"
SERVER_FAIL = "⭕ Problemas desconocidos en el servidor"
	
botclient = Client('bot',api_id=api_id,api_hash=api_hash).start(bot_token=bot_token)

def mydata(username):
	user = getusern(username)
	if user:
		usern = user["user"]
		passw = user["passw"]
		host = user["host"]
		repoid = user["repoid"]
		proxy = user["proxy"]
		zips = user["zips"]
		if proxy != "❌":
			proxy = "✅"
    	
		msg = f"🆔**Sesion:** @{username}\n"
		#g+= f"🛂**User:** {usern}\n"
		#sg+= f"🔑**Pass:** {passw}\n"
		msg+= f"📡**Host:** {host}\n"
		#msg+= f"📓**Repo_ID:**{repoid}\n"
		msg+= f"📚**Zips:** {zips}\n"
		msg+= f"⚡️**Proxy:** {proxy}\n"
		return msg
    
@botclient.on(events.NewMessage)
async def messages(event):
	username = event.message.chat.username
	id = event.message.chat.id
	msg = event.message.text
	
	try:
		loaddb()
	except:pass
	
	try:obt = getusern(username)
	except:obt = None
	if username in OWNER or obt:
		if obt is None:
			makeuser(username)
	else:
		await botclient.send_message(id,"❌No posee acceso❌")
		return
		
	if msg.lower().startswith("/start"):
		await event.reply(MSG_START)
	
	if msg.lower().startswith("/proxy"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await event.reply("❌Fallo en la escritura del comando\n👉/proxy proxy👈.")
		else:
			proxymsg = splitmsg[1]
			proxys = proxyparsed(proxymsg)
			proxy = f"socks5://{proxys}"
			
			user = getusern(username)
			if user:
				user["proxy"] = proxy
				savedata(username,user)
				savedb()
				await event.reply(mydata(username))
	
	if msg.lower().startswith("/zips"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await event.reply("❌Fallo en la escritura del comando\n👉/zips size👈.")
		else:
			zips = splitmsg[1]
			
			user = getusern(username)
			if user:
				user["zips"] = zips
				savedata(username,user)
				savedb()
				await event.reply(mydata(username))
				
	if msg.lower().startswith("/add"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await event.reply("❌Fallo en la escritura del comando\n👉/add usern👈.")
		else:
			if username not in OWNER:
				return
			usuario = splitmsg[1]
			
			makeuser(usuario)
			await event.reply(f"✅ Añadido @{usuario}")
	
	if msg.lower().startswith("/ban"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await event.reply("❌Fallo en la escritura del comando\n👉/ban usern👈.")
		else:
			if username not in OWNER:
				return
			usuario = splitmsg[1]
			
			outusern(usuario)
			await event.reply("❌ Baneado @{usuario}")
		
	if msg.lower().startswith("/mydata"):
		await botclient.send_message(id,mydata(username),link_preview=False)
	

	if msg.lower().startswith("/delete_proxy"):
		user = getusern(username)
		if user:
			user["proxy"] = "❌"
			savedata(username,user)
			message = mydata(username)
			savedb()
			await event.reply(message)
			

	if msg.lower().startswith("https"):
		usern = getusern(username)
		async with aiohttp.ClientSession() as session:
			async with session.get(msg) as response:
				try:
					name = response.content_disposition.filename
				except:
					name = msg.split("/")[-1]
				
				size = int(response.headers.get("content-length"))
				
				message = await botclient.send_message(id,DOWNLOAD_START)
					
				if os.path.exists(username):pass
				else:os.mkdir(username)
				
				pathfull = os.path.join(os.getcwd(),username,name)
				fi = await aiofiles.open(pathfull,"wb")
				chunkcurrent = 0
				starttime = time.time()
				sizee = 0
				async for chunk in response.content.iter_chunked(1024*1024):
					if obt["status"] != "❌":
						break
					chunkcurrent+=len(chunk)
					currenttime = time.time()-starttime
					speed = chunkcurrent/currenttime
					sizee+=len(chunk)
					
					if sizee >= 5242880:
						await progress(chunkcurrent,size,speed,message,name)
						sizee = 0
					await fi.write(chunk)
				fi.close()
				
				if obt["status"] == "❌":
					await botclient.edit_message(message,DOWNLOAD_COMPLETE)
					await upload(pathfull,message,username)
				else:
					await message.edit(DOWNLOAD_CANCELLED)
					obt["status"] = "❌"
					savedb()
	
	if event.message.media:
		
		usern = getusern(username)
		
		name = event.file.name
		if ".txt" in name:
			return
		
		size = event.file.size
		
		message = await botclient.send_message(id,DOWNLOAD_START)
		
		if os.path.exists(username):pass
		else:os.mkdir(username)
		
		pathfull = os.path.join(os.getcwd(),username,name)
		
		fi = open(pathfull,"wb")
		chunkcurrent = 0
		starttime = time.time()
		sizee = 0
		async for chunk in botclient.iter_download(event.message.media,chunk_size=1024*1024):
			if obt["status"] != "❌":
				break
			chunkcurrent+=len(chunk)
			currenttime = time.time()-starttime
			speed = chunkcurrent/currenttime
			sizee+=len(chunk)
			
			if sizee >= 5242880:
				await progress(chunkcurrent,size,speed,message,name)
				sizee = 0
			fi.write(chunk)
		fi.close()
		
		if obt["status"] == "❌":
			await botclient.edit_message(message,DOWNLOAD_COMPLETE)
			await upload(pathfull,message,username)
		else:
			await message.edit(DOWNLOAD_CANCELLED)
			obt["status"] = "❌"
			savedb()
	
async def progress(chunkcurrent,size,speed,message,name):
		#bytesnormalsize = convertbytes(size)
		#bytesnormalcurrent = convertbytes(chunkcurrent)
		#bytesnormalspeed = convertbytes(speed)
		msgprogress = f"⬇ Descargando achivo , sea paciente...\n\n"
		#msgprogress+= f"📦 `Size`: `{bytesnormalsize}`\n\n"
		#msgprogress+= f"💨`Current`: `{bytesnormalcurrent}`\n\n"
		#msgprogress+= f"⚡ `Speed`: `{bytesnormalspeed}/s`"
		try:
			await botclient.edit_message(message,msgprogress)
		except:pass
		
async def upload(path,msg,username):
	Obtener = getusern(username)
	
	zips = Obtener["zips"]
	
	FILE_SIZE = os.path.getsize(path)
	SIZE = 1024*1024*int(zips)
	
	if FILE_SIZE > SIZE:
		await msg.edit(SPLIT_MSG.format(convertbytes(SIZE)))
		files = zipfile.MultiFile(path,SIZE)
		zips = zipfile.ZipFile(files,mode="w",compression=zipfile.ZIP_DEFLATED)
		zips.write(path)
		zips.close()
		files.close()
		FILES = files.files
	else:
		FILES = [path]
	
	if Obtener["proxy"] != "❌":
		conector = ProxyConnector.from_url(Obtener["proxy"])
	else:
		conector = aiohttp.TCPConnector()
		
	async with aiohttp.ClientSession(connector=conector) as Session:
		client = MoodleClientAio(Obtener["host"],Obtener["user"],Obtener["passw"],Obtener["repoid"],Session)
		counter = 0
		while counter <= 20:
			try:
				await msg.edit(FINDING_TOKEN)
				await asyncio.sleep(0.5)
				token = await gettoken(Obtener["host"],Obtener["user"],Obtener["passw"],Session)
				if token:
					await msg.edit(FINDED_TOKEN)
					await asyncio.sleep(0.5)
					links = []
					
					for path in FILES:
						try:
							await msg.edit(UPLOAD_MSG.format(Path(path).name))
						except:pass
						resp = await client.UploadToken(path,token,progress_callback=moodle_upload_progress)
						
						if resp:
							ws = resp.replace("pluginfile.php","webservice/pluginfile.php")
							url = ws+f"?token={token}"
							#shurl = await shorturl(url)
							await botclient.send_message(username,f"✅**Subida Finalizada**\n📌**Nombre:** {Path(path).name}\n📦**Tamaño:** {convertbytes(Path(path).stat().st_size)}\n\n📌**Enlaces**📌\n{url}",link_preview=False)
							links.append(url)
					break
				else:
					links = []
					token = global_token
					for path in FILES:
						try:
							await msg.edit(UPLOAD_MSG.format(Path(path).name))
						except:pass
						resp = await client.UploadToken(path,token,progress_callback=moodle_upload_progress)
						
						if resp:
							ws = resp.replace("pluginfile.php","webservice/pluginfile.php")
							url = ws+f"?token={token}"
							#shurl = await shorturl(url)
							await botclient.send_message(username,f"✅**Subida Finalizada**\n📌**Nombre:** {Path(path).name}\n📦**Tamaño:** {convertbytes(Path(path).stat().st_size)}\n\n📌**Enlaces**📌\n{url}",link_preview=False)
							links.append(url)
						else:
							await msg.edit(LOGIN_IN)
							await asyncio.sleep(0.5)
							links = []
							
							login = await client.Login()
							if login:
								await msg.edit(LOGIN_COMPLETED)
								await asyncio.sleep(0.5)
								for path in FILES:
									try:
										await msg.edit(UPLOAD_MSG.format(Path(path).name))
									except:pass
									resp = await client.UploadDraft(path,progress_callback=moodle_upload_progress)
									if resp:
										url = resp["url"]
										#shurl = await shorturl(url)
										await botclient.send_message(username,f"✅**Subida Finalizada**\n📌**Nombre:** {Path(path).name}\n📦**Tamaño:** {convertbytes(Path(path).stat().st_size)}\n\n📌**Enlaces**📌\n{url}",link_preview=False)
										links.append(url)
					break
			except:
				print(traceback.format_exc())
				counter+= 1
			
		if counter >= 20:
			await msg.edit(SERVER_FAIL)
		else:
			txts = ""
			msg_links = ""
			for link in links:
				#shurl = await shorturl(link)
				txts+=f"{link}\n"
				msg_links+=f"🔗 {url} \n"
			
			txt = open(f"{Path(path).name}.txt","w")
			txt.write(txts)
			txt.close()
			
			await botclient.send_file(username,f"{Path(path).name}.txt")
	
			await botclient.send_message(-1001648620646,"✅Subida Completada por @"+username+"\n📌Nombre: "+Path(path).name+"\n📦Size: "+convertbytes(FILE_SIZE)+"º\n🆔Host: "+Obtener["host"]+"\n\n📌Enlaces📌\n"+msg_links,link_preview=False)
			
			await botclient.send_file(-1001648620646,f"{Path(path).name}.txt")

def moodle_upload_progress(current,size):
	pass
	

async def gettoken(moodle,user,pasw,session):
	query = {"service": "moodle_mobile_app",
             "username": user,
             "password": pasw}
	tokenurl = URL(moodle).with_path("login/token.php").with_query(query)
	try:
		async with session.get(tokenurl) as resp:
			respjson = await resp.json()
			return respjson["token"]
	except KeyError:
		return None
        
def proxyparsed(proxy):
    trans = str.maketrans(
        "@./=#$%&:,;_-|0123456789abcd3fghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ZYXWVUTSRQPONMLKJIHGFEDCBAzyIwvutsrqponmlkjihgf3dcba9876543210|-_;,:&%$#=/.@",
    )
    return str.translate(proxy[::2], trans)
          
def convertbytes(size):
	if size >= 1024 * 1024 * 1024:
		sizeconvert = "{:.2f}".format(size / (1024 * 1024 * 1024))
		normalbytes = f"{sizeconvert}GiB"
	
	elif size >= 1024 * 1024:
		sizeconvert = "{:.2f}".format(size / (1024 * 1024))
		normalbytes = f"{sizeconvert}MiB"
	
	elif size >= 1024:
		sizeconvert = "{:.2f}".format(size / 1024)
		normalbytes = f"{sizeconvert}KiB"
	
	if size < 1024:
		normalbytes = f"{sizeconvert}B"
	
	return normalbytes

@botclient.on(events.CallbackQuery)
async def cancel(event):
	username = event.chat.username
	obt = getusern(username)
	if event.data == b"cancel":
		obt["status"] = "✅"
		savedb()

if __name__ == "__main__":
	try:
		botclient.run_until_disconnected()
	except Exception as exc:
		print(exc)

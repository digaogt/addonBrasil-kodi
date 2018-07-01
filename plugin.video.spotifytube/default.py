#!/usr/bin/python
# -*- coding: utf-8 -*-
###########################################################
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs, os, re, sys
import urllib, urllib2, datetime, time
import json, shutil, random, socket, spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date
addonID = 'plugin.video.spotifytube'
addon   = xbmcaddon.Addon(id=addonID)
icon    = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
fanart  = xbmc.translatePath('special://home/addons/'+addonID+'/fanart.jpg')
iconsp  = xbmc.translatePath('special://home/addons/'+addonID+'/resources/imgs/iconsp.png')
socket.setdefaulttimeout(30)
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
blacklist = addon.getSetting("blacklist").split(',')
infoEnabled  = addon.getSetting("showInfo") == "true"
infoType     = addon.getSetting("infoType")
infoDelay    = int(addon.getSetting("infoDelay"))
infoDuration = int(addon.getSetting("infoDuration"))
itSubCats = addon.getSetting("itSubCats") == "true"
forceVisu = addon.getSetting("forceVisu") == "true"
gensVisu  = str(addon.getSetting("gensVisu"))
plstVisu  = str(addon.getSetting("plstVisu"))
ytAddonURL = addon.getSetting("youtubeAddon")
ytAddonURL = ["plugin://plugin.video.youtube/play/?video_id=", "plugin://plugin.video.bromix.youtube/play/?video_id="][int(ytAddonURL)]
ytApiKey = "AIzaSyARx3HWm6ScnCPyVUpAvGNQ-OugHv3Mtxs"
userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', userAgent)]
if not os.path.isdir(addonUserDataFolder) : os.mkdir(addonUserDataFolder)
dTT = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M").replace(":","%3A")
def menu():
		addDir("Top Listas" , "http://api.tunigo.com/v3/space/toplists?region=br&page=0&per_page=100&platform=web", "getplaylists", "")
		addDir("Gêneros"    , "http://api.tunigo.com/v3/space/genres?region=br&per_page=1000&platform=web", "getgeneros", "")
		addDir("Destaques"  , "http://api.tunigo.com/v3/space/featured-playlists?region=br&page=0&per_page=50&dt="+dTT+"%3A00&platform=web", "getplaylists", "")
		addDir("Lançamentos", "http://api.tunigo.com/v3/space/new-releases?region=br&page=0&per_page=500&platform=web", "getlancamentos", "")
		if forceVisu : setViewMenu()
		
def getGeneros(url):
		conteudo = opener.open(url).read()
		conteudo = json.loads(conteudo)
		gens = conteudo['items']
		for gen in gens:
				idG = gen['genre']['templateName']
				
				try    : imgG = gen['genre']['iconImageUrl']
				except : imgG = ""
				
				titG = gen['genre']['name'].encode('utf-8')
				
				if titG.strip().lower() != "top lists":
						addDir(titG, "http://api.tunigo.com/v3/space/"+idG+"?region=br&page=0&per_page=100&platform=web", "getplaylists", imgG)
						
		if forceVisu : setViewGens()
		
def getPlaylists(url):
		conteudo = opener.open(url).read()
		conteudo = json.loads(conteudo)
		
		plists = conteudo['items']
		
		for pl in plists:
				urlP = pl['playlist']['uri'].encode('utf-8')
				
				try    : imgP = "http://d3rt1990lpmkn.cloudfront.net/300/"+pl['playlist']['image']
				except : imgP = ""
				
				titP  = pl['playlist']['title'].encode('utf-8')
				descP = pl['playlist']['description'].encode('utf-8')
				
				addAutoPlayDir(titP, urlP, "getvideos", imgP, descP, "browse")
				
		pp    = re.compile('page=(.+?)&per_page=(.+?)&', re.DOTALL).findall(url)
		cPage = int(pp[0][0])
		pPage = int(pp[0][1])
		nPage = cPage+1
		
		if nPage*pPage < conteudo['totalItems']:
				addDir('Próxima Página >>>', url.replace("page="+str(cPage),"page="+str(nPage)), "getplaylists", "")
		
		if forceVisu : setViewPlst()
def getLancamentos(url):
		conteudo = opener.open(url).read()
		conteudo = json.loads(conteudo)
		
		plists = conteudo['items']
		
		for pl in plists:
				urlP = pl['release']['uri'].encode('utf-8')
				
				try    : imgP = "http://d3rt1990lpmkn.cloudfront.net/300/"+pl['release']['image']
				except : imgP = ""
				
				albP  = pl['release']['albumName'].encode('utf-8')
				artP  = pl['release']['artistName'].encode('utf-8')
				titP = artP + ' -' + albP
				
				addAutoPlayDir(titP, urlP, "getvideos", imgP, "", "browse")
				
		pp    = re.compile('page=(.+?)&per_page=(.+?)&', re.DOTALL).findall(url)
		cPage = int(pp[0][0])
		pPage = int(pp[0][1])
		nPage = cPage+1
		
		if nPage*pPage < conteudo['totalItems']:
				addDir('Próxima Página >>>', url.replace("page="+str(cPage),"page="+str(nPage)), "getplaylists", "")
		
		if forceVisu : setViewPlst()

def generate_token():
        credentials = SpotifyClientCredentials(client_id='4fe3fecfe5334023a1472516cc99d805', client_secret='0f02b7c483c04257984695007a4a8d5c')
        token = credentials.get_access_token()
        return spotipy.Spotify(auth=token)

def getVideos(type, url, limit):
		if type == "play":
				musicVideos = []
				playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
				playlist.clear()
		spotify = generate_token()
		username = url.split(':')[2]
		playList_id = url.split(':')[4]
		playlist = spotify.user_playlist(user=username, playlist_id=playList_id)["tracks"]["items"]
		lenght = len(playlist)
		pos = 1
		for i in range(lenght):
				artista = playlist[i]['track']['album']['artists'][0]['name'].encode('utf-8')

				titulo = playlist[i]['track']['name'].encode('utf-8')

				titV = doLimpa(artista + " - " + titulo)

				try    : imgV = playlist[i]['track']['album']['images'][0]['url']
				except : imgV = ""
				
				filtro = False
				
				for entry2 in blacklist:
						if entry2.strip().lower() and entry2.strip().lower() in titV.lower():
								filtro = True
								
				if filtro : continue
				
				if type=="browse" : addLink(titV, titV.replace(" - ", " "), "playvideo", imgV)
				else:
						urlV = "plugin://"+addonID+"/?url="+urllib.quote_plus(titV.replace(" - ", " "))+"&mode=playvideo"
						
						musicVideos.append([titV, urlV, imgV])
						
						if limit and int(limit)==pos : break
						
						pos += 1
						
		if type=="browse":
				if forceVisu : setViewPlst()
		else:
				random.shuffle(musicVideos)
				
				for t, u, i in musicVideos:
						listitem = xbmcgui.ListItem(t, thumbnailImage=i)
						playlist.add(u, listitem)
						
				xbmc.Player().play(playlist)
def playVideo(title):
    try:
				ytID = getYTID(title)
				
				url = ytAddonURL + ytID
				
				listitem = xbmcgui.ListItem(path=url)
				
				xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
				
				if infoEnabled : showInfo()
    except:
        pass
def getYTID(title):
		titYT  = urllib.quote_plus(title.lower())
		urlYT  = "https://www.googleapis.com/youtube/v3/search?part=snippet&max-results=1&order=relevance&q=%s&key=%s" % (titYT, ytApiKey)
		contYT = opener.open(urlYT).read()
		ytID   = re.findall('"videoId": "(.*?)"',contYT,re.S)[0]
		return ytID
def queueVideo(url, name):
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		listitem = xbmcgui.ListItem(name)
		playlist.add(url, listitem)        
def showInfo():
    count = 0
		
    while not xbmc.Player().isPlaying():
        xbmc.sleep(200)
				
        if count == 50 : break
				
        count += 1
				
    xbmc.sleep(infoDelay*1000)
		
    if infoType == "0":
        xbmc.executebuiltin('XBMC.ActivateWindow(12901)')
        xbmc.sleep(infoDuration*1000)
        xbmc.executebuiltin('XBMC.ActivateWindow(12005)')
				
    elif infoType == "1":
        siTit = 'Tocando Agora:'
        siVid = xbmc.getInfoLabel('VideoPlayer.Title').replace(","," ")
        siImg = xbmc.getInfoImage('VideoPlayer.Cover')
				
        xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % (siTit, siVid, infoDuration*1000, siImg))
def doLimpa(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title
		
def setViewMenu() :
		opcao = addon.getSetting('menuVisu')
		
		if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
		elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
		
def setViewGens() :
		opcao = addon.getSetting('gensVisu')
		
		if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
		elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
		
def setViewPlst() :
		opcao = addon.getSetting('plstVisu')
		if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
		elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
		
def addLink(name, url, mode, iconimage):
		u   = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
		ok  = True
		liz = xbmcgui.ListItem(name, iconImage=iconsp, thumbnailImage=iconimage)
		liz.setInfo(type="Video", infoLabels={"Title": name})
		liz.setProperty('fanart_image', fanart)
		liz.setProperty('IsPlayable', 'true')
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
		return ok
def addDir(name, url, mode, iconimage="", description="", type="", limit=""):
		u   = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
		ok  = True
		liz = xbmcgui.ListItem(name, iconImage=iconsp, thumbnailImage=iconimage)
		
		liz.setProperty('fanart_image', fanart)
		liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
		
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
		
		return ok
def addAutoPlayDir(name, url, mode, iconimage="", description="", type="", limit=""):
		u   = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
		ok  = True
		liz = xbmcgui.ListItem(name, iconImage=iconsp, thumbnailImage=iconimage)
		
		liz.setProperty('fanart_image', fanart)
		liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
		
		entries = []
		entries.append(("Autoplay Todos", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=)',))
		
		liz.addContextMenuItems(entries)
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
		return ok
		
def getParams(parameters):
		paramDict = {}
		if parameters : 
				paramPairs = parameters[1:].split("&")
				
				for paramsPair in paramPairs:
						paramSplits = paramsPair.split('=')
						
						if (len(paramSplits)) == 2 : paramDict[paramSplits[0]] = paramSplits[1]
						
		return paramDict
params    = getParams(sys.argv[2])
mode      = urllib.unquote_plus(params.get('mode', ''))
url       = urllib.unquote_plus(params.get('url', ''))
name      = urllib.unquote_plus(params.get('name', ''))
iconimage = urllib.unquote_plus(params.get('iconimage', ''))
type      = urllib.unquote_plus(params.get('type', ''))
limit     = urllib.unquote_plus(params.get('limit', ''))
if   mode == ''               : menu()
elif mode == 'getgeneros'     : getGeneros(url)
elif mode == 'getplaylists'   : getPlaylists(url)
elif mode == 'getlancamentos' : getLancamentos(url)
elif mode == 'getvideos'      : getVideos(type, url, limit)
elif mode == 'playvideo'      : playVideo(url)
elif mode == 'queueVideo'     : queueVideo(url, name)
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

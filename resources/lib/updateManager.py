# -*- coding: UTF-8 -*-

import os, base64, sys
import json
import requests
from requests.auth import HTTPBasicAuth

import xbmc, xbmcvfs
from xbmc import LOGDEBUG, LOGERROR
from xbmcgui import Dialog
from xbmcaddon import Addon

if sys.version_info[0] == 2:
    from xbmc import LOGNOTICE as LOGINFO
    from xbmc import translatePath
    _ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s')).decode('utf-8')
    _ADDON_DATA_DIR = translatePath(os.path.join('special://home/userdata/addon_data', '%s')).decode('utf-8')
else:
    from xbmc import LOGINFO
    from xbmcvfs import translatePath
    _ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s'))
    _ADDON_DATA_DIR = translatePath(os.path.join('special://home/userdata/addon_data', '%s'))   # plugin_id

## Android K18 ZIP Fix.
if xbmc.getCondVisibility('system.platform.android') and int(xbmc.getInfoLabel('System.BuildVersion')[:2]) <= 18:
    import fixetzipfile as zipfile
else:
    import zipfile

# Text/Überschrift im Dialog
PLUGIN_NAME = Addon().getAddonInfo('name')
PLUGIN_ID = Addon().getAddonInfo('id')

# Update Funktion Github
def Update(username, plugin_id, repo, branch, token, silent):
    REMOTE_PLUGIN_COMMITS = "https://api.github.com/repos/%s/%s/commits/%s" % (username, repo, branch)
    REMOTE_PLUGIN_DOWNLOADS = "https://api.github.com/repos/%s/%s/zipball/%s" % (username, repo, branch)
    try:
        #auth = HTTPBasicAuth(username, base64.b64decode(token))
        try:
            auth = HTTPBasicAuth(username, token)
        except:
            return 'auth-error'
        try:
            xbmc.log('%s - Search for update ' % plugin_id, LOGINFO)
            ADDON_PATH = _ADDON_PATH % plugin_id
            ADDON_DATA_DIR = _ADDON_DATA_DIR % plugin_id

            if not os.path.exists(ADDON_DATA_DIR): os.mkdir(ADDON_DATA_DIR)

            LOCAL_PLUGIN_VERSION = os.path.join(ADDON_DATA_DIR, "update_sha")
            LOCAL_FILE_NAME_PLUGIN = os.path.join(ADDON_DATA_DIR, 'update-' + plugin_id + '.zip')

            commitXML = _getXmlString(REMOTE_PLUGIN_COMMITS, auth)
            if commitXML == 'auth-error': return 'auth-error'
            if commitXML:
                isTrue = commitUpdate(commitXML, LOCAL_PLUGIN_VERSION, REMOTE_PLUGIN_DOWNLOADS, ADDON_PATH, plugin_id,
                                      LOCAL_FILE_NAME_PLUGIN, silent, auth)
                if isTrue == True:
                    xbmc.log('%s - Update successful.' % plugin_id, LOGINFO)
                    ##if silent == False: Dialog().ok(PLUGIN_NAME, plugin_id + " - Update erfolgreich.")
                    return True
                elif isTrue == None:
                    xbmc.log('%s - no new update ' % plugin_id, LOGINFO)
                    ##if silent == False: Dialog().ok(PLUGIN_NAME, plugin_id + " - Kein Update verfügbar.")
                    return None

            xbmc.log('%s - Update error ' % plugin_id, LOGERROR)
            if silent == False: Dialog().ok(PLUGIN_NAME, 'Fehler 2 beim Update vom ' + plugin_id)
            return False
        except:
            xbmc.log('%s - Update error ' % plugin_id, LOGERROR)
            if silent == False: Dialog().ok(PLUGIN_NAME, 'Fehler beim Update vom ' + plugin_id + '\n Keine Internetverbindung zum Git!')
            return False
    except:
        xbmc.log('%s - Update error - Update-Key' % plugin_id, LOGERROR)
        if silent == False: Dialog().ok(PLUGIN_NAME, 'Fehler beim Update von  [COLOR red]' + plugin_id + '[/COLOR]\nUpdate-Key abgelaufen oder ungültig!')
        return 'auth-error'

def commitUpdate(onlineFile, offlineFile, downloadLink, LocalDir, plugin_id, localFileName, silent, auth):
    try:
        jsData = json.loads(onlineFile)
        if not os.path.exists(offlineFile) or open(offlineFile).read() != jsData['sha']:
            xbmc.log('%s - start update ' % plugin_id, LOGINFO)
            isTrue = doUpdate(LocalDir, downloadLink, plugin_id, localFileName, auth)
            if isTrue == True:
                try:
                    open(offlineFile, 'w').write(jsData['sha'])
                    return True
                except:
                    return False
            else:
                return False
        else:
            return None

    except Exception as e:
        os.remove(offlineFile)
        xbmc.log("RateLimit reached")
        return False
        
def delete_folder_contents(path):
    for root, dirs, files in os.walk(path):
        if ".git" in root or "pydev" in root or ".idea" in root: continue
        for filename in files: xbmcvfs.delete(os.path.join(path, filename))
        for directory in dirs:
            delete_folder_contents(os.path.join(path, directory))
            xbmc.sleep(80)
            xbmcvfs.rmdir(os.path.join(path, directory))

def doUpdate(LocalDir, REMOTE_PATH, Title, localFileName, auth):
    try:
        response = requests.get(REMOTE_PATH, auth=auth)  # verify=False,
                                
        # Open our local file for writing
        # with open(localFileName,"wb") as local_file:
        # local_file.write(f.read())
        if response.status_code == 200:
            open(localFileName, "wb").write(response.content)
        else:
            return False
        updateFile = zipfile.ZipFile(localFileName)
        delete_folder_contents(LocalDir)
        for index, n in enumerate(updateFile.namelist()):
            if n[-1] != "/":
                dest = os.path.join(LocalDir, "/".join(n.split("/")[1:]))
                destdir = os.path.dirname(dest)
                if not os.path.isdir(destdir):
                    os.makedirs(destdir)
                data = updateFile.read(n)
                if os.path.exists(dest):
                    os.remove(dest)
                f = open(dest, 'wb')
                f.write(data)
                f.close()
        updateFile.close()
        os.remove(localFileName)
#
        #xbmc.executebuiltin("UpdateLocalAddons()")
        return True
    except:
        xbmc.log("do Update not possible due download error")
        return False
        

def _getXmlString(xml_url, auth):
    try:
        xmlString = requests.get(xml_url, auth=auth).content  # verify=False,
        if "sha" in json.loads(xmlString):
            return xmlString
        else:
            xbmc.log("Update-URL incorrect or bad credentials")
            return 'auth-error'
    except Exception as e:
        xbmc.log(e)

def log(msg, level=LOGDEBUG):
    DEBUGPREFIX = '[ ' + PLUGIN_ID + ' DEBUG ]'
    # override message level to force logging when addon logging turned on
    level = LOGINFO
    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))
        xbmc.log('%s: %s' % (DEBUGPREFIX, msg), level)
    except Exception as e:
        try:
            xbmc.log('Logging Failure: %s' % (e), level)
        except:
            pass  # just give up

# todo Verzeichnis packen -für zukünftige Erweiterung "Backup"
def zipfolder(foldername, target_dir):
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
    zipobj.close()

def lookForUpdates(silent):
    import xbmcaddon

    plugin_id = "plugin.video.xstream"

    repo = xbmcaddon.Addon().getSetting('update.repo')

    if repo == '':
        repo = 'plugin.video.xstream'

    branch = xbmcaddon.Addon().getSetting('update.branch')
    
    #owner of the repository used for updates
    username = xbmcaddon.Addon().getSetting('update.user')

    if username == '':
        username = 'streamxstream'

    #a GitHub token used on private repositories or those that requiere special rights
    token = xbmcaddon.Addon().getSetting('update.token')

    status = Update(username, plugin_id, repo, branch, token, silent)

    if status == True: infoDialog("Update abgeschlossen", sound=False, icon='INFO', time=3000)
    if status == False: infoDialog("Update mit Fehler beendet", sound=True, icon='ERROR')
    if silent == False and status == None: infoDialog("Keine neuen Updates verfügbar", sound=False, icon='INFO', time=3000)

def infoDialog(message, heading='', icon='', time=5000, sound=False):
    if heading == '':
        import xbmcaddon
        heading = xbmcaddon.Addon().getAddonInfo('name')

    import xbmcgui
    if icon == '':
        icon = xbmcaddon.Addon().getAddonInfo('icon')
    elif icon == 'INFO':
        icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR':
        icon = xbmcgui.NOTIFICATION_ERROR

    xbmcgui.Dialog().notification(heading, message, icon, time, sound=sound)
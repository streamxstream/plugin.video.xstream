# -*- coding: utf-8 -*-

import sys, os, json, re, xbmc, xbmcaddon, xbmcgui
from xbmc import LOGDEBUG, LOGERROR

AddonName = xbmcaddon.Addon().getAddonInfo('name')

if sys.version_info[0] == 2:
    from xbmc import translatePath

    NIGHTLY_VERSION_CONTROL = os.path.join(translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'), "update_sha")
    ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s')).decode('utf-8')
else:
    from xbmcvfs import translatePath

    NIGHTLY_VERSION_CONTROL = os.path.join(translatePath(xbmcaddon.Addon().getAddonInfo('profile')), "update_sha")
    ADDON_PATH = translatePath(os.path.join('special://home/addons/', '%s'))

def enableAddon(ADDONID):
    struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
    if 'error' in struktur or struktur["result"]["addon"]["enabled"] != True:
        count = 0
        while True:
            if count == 5: break
            count += 1
            xbmc.executebuiltin('EnableAddon(%s)' % (ADDONID))
            xbmc.executebuiltin('SendClick(11)')
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid":"%s", "enabled":true}}' % ADDONID)
            xbmc.sleep(500)
            try:
                struktur = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params": {"addonid":"%s", "properties": ["enabled"]}}' % ADDONID))
                if struktur["result"]["addon"]["enabled"] == True: break
            except:
                pass

def checkDependence(ADDONID):
    isdebug = True
    if isdebug: xbmc.log(__name__ + ' - %s - checkDependence ' % ADDONID, xbmc.LOGDEBUG)
    try:
        addon_xml = os.path.join(ADDON_PATH % ADDONID, 'addon.xml')
        with open(addon_xml, 'rb') as f:
            xml = f.read()
        pattern = '(import.*?addon[^/]+)'
        allDependence = re.findall(pattern, str(xml))
        # if isdebug: log_utils.log(__name__ + '%s - allDependence ' % str(allDependence), log_utils.LOGDEBUG)
        for i in allDependence:
            try:
                if 'optional' in i or 'xbmc.python' in i: continue
                pattern = 'import.*?"([^"]+)'
                IDdoADDON = re.search(pattern, i).group(1)
                if os.path.exists(ADDON_PATH % IDdoADDON) == True and xbmcaddon.Addon().getSetting('enforceUpdate') != 'true':
                    enableAddon(IDdoADDON)
                else:
                    xbmc.executebuiltin('InstallAddon(%s)' % (IDdoADDON))
                    xbmc.executebuiltin('SendClick(11)')
                    enableAddon(IDdoADDON)
            except:
                pass
    except Exception as e:
        xbmc.log(__name__ + '  %s - Exception ' % e, LOGERROR)


if os.path.isfile(NIGHTLY_VERSION_CONTROL) == False or xbmcaddon.Addon().getSetting('DevUpdateAuto') == 'true' or xbmcaddon.Addon().getSetting('enforceUpdate') == 'true':
    from resources.lib import updateManager
    updateManager.lookForUpdates(True)

# "setting.xml" wenn notwendig Indexseiten aktualisieren
try:
    if xbmcaddon.Addon().getSetting('newSetting') == 'true':
        from resources.lib.handler.pluginHandler import cPluginHandler

        cPluginHandler().getAvailablePlugins()
except Exception:
    pass

checkDependence('plugin.video.xstream')
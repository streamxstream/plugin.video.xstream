# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.tools import logger
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
import sys, xbmc, xbmcgui

try:
    import resolveurl as resolver
except ImportError:
    xbmcgui.Dialog().ok('ResolveUrl Error', 'Bitte installiere ResolveURL um Videos ansehen zu können')


def run():
    parseUrl()


def viewInfo(params):
    from resources.lib.tmdbinfo import WindowsBoxes
    parms = ParameterHandler()
    sCleanTitle = params.getValue('searchTitle')
    sMeta = parms.getValue('sMeta')
    sYear = parms.getValue('sYear')
    WindowsBoxes(sCleanTitle, sCleanTitle, sMeta, sYear)


def parseUrl():
    if xbmc.getInfoLabel('Container.PluginName') == 'plugin.video.osmosis':
        sys.exit()
    params = ParameterHandler()
    logger.info(params.getAllParameters())
    # If no function is set, we set it to the default "load" function
    if params.exist('function'):
        sFunction = params.getValue('function')
        if sFunction == 'spacer':
            return True
        elif sFunction == 'clearCache':
            cRequestHandler('dummy').clearCache()
            return
        elif sFunction == 'viewInfo':
            viewInfo(params)
            return
        elif sFunction == 'searchAlter':
            searchAlter(params)
            return
        elif sFunction == 'searchTMDB':
            searchTMDB(params)
            return
        elif sFunction == 'manualUpdate':
            from resources.lib import updateManager
            updateManager.lookForUpdates(False)
            return
    elif params.exist('remoteplayurl'):
        try:
            #import urlresolver as resolver
            remotePlayUrl = params.getValue('remoteplayurl')
            sLink = resolver.resolve(remotePlayUrl)
            if sLink:
                xbmc.executebuiltin('PlayMedia(' + sLink + ')')
            else:
                logger.info("Could not play remote url '%s'" % sLink)
        except resolver.resolver.ResolverError as e:
            logger.error('ResolverError: %s' % e)
        return
    else:
        sFunction = 'load'

    # Test if we should run a function on a special site
    if not params.exist('site'):
        xbmc.executebuiltin('RunPlugin(%s?function=clearCache)' % sys.argv[0])
        # As a default if no site was specified, we run the default starting gui with all plugins
        showMainMenu(sFunction)
        return
    sSiteName = params.getValue('site')
    if params.exist('playMode'):
        from resources.lib.gui.hoster import cHosterGui
        url = False
        playMode = params.getValue('playMode')
        isHoster = params.getValue('isHoster')
        url = params.getValue('url')
        manual = params.exist('manual')

        if cConfig().getSetting('hosterSelect') == 'Auto' and playMode != 'jd' and playMode != 'jd2' and playMode != 'pyload' and not manual:
            cHosterGui().streamAuto(playMode, sSiteName, sFunction)
        else:
            cHosterGui().stream(playMode, sSiteName, sFunction, url)
        return
    logger.info("Call function '%s' from '%s'" % (sFunction, sSiteName))
    # If the hoster gui is called, run the function on it and return
    if sSiteName == 'cHosterGui':
        showHosterGui(sFunction)
    # If global search is called
    elif sSiteName == 'globalSearch':
        searchterm = False
        if params.exist('searchterm'):
            searchterm = params.getValue('searchterm')
        searchGlobal(searchterm)
    elif sSiteName == 'xStream':
        oGui = cGui()
        oGui.openSettings()
        oGui.updateDirectory()
    # If the resolver settings are called
    elif sSiteName == 'resolver':
        #import urlresolver as resolver
        resolver.display_settings()
    # If UpdateManager are called (manual update)
    elif sSiteName == 'manualUpdate':
        from resources.lib import updateManager
        updateManager.lookForUpdates(False)
    elif sSiteName == 'settings':
        oGui = cGui()
        for folder in settingsGuiElements():
            oGui.addFolder(folder)
        oGui.setEndOfDirectory()
    else:
        # Else load any other site as plugin and run the function
        plugin = __import__(sSiteName, globals(), locals())
        function = getattr(plugin, sFunction)
        function()


def showMainMenu(sFunction):
    oGui = cGui()
    if cConfig().getSetting('GlobalSearchPosition') == 'true':
        oGui.addFolder(globalSearchGuiElement())
    oPluginHandler = cPluginHandler()
    aPlugins = oPluginHandler.getAvailablePlugins()
    if not aPlugins:
        logger.info('No activated Plugins found')
        # Open the settings dialog to choose a plugin that could be enabled
        oGui.openSettings()
        oGui.updateDirectory()
    else:
        # Create a gui element for every plugin found
        for aPlugin in sorted(aPlugins, key=lambda k: k['id']):
            oGuiElement = cGuiElement()
            oGuiElement.setTitle(aPlugin['name'])
            oGuiElement.setSiteName(aPlugin['id'])
            oGuiElement.setFunction(sFunction)
            if 'icon' in aPlugin and aPlugin['icon']:
                oGuiElement.setThumbnail(aPlugin['icon'])
            oGui.addFolder(oGuiElement)
        if cConfig().getSetting('GlobalSearchPosition') == 'false':
            oGui.addFolder(globalSearchGuiElement())

    if cConfig().getSetting('SettingsFolder') == 'true':
        # Create a gui element for Settingsfolder
        oGuiElement = cGuiElement()
        oGuiElement.setTitle(cConfig().getLocalizedString(30041))
        oGuiElement.setSiteName('settings')
        oGuiElement.setFunction('showSettingsFolder')
        oGuiElement.setThumbnail('DefaultAddonService.png')
        oGui.addFolder(oGuiElement)
    else:
        for folder in settingsGuiElements():
            oGui.addFolder(folder)
    # ka add - Create a gui element for updateManager
    #if cConfig().getSetting('DevUpdateAuto') == 'false':
    oGuiElement = cGuiElement()
    oGuiElement.setTitle(cConfig().getLocalizedString(30045))
    oGuiElement.setSiteName('manualUpdate')
    oGuiElement.setFunction(sFunction)
    oGuiElement.setThumbnail('DefaultAddonProgram.png')
    oGui.addFolder(oGuiElement)
    oGui.setEndOfDirectory()


def settingsGuiElements():
    # Create a gui element for addon settings
    oGuiElement = cGuiElement()
    oGuiElement.setTitle(cConfig().getLocalizedString(30042))
    oGuiElement.setSiteName('xStream')
    oGuiElement.setFunction('display_settings')
    oGuiElement.setThumbnail('DefaultAddonProgram.png')
    xStreamSettings = oGuiElement

    # Create a gui element for resolver settings
    oGuiElement = cGuiElement()
    oGuiElement.setTitle(cConfig().getLocalizedString(30043))
    oGuiElement.setSiteName('resolver')
    oGuiElement.setFunction('display_settings')
    oGuiElement.setThumbnail('DefaultAddonRepository.png')
    resolveurlSettings = oGuiElement
    return xStreamSettings, resolveurlSettings


def globalSearchGuiElement():
    # Create a gui element for global search
    oGuiElement = cGuiElement()
    oGuiElement.setTitle(cConfig().getLocalizedString(30040))
    oGuiElement.setSiteName('globalSearch')
    oGuiElement.setFunction('globalSearch')
    oGuiElement.setThumbnail('DefaultAddonWebSkin.png')
    return oGuiElement


def showHosterGui(sFunction):
    from resources.lib.gui.hoster import cHosterGui
    oHosterGui = cHosterGui()
    function = getattr(oHosterGui, sFunction)
    function()
    return True


def searchGlobal(sSearchText=False):
    import threading
    oGui = cGui()
    oGui.globalSearch = True
    oGui._collectMode = True
    if not sSearchText:
        sSearchText = oGui.showKeyBoard()
    if not sSearchText: return True
    aPlugins = []
    aPlugins = cPluginHandler().getAvailablePlugins()
    dialog = xbmcgui.DialogProgress()
    dialog.create('xStream', 'Searching...')
    numPlugins = len(aPlugins)
    threads = []
    for count, pluginEntry in enumerate(aPlugins):
        if not pluginEntry['globalsearch']:
            continue
        dialog.update((count + 1) * 50 // numPlugins, 'Searching: ' + str(pluginEntry['name']) + '...')
        if dialog.iscanceled(): return
        if sys.version_info[0] == 2:
            logger.info('Searching for %s at %s' % (sSearchText.decode('utf-8'), pluginEntry['id']))
        else:
            logger.info('Searching for %s at %s' % (sSearchText, pluginEntry['id']))

        t = threading.Thread(target=_pluginSearch, args=(pluginEntry, sSearchText, oGui), name=pluginEntry['name'])
        threads += [t]
        t.start()
    for count, t in enumerate(threads):
        if dialog.iscanceled(): return
        t.join()
        dialog.update((count + 1) * 50 // numPlugins + 50, t.getName() + ' returned')
    dialog.close()
    # deactivate collectMode attribute because now we want the elements really added
    oGui._collectMode = False
    total = len(oGui.searchResults)
    dialog = xbmcgui.DialogProgress()
    dialog.create('xStream', 'Gathering info...')
    for count, result in enumerate(sorted(oGui.searchResults, key=lambda k: k['guiElement'].getSiteName()), 1):
        if dialog.iscanceled(): return
        oGui.addFolder(result['guiElement'], result['params'], bIsFolder=result['isFolder'], iTotal=total)
        dialog.update(count * 100 // total, str(count) + ' of ' + str(total) + ': ' + result['guiElement'].getTitle())
    dialog.close()
    oGui.setView()
    oGui.setEndOfDirectory()
    return True


def searchAlter(params):
    searchTitle = params.getValue('searchTitle')
    searchImdbId = params.getValue('searchImdbID')
    searchYear = params.getValue('searchYear')
    import threading
    oGui = cGui()
    oGui.globalSearch = True
    oGui._collectMode = True
    aPlugins = []
    aPlugins = cPluginHandler().getAvailablePlugins()
    dialog = xbmcgui.DialogProgress()
    dialog.create('xStream', "Searching...")
    numPlugins = len(aPlugins)
    threads = []
    for count, pluginEntry in enumerate(aPlugins):
        if dialog.iscanceled(): return
        dialog.update((count + 1) * 50 // numPlugins, 'Searching: ' + str(pluginEntry['name']) + '...')
        if sys.version_info[0] == 2:
            logger.info('Searching for ' + searchTitle + pluginEntry['id'].encode('utf-8'))
        else:
            logger.info('Searching for ' + searchTitle + pluginEntry['id'])
        t = threading.Thread(target=_pluginSearch, args=(pluginEntry, searchTitle, oGui), name=pluginEntry['name'])
        threads += [t]
        t.start()
    for count, t in enumerate(threads):
        t.join()
        if dialog.iscanceled(): return
        dialog.update((count + 1) * 50 // numPlugins + 50, t.getName() + ' returned')
    dialog.close()
    # check results, put this to the threaded part, too
    filteredResults = []
    for result in oGui.searchResults:
        guiElement = result['guiElement']
        logger.info('Site: %s Titel: %s' % (guiElement.getSiteName(), guiElement.getTitle()))
        if searchTitle not in guiElement.getTitle():
            continue
        if guiElement._sYear and searchYear and guiElement._sYear != searchYear: continue
        if searchImdbId and guiElement.getItemProperties().get('imdbID', False) and guiElement.getItemProperties().get('imdbID', False) != searchImdbId: continue
        filteredResults.append(result)
    oGui._collectMode = False
    total = len(filteredResults)
    for result in sorted(filteredResults, key=lambda k: k['guiElement'].getSiteName()):
        oGui.addFolder(result['guiElement'], result['params'], bIsFolder=result['isFolder'], iTotal=total)
    oGui.setView()
    oGui.setEndOfDirectory()
    xbmc.executebuiltin('Container.Update')
    return True


def searchTMDB(params):
    sSearchText = params.getValue('searchTitle')
    import threading
    oGui = cGui()
    oGui.globalSearch = True
    oGui._collectMode = True
    if not sSearchText: return True
    aPlugins = []
    aPlugins = cPluginHandler().getAvailablePlugins()
    dialog = xbmcgui.DialogProgress()
    dialog.create('xStream', 'Searching...')
    numPlugins = len(aPlugins)
    threads = []
    for count, pluginEntry in enumerate(aPlugins):
        if not pluginEntry['globalsearch']:
            continue
        if dialog.iscanceled(): return
        dialog.update((count + 1) * 50 // numPlugins, 'Searching: ' + str(pluginEntry['name']) + '...')
        if sys.version_info[0] == 2:
            logger.info('Searching for %s at %s' % (sSearchText.decode('utf-8'), pluginEntry['id']))
        else:
            logger.info('Searching for %s at %s' % (sSearchText, pluginEntry['id']))

        t = threading.Thread(target=_pluginSearch, args=(pluginEntry, sSearchText, oGui), name=pluginEntry['name'])
        threads += [t]
        t.start()
    for count, t in enumerate(threads):
        t.join()
        if dialog.iscanceled(): return
        dialog.update((count + 1) * 50 // numPlugins + 50, t.getName() + ' returned')
    dialog.close()
    # deactivate collectMode attribute because now we want the elements really added
    oGui._collectMode = False
    total = len(oGui.searchResults)
    dialog = xbmcgui.DialogProgress()
    dialog.create('xStream', 'Gathering info...')
    for count, result in enumerate(sorted(oGui.searchResults, key=lambda k: k['guiElement'].getSiteName()), 1):
        if dialog.iscanceled(): return
        oGui.addFolder(result['guiElement'], result['params'], bIsFolder=result['isFolder'], iTotal=total)
        dialog.update(count * 100 // total, str(count) + ' of ' + str(total) + ': ' + result['guiElement'].getTitle())
    dialog.close()
    oGui.setView()
    oGui.setEndOfDirectory()
    return True


def _pluginSearch(pluginEntry, sSearchText, oGui):
    try:
        plugin = __import__(pluginEntry['id'], globals(), locals())
        function = getattr(plugin, '_search')
        function(oGui, sSearchText)
    except Exception:
        logger.error(pluginEntry['name'] + ': search failed')
        import traceback
        logger.debug(traceback.format_exc())

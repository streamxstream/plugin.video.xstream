# -*- coding: utf-8 -*-
# Python 3
# Always pay attention to the translations in the menu!

# 2022-12-06 Heptamer - Suchfunktion überarbeitet
# 2022-12-10 suuhm - Erweiterte Metadata Suchfunktion hinzugefügt

import xbmcgui
import time

from operator import truediv
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'serienstream_to'
SITE_NAME = 'SerienStream'
SITE_ICON = 'serienstream.png'
#SITE_GLOBAL_SEARCH = False     # Global search function is thus deactivated!
domain = cConfig().getSetting('serienstream_to-domain') # Domain Auswahl über die xStream Einstellungen möglich
#URL_MAIN = 'https://s.to/'
if domain == "190.115.18.20":
    URL_MAIN = 'http://' + domain
    proxy = 'true'
else:
    URL_MAIN = 'https://' + domain
    proxy = 'false'
URL_SERIES = URL_MAIN + '/serien'
URL_NEW_SERIES = URL_MAIN + '/neu'
URL_NEW_EPISODES = URL_MAIN + '/neue-episoden'
URL_POPULAR = URL_MAIN + '/beliebte-serien'
URL_LOGIN = URL_MAIN + '/login'
URL_SEARCH = URL_MAIN + '/ajax/search'


def load(): # Menu structure of the site plugin
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    username = cConfig().getSetting('serienstream.user')# Username
    password = cConfig().getSetting('serienstream.pass')# Password   
    if username == '' or password == '':                # If no username and password were set, close the plugin!
        xbmcgui.Dialog().ok(cConfig().getLocalizedString(30241), cConfig().getLocalizedString(30264))   # Info Dialog!
    else:
        params.setParam('sUrl', URL_SERIES)
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30518), SITE_IDENTIFIER, 'showAllSeries'), params)# All Series
        params.setParam('sUrl', URL_NEW_SERIES)
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30514), SITE_IDENTIFIER, 'showEntries'), params)  # New Series
        params.setParam('sUrl', URL_NEW_EPISODES)
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30516), SITE_IDENTIFIER, 'showNewEpisodes'), params)  # New Episodes
        params.setParam('sUrl', URL_POPULAR)
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30519), SITE_IDENTIFIER, 'showEntries'), params)  # Popular Series
        params.setParam('sUrl', URL_MAIN)
        params.setParam('sCont', 'catalogNav')
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30517), SITE_IDENTIFIER, 'showValue'), params)    # From A-Z
        params.setParam('sCont', 'homeContentGenresList')
        cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30506), SITE_IDENTIFIER, 'showValue'), params)    # Genre
        if cConfig().getSetting('serienstream_to-advsearch') == 'true':
            cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearchAdv'), params)   # Search
        else:
            cGui().addFolder(cGuiElement(cConfig().getLocalizedString(30520), SITE_IDENTIFIER, 'showSearch'), params)   # Search
        cGui().setEndOfDirectory()


def showValue():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, '<ul[^>]*class="%s"[^>]*>(.*?)<\\/ul>' % params.getValue('sCont'))
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, '<li>\s*<a[^>]*href="([^"]*)"[^>]*>(.*?)<\\/a>\s*<\\/li>')
    if not isMatch:
        cGui().showInfo()
        return

    for sUrl, sName in aResult:
        sUrl = sUrl if sUrl.startswith('http') else URL_MAIN + sUrl
        params.setParam('sUrl', sUrl)
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showAllSeries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False)).request()
    pattern = '<a[^>]*href="(\\/serie\\/[^"]*)"[^>]*>(.*?)</a>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName in aResult:
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons')
        oGuiElement.setMediaType('tvshow')
        params.setParam('sUrl', URL_MAIN + sUrl)
        params.setParam('TVShowTitle', sName)
        oGui.addFolder(oGuiElement, params, True, total)
    if not sGui:
        oGui.setView('tvshows')
        oGui.setEndOfDirectory()
   


def showNewEpisodes(entryUrl=False, sGui=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl:
        entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="col-md-[^"]*"[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>\s*<strong>([^<]+)</strong>\s*<span[^>]*>([^<]+)</span>'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sName, sInfo in aResult:
        sMovieTitle = sName + ' ' + sInfo
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons')
        oGuiElement.setMediaType('tvshow')
        oGuiElement.setTitle(sMovieTitle)
        params.setParam('sUrl', URL_MAIN + sUrl)
        params.setParam('TVShowTitle', sMovieTitle)

        oGui.addFolder(oGuiElement, params, True, total)
    if not sGui:
        oGui.setView('tvshows')
        oGui.setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl:
        entryUrl = params.getValue('sUrl')
    oRequest = cRequestHandler(entryUrl, ignoreErrors=(sGui is not False))
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="col-md-[^"]*"[^>]*>.*?'  # start element
    pattern += '<a[^>]*href="([^"]*)"[^>]*>.*?'  # url
    pattern += '<img[^>]*src="([^"]*)"[^>]*>.*?'  # thumbnail
    pattern += '<h3>(.*?)<span[^>]*class="paragraph-end">.*?'  # title
    pattern += '<\\/div>'  # end element
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        #sThumbnail = URL_MAIN + sThumbnail
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setMediaType('tvshow')
        params.setParam('sUrl', URL_MAIN + sUrl)
        params.setParam('TVShowTitle', sName)
        oGui.addFolder(oGuiElement, params, True, total)
    if not sGui:
        pattern = 'pagination">.*?<a href="([^"]+)">&gt;</a>.*?</a></div>'
        isMatchNextPage, sNextUrl = cParser.parseSingleResult(sHtmlContent, pattern)
        if isMatchNextPage:
            params.setParam('sUrl', sNextUrl)
            oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows')
        oGui.setEndOfDirectory()


def showSeasons():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sTVShowTitle = params.getValue('TVShowTitle')
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()
    pattern = '<div[^>]*class="hosterSiteDirectNav"[^>]*>.*?<ul>(.*?)<\\/ul>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"[^>]*>(.*?)<\\/a>.*?'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p[^>]*data-full-description="(.*?)"[^>]*>')
    isThumbnail, sThumbnail = cParser.parseSingleResult(sHtmlContent, '<div[^>]*class="seriesCoverBox"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*>')
    if isThumbnail:
        if sThumbnail.startswith('/'):
            sThumbnail = URL_MAIN + sThumbnail

    total = len(aResult)
    for sUrl, sName, sNr in aResult:
        isMovie = sUrl.endswith('filme')
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes')
        oGuiElement.setMediaType('season' if not isMovie else 'movie')
        if isThumbnail:
            oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        if not isMovie:
            oGuiElement.setTVShowTitle(sTVShowTitle)
            oGuiElement.setSeason(sNr)
            params.setParam('sSeason', sNr)
        params.setParam('sThumbnail', sThumbnail)
        params.setParam('sUrl', URL_MAIN + sUrl)
        cGui().addFolder(oGuiElement, params, True, total)
    cGui().setView('seasons')
    cGui().setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sUrl = params.getValue('sUrl')
    sTVShowTitle = params.getValue('TVShowTitle')
    sSeason = params.getValue('sSeason')
    sThumbnail = params.getValue('sThumbnail')
    if not sSeason:
        sSeason = '0'
    isMovieList = sUrl.endswith('filme')
    oRequest = cRequestHandler(sUrl)
    sHtmlContent = oRequest.request()
    pattern = '<table[^>]*class="seasonEpisodesList"[^>]*>(.*?)<\\/table>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<tr[^>]*data-episode-season-id="(\d+).*?<a href="([^"]+).*?(?:<strong>(.*?)</strong>.*?)?(?:<span>(.*?)</span>.*?)?<'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        cGui().showInfo()
        return

    isDesc, sDesc = cParser.parseSingleResult(sHtmlContent, '<p[^>]*data-full-description="(.*?)"[^>]*>')
    total = len(aResult)
    for sID, sUrl2, sNameGer, sNameEng in aResult:
        sName = '%d - ' % int(sID)
        sName += sNameGer if sNameGer else sNameEng
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('episode' if not isMovieList else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        if isDesc:
            oGuiElement.setDescription(sDesc)
        if not isMovieList:
            oGuiElement.setSeason(sSeason)
            oGuiElement.setEpisode(int(sID))
            oGuiElement.setTVShowTitle(sTVShowTitle)
        params.setParam('sUrl', URL_MAIN + sUrl2)
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes' if not isMovieList else 'movies')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    sUrl = ParameterHandler().getValue('sUrl')
    sHtmlContent = cRequestHandler(sUrl).request()
    pattern = '<li[^>]*data-lang-key="([^"]+).*?data-link-target="([^"]+).*?<h4>([^<]+)<([^>]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        for sLang, sUrl, sName, sQualy in aResult:
            if sLang == '1':
                sLang = 'Deutsch'
            if sLang == '2':
                sLang = 'Englisch'
            if sLang == '3':
                sLang = 'Englisch mit Untertitel'
            if 'HD' == sQualy:
                sQualy = 'HD'
            else:
                sQualy = 'SD'
            hoster = {'link': sUrl, 'name': sName, 'displayedName': '%s %s %s' % (sName, sQualy, sLang)}
            hosters.append(hoster)
        if hosters:
            hosters.append('getHosterUrl')
        return hosters


def getHosterUrl(sUrl=False):
    username = cConfig().getSetting('serienstream.user')
    password = cConfig().getSetting('serienstream.pass')
    Handler = cRequestHandler(URL_LOGIN, caching=False)
    Handler.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    Handler.addHeaderEntry('Referer', ParameterHandler().getValue('entryUrl'))
    Handler.addParameters('email', username)
    Handler.addParameters('password', password)
    Handler.request()
    Request = cRequestHandler(URL_MAIN + sUrl, caching=False)
    Request.addHeaderEntry('Referer', ParameterHandler().getValue('entryUrl'))
    Request.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    Request.request()
    return [{'streamUrl': Request.getRealUrl(), 'resolved': False}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    SSsearch(oGui, sSearchText)


def SSsearch(sGui=False, sSearchText=False):
    from json import loads
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    params.getValue('sSearchText')
    oRequest = cRequestHandler(URL_SEARCH, caching=True, ignoreErrors=(sGui is not False))
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', 'https://s.to/search')
    oRequest.addHeaderEntry('Origin', 'https://s.to')
    oRequest.addHeaderEntry('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    oRequest.addParameters('keyword', sSearchText)

    sHtmlContent = oRequest.request()
    time.sleep(3)
    if not sHtmlContent:
            return


    sst = sSearchText.lower()

    jload = loads(sHtmlContent)
    total = len(jload)
    for a in jload:
        if 'support' in a.get('link'):
            continue
      
        sName = a.get('title').replace('/', '').replace('<em>', '')
        
        sLink = a.get('link')
        if a.get('description'):
            sDesc = a.get('description').replace('/', '').replace('<em>', '')
        else:
            sDesc = ' '
        
        if not sst in sName.lower() or 'pisode' in sName:
            continue
        else:
            oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showSeasons')
            oGuiElement.setMediaType('tvshow')
            oGuiElement.setDescription(sDesc)
            params.setParam('sUrl', URL_MAIN + sLink)
            params.setParam('TVShowTitle', sName)
            oGui.addFolder(oGuiElement, params, True, total)
        if not sGui:
            oGui.setView('tvshows')

#
# Advanced Metadata Search
#
def showSearchAdv():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _searchAdv(False, sSearchText)
    cGui().setEndOfDirectory()


def _searchAdv(oGui, sSearchText):
    SSsearchAdv(oGui, sSearchText)


def SSsearchAdv(sGui, sSearchText):
    from json import loads
    #import xbmc, sys
    oGui = cGui()
    params = ParameterHandler()
    params.getValue('sSearchText')

    oRequest = cRequestHandler(URL_SERIES, caching=True, ignoreErrors=(sGui is not False))
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', 'https://s.to/serien')
    oRequest.addHeaderEntry('Origin', 'https://s.to')
    oRequest.addHeaderEntry('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')

    sHtmlContent = oRequest.request()
    if not sHtmlContent:
            return

    sst = sSearchText.lower()
    #xbmc.log(str(sHtmlContent),2)

    pattern = '<li><a data.+?href="([^"]+)".+?">(.*?)\<\/a><\/l' #link - title

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)

    if not aResult[0]:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    total = len(aResult[1])
    for link, title in aResult[1]:
        if not sst in title.lower():
            continue
        else:
            #get images thumb / descr pro call. (optional)
            sThumbnail, sDescription = getMetaInfo(link, title)
            oGuiElement = cGuiElement(title, SITE_IDENTIFIER, 'showSeasons')
            oGuiElement.setThumbnail(sThumbnail)
            oGuiElement.setDescription(sDescription)
            oGuiElement.setMediaType('tvshow')
            #GuiElement.setYear(year)
            params.setParam('sUrl', URL_MAIN + link)
            params.setParam('sName', title)
            oGui.addFolder(oGuiElement, params, True, total)
        if not sGui:
            oGui.setView('tvshows')


def getMetaInfo(link, title):   # Setzen von Metadata in Suche:
    #import xbmc, sys
    oRequest = cRequestHandler(URL_MAIN + link, caching=False)
    oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
    oRequest.addHeaderEntry('Referer', 'https://s.to/serien')
    oRequest.addHeaderEntry('Origin', 'https://s.to')

    #GET CONTENT OF HTML
    sHtmlContent = oRequest.request()
    if not sHtmlContent:
        return

    #xbmc.log(str(sHtmlContent),2)
    pattern = 'seriesCoverBox">.*?<img src="(http.\:.+?)"\ al.+?data-full-description="([^"]+)"' #img , descr

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, pattern)

    if not aResult[0]:
        oGui.showInfo('xStream', 'Es wurde kein Eintrag gefunden')
        return

    for sImg, sDescr in aResult[1]:
        return sImg, sDescr

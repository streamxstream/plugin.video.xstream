# -*- coding: utf-8 -*-
# 2022-04-29 Heptamer

from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
#from resources.lib.jsnprotect import cHelper
from resources.lib.config import cConfig
SITE_IDENTIFIER = 'serienstream_to'
SITE_NAME = 'SerienStream'
SITE_ICON = 'serienstream.png'
SITE_SETTINGS = '<setting default="s.to" enable="!eq(-2,false)" id="serienstream_to-domain" label="30051" type="labelenum" values="s.to|serienstream.to|serien.cam|190.115.18.20" />'
domain = cConfig().getSetting('serienstream_to-domain')
#SITE_SETTINGS = '<setting id="serienstream.user" type="text" label="30083" default="" /><setting id="serienstream.pass" type="text" option="hidden" label="30084" default="" />'
SITE_GLOBAL_SEARCH = False

#URL_MAIN = 'https://serien.cam/'
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


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
#    if proxy == 'true':
#        pass
#    else:
    params.setParam('sUrl', URL_SERIES)
    cGui().addFolder(cGuiElement('Alle Serien', SITE_IDENTIFIER, 'showAllSeries'), params)

    params.setParam('sUrl', URL_NEW_SERIES)
    cGui().addFolder(cGuiElement('Neue Serien', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_NEW_EPISODES)
    cGui().addFolder(cGuiElement('Neue Episoden', SITE_IDENTIFIER, 'showNewEpisodes'), params)
    params.setParam('sUrl', URL_POPULAR)
    cGui().addFolder(cGuiElement('Populär', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', URL_MAIN)
    params.setParam('sCont', 'catalogNav')
    cGui().addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showValue'), params)
    params.setParam('sCont', 'homeContentGenresList')
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showValue'), params)
#    if proxy == 'true':
#        pass
#    else:
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), params)

    #cGui().addFolder(cGuiElement('[COLOR red]Bei Problemen hier Domain ändern[/COLOR]', SITE_IDENTIFIER, 'checkDomain'))
    cGui().setEndOfDirectory()


def checkDomain():
    import xbmcgui, xbmcaddon
    r = cRequestHandler('https://serien.domains/', caching=False).request()
    pattern = 'ol class="links">(.*?)</ol'
    isMatch, aResult = cParser.parse(r, pattern)
    isMatch, links = cParser.parse(str(aResult), 'href="([^"]+)')
    url = []
    for link in links:
        url.append(link)
    index = xbmcgui.Dialog().select('Serienstream', url)
    if index > -1:
        url = url[index]
        Request = cRequestHandler(url, caching=False)
        sHtmlContent = Request.request()
        if not sHtmlContent:
            xbmcgui.Dialog().ok('Serienstream', 'Fehler Domain funktioniert nicht')
            return
        if 'S.to, serien stream' in sHtmlContent:
            xbmcgui.Dialog().ok('Serienstream', 'Serienstream müsste jetzt funktioniert ggf. ist ein Kodi Neustart erforderlich')
            return xbmcaddon.Addon().setSetting('seriendomain', Request.getRealUrl())
    else:
        return False


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
    if username == '' or password == '':
        # username = cHelper.UserName
        # password = cHelper.PassWord
        import xbmcgui
        xbmcgui.Dialog().ok('xStream Serienstream', 'Unter Einstellungen / Konten für Serienstream die eigenen Kontendaten  eintragen!')
        return
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
    showAllSeries(URL_SERIES, oGui, sSearchText)

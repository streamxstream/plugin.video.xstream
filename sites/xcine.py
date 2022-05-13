# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui

SITE_IDENTIFIER = 'xcine'
SITE_NAME = 'XCine'
SITE_ICON = 'xcine.png'
URL_MAIN = 'https://xcine.me/'
URL_MOVIES = URL_MAIN + 'filme1?'
URL_SHOWS = URL_MAIN + 'serien1?'
URL_SEARCH = URL_MAIN + 'search?key=%s'


def load():
    logger.info('Load %s' % SITE_NAME)
    params = ParameterHandler()
    params.setParam('sUrl', URL_MOVIES)
    cGui().addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMenu'), params)
    params.setParam('sUrl', URL_SHOWS)
    cGui().addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showMenu'), params)
    cGui().addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'))
    cGui().setEndOfDirectory()


def showMenu():
    params = ParameterHandler()
    baseURL = params.getValue('sUrl')
    params.setParam('sUrl', baseURL + 'sort=top&sort_type=desc')
    cGui().addFolder(cGuiElement('Neueste', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + 'sort=year&sort_type=desc')
    cGui().addFolder(cGuiElement('Sortiere nach Jahr', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + 'sort=name&sort_type=desc')
    cGui().addFolder(cGuiElement('Sortiere nach Name', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + 'sort=imdb_rate&sort_type=desc')
    cGui().addFolder(cGuiElement('IMDB rating', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + 'sort=rate_point&sort_type=desc')
    cGui().addFolder(cGuiElement('Rate', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL + 'sort=view_total&sort_type=desc')
    cGui().addFolder(cGuiElement('Meist gesehen', SITE_IDENTIFIER, 'showEntries'), params)
    params.setParam('sUrl', baseURL)
    cGui().addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showGenre'), params)
    cGui().setEndOfDirectory()


def showGenre():
    params = ParameterHandler()
    entryUrl = params.getValue('sUrl')
    sHtmlContent = cRequestHandler(entryUrl).request()
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, 'Genre</option>.*?</div>')
    if isMatch:
        isMatch, aResult = cParser.parse(sContainer, 'value="([^"]+)">([^<]+)')
    if not isMatch:
        cGui().showInfo()
        return

    for sID, sName in sorted(aResult, key=lambda k: k[1]):
        params.setParam('sUrl', entryUrl + 'category=' + sID + '&country=&sort=&key=&sort_type=desc')
        cGui().addFolder(cGuiElement(sName, SITE_IDENTIFIER, 'showEntries'), params)
    cGui().setEndOfDirectory()


def showEntries(entryUrl=False, sGui=False, sSearchText=False):
    oGui = sGui if sGui else cGui()
    params = ParameterHandler()
    if not entryUrl: entryUrl = params.getValue('sUrl')
    iPage = int(params.getValue('page'))
    oRequest = cRequestHandler(entryUrl + '&page=' + str(iPage) if iPage > 0 else entryUrl, ignoreErrors=(sGui is not False))
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    if not sSearchText:
        oRequest.addParameters('load', 'full-page')
    sHtmlContent = oRequest.request()
    pattern = '<div class="group-film-small">[\s\S]*?<\/a>\s<\/div>'
    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
    if isMatch:
        pattern = '<a href="(.+?)"[\s\S]*?(?:;|data-src=")(.+?)(?:&|")[\s\S]*?title-film">(.*?)<\/b>'
        isMatch, aResult = cParser.parse(sContainer, pattern)
    if not isMatch:
        if not sGui: oGui.showInfo()
        return

    total = len(aResult)
    for sUrl, sThumbnail, sName in aResult:
        isTvshow = True if 'taffel' in sName or 'taffel' in sUrl else False
        sName = sName.replace(' stream', '')
        if sSearchText and not cParser().search(sSearchText, sName):
            continue
        isMatch, sYear = cParser.parse(sName, '(.*?)\((\d*)\)')
        for name, year in sYear:
            sName = name
            sYear = year
            break
        if 'sort=year&sort_type=desc' in entryUrl and not isTvshow:
            sName += ' (' + str(sYear) + ')'
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showEpisodes' if isTvshow else 'showHosters')
        oGuiElement.setMediaType('tvshow' if isTvshow else 'movie')
        oGuiElement.setThumbnail(sThumbnail)
        if sYear:
            oGuiElement.setYear(sYear)
        params.setParam('entryUrl', sUrl)
        params.setParam('sName', sName)
        params.setParam('sThumbnail', sThumbnail)
        oGui.addFolder(oGuiElement, params, isTvshow, total)
    if not sGui and not sSearchText:
        sPageNr = int(params.getValue('page'))
        if sPageNr == 0:
            sPageNr = 2
        else:
            sPageNr += 1
        params.setParam('page', int(sPageNr))
        params.setParam('sUrl', entryUrl)
        oGui.addNextPage(SITE_IDENTIFIER, 'showEntries', params)
        oGui.setView('tvshows' if URL_SHOWS in entryUrl else 'movies')
        oGui.setEndOfDirectory()


def showEpisodes():
    params = ParameterHandler()
    sUrl = cParser.urlEncode(params.getValue('entryUrl'), ':|/') + '/folge-1'
    sThumbnail = params.getValue('sThumbnail')
    sHtmlContent = cRequestHandler(sUrl, caching=False).request()
    pattern = '<a[^>]class="(?:current|new)".*? href="([^"]+).*?data-episode-id="(\d+)".*?folge.*?([\d]+)'
    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
    isMatch, sID = cParser.parse(sHtmlContent, 'data-movie-id="([\d]+)')
    if not isMatch:
        cGui().showInfo()
        return

    total = len(aResult)
    for sUrl, eID, eNr in aResult:
        oGuiElement = cGuiElement('Folge ' + eNr, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setThumbnail(sThumbnail)
        params.setParam('eID', eID)
        params.setParam('sID', sID[0])
        params.setParam('entryUrl', sUrl)
        cGui().addFolder(oGuiElement, params, False, total)
    cGui().setView('episodes')
    cGui().setEndOfDirectory()


def showHosters():
    hosters = []
    eID = ParameterHandler().getValue('eID')
    sID = ParameterHandler().getValue('sID')
    sUrl = cParser.urlEncode(ParameterHandler().getValue('entryUrl'), ':|/')
    if 'folge-' not in sUrl:
        sUrl = sUrl + '/deutsch'

    oRequest = cRequestHandler(sUrl, caching=False)
    oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
    sHtmlContent = oRequest.request()
    Cookie = oRequest.getResponseHeader()
    pattern = '(PHPSESSID=[^;]+).*?(SERVERID=[^;]+)'
    isMatch, Cookie = cParser().parse(str(Cookie), pattern)

    coo, sig = get_data(sHtmlContent)
    if isMatch and coo and Cookie:
        sig = sig.split('=')

    if not eID and not sID:
        pattern = 'data-movie-id="(\d+).*?data-episode-id="(\d+)"'
        isMatch, dataID = cParser().parse(sHtmlContent, pattern)
        sID = dataID[0][0]
        eID = dataID[0][1]

    if isMatch:
        oRequest = cRequestHandler(URL_MAIN + 'movie/load-stream/' + sID + '/' + eID + '?', caching=False)
        oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequest.addHeaderEntry('Referer', sUrl)
        oRequest.addHeaderEntry('Origin', 'https://xcine.me')
        oRequest.addHeaderEntry('Cookie', Cookie[0][0] + ';' + Cookie[0][1] + ';' + coo[0])
        oRequest.addParameters(sig[0], sig[1])
        sHtmlContent = oRequest.request()
        isMatch, aResult = cParser().parse(sHtmlContent, 'vip_source .*?;')
        if isMatch:
            isMatch, aResult = cParser().parse(aResult[0], 'file":"([^"]+).*?label":"([^"]+)')
        if isMatch:
            for sUrl, sQualy in aResult:
                hoster = {'link': sUrl, 'name': sQualy, 'resolveable': True}
                hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    sUrl = sUrl + '|Referer=https%3A%2F%2Fxcine.me%2F&User-Agent=Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%3B+rv%3A100.0%29+Gecko%2F20100101+Firefox%2F100.0'
    return [{'streamUrl': sUrl, 'resolved': True}]


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    showEntries(URL_SEARCH % cParser().quotePlus(sSearchText), oGui, sSearchText)


def get_data(sHtmlContent):
    import base64
    pattern = '}</script><script>.*?<div class="footer1">'
    isMatch, sContainer = cParser().parse(sHtmlContent, pattern)
    if isMatch:
        pattern = '"(_[^;]+);path'
        isMatch, coo = cParser().parse(sContainer[0], pattern)
        if not isMatch and sContainer:
            pattern = '(?:window|atob).*?"([^"]+)'
            isMatch, aResult = cParser().parse(sContainer[0], pattern)
            if isMatch:
                aResult = aResult[0]
                if not aResult.endswith('='):
                    aResult = aResult + '=='
                aResult = base64.b64decode(aResult).decode()
                pattern = '"(_[^;]+);path'
                isMatch, coo = cParser().parse(aResult, pattern)
    if isMatch:
        pattern = "'server=3';.*?function"
        isMatch, sHtmlContainer = cParser.parse(sHtmlContent, pattern)
    if isMatch:
        isMatch, K1 = cParser.parse(sHtmlContainer[0], 'loadStreamSV,.*?([a0-z9]+)')
    if isMatch:
        isMatch, K2 = cParser.parse(sHtmlContainer[0], 'var[^>]_.*?;')
    if isMatch:
        K2 = K2[0].replace(',', '').replace('];', '')
        isMatch, K2 = cParser.parse(K2, '"([^"]+)')
    if isMatch:
        L = int(K2[int(len(K2)) - 2])
        if len(str(L)) == 1 and str(L).isdigit():
            K2 = str(K2[L].replace('\\', '').replace('x', ''))
            K2 = bytearray.fromhex(K2).decode()
            sig = str(K1[0] + '=' + K2)
            return coo, sig
    return '', ''

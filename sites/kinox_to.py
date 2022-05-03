# -*- coding: utf-8 -*-
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.tools import logger, cParser
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.gui import cGui
from resources.lib.config import cConfig
from json import loads
import sys

SITE_IDENTIFIER = 'kinox_to'
SITE_NAME = 'KinoX'
SITE_ICON = 'kinox.png'

URL_MAIN = str(cConfig().getSetting('kinox-domain', 'https://www12.kinos.to/'))
URL_NEWS = URL_MAIN + '/index.php'
URL_CINEMA_PAGE = URL_MAIN + '/Kino-Filme.html'
URL_GENRE_PAGE = URL_MAIN + '/Genre.html'
URL_MOVIE_PAGE = URL_MAIN + '/Movies.html'
URL_SERIE_PAGE = URL_MAIN + '/Series.html'
URL_DOCU_PAGE = URL_MAIN + '/Documentations.html'
URL_FAVOURITE_MOVIE_PAGE = URL_MAIN + '/Popular-Movies.html'
URL_FAVOURITE_SERIE_PAGE = URL_MAIN + '/Popular-Series.html'
URL_FAVOURITE_DOCU_PAGE = URL_MAIN + '/Popular-Documentations.html'
URL_LATEST_SERIE_PAGE = URL_MAIN + '/Latest-Series.html'
URL_LATEST_DOCU_PAGE = URL_MAIN + '/Latest-Documentations.html'
URL_SEARCH = URL_MAIN + '/Search.html?q=%s'
URL_MIRROR = URL_MAIN + '/aGET/Mirror/'
URL_EPISODE_URL = URL_MAIN + '/aGET/MirrorByEpisode/'
URL_AJAX = URL_MAIN + '/aGET/List/'
URL_LANGUAGE = URL_MAIN + '/aSET/PageLang/1'


def checkDomain():
    KD = 'https://ww11.kinox.to', 'https://www12.kinos.to', 'https://www12.kinox.to', 'https://www12.kinoz.to', 'https://kinoz.to', 'https://kinos.to', 'https://kinox.tv', 'https://kinox.io', 'https://kinox.am', 'https://kinox.sx', 'https://kinox.bz', 'https://kinox.gratis', 'https://kinox.mobi', 'https://kinox.sh', 'https://kinox.lol', 'https://kinox.wtf', 'https://kinox.fun', 'https://kinox.fyi', 'https://kinox.cloud', 'https://kinox.to', 'https://kinox.click', 'https://kinox.tube', 'https://kinox.club', 'https://kinox.digital', 'https://kinox.direct', 'https://kinox.pub', 'https://kinox.express', 'https://kinox.me'
    import time
    if int(cConfig().getSetting('kinoxhourblock', 0)) + 3600 < time.time():
        i = 0
        for sUrl in KD:
            i = i + 1
            if i == len(KD):
                cConfig().setSetting('kinoxhourblock', str(time.time() + 3600))
            oRequest = cRequestHandler(sUrl, caching=False)
            oRequest.request()
            st = str(oRequest.getStatus())
            if st == '403':
                continue
            if st == '503':
                continue
            if oRequest.getStatus() == '301':
                rurl = oRequest.getRealUrl()
                oRequest = cRequestHandler(rurl, caching=False)
                oRequest.request()
                st = str(oRequest.getStatus())
            if st == '200':
                url = oRequest.getRealUrl()
                if not url.startswith('http'):
                    url = 'https://' + url
                cConfig().setSetting('kinox-domain', str(url))
                break
        return st
    return 403


def load():
    logger.info('Load %s' % SITE_NAME)
    parms = ParameterHandler()
    oGui = cGui()
    oRequest = cRequestHandler(URL_MAIN, ignoreErrors=True)
    oRequest.request()
    st = str(oRequest.getStatus())
    if not st == '200':
        checkDomain()
    parms.setParam('sUrl', URL_NEWS)
    parms.setParam('page', 1)
    parms.setParam('mediaType', 'news')
    oGui.addFolder(cGuiElement('Neues von Heute', SITE_IDENTIFIER, 'showNews'), parms)
    parms.setParam('sUrl', URL_MOVIE_PAGE)
    parms.setParam('mediaType', 'movie')
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMovieMenu'), parms)
    parms.setParam('sUrl', URL_SERIE_PAGE)
    parms.setParam('mediaType', 'series')
    oGui.addFolder(cGuiElement('Serien', SITE_IDENTIFIER, 'showSeriesMenu'), parms)
    parms.setParam('sUrl', URL_DOCU_PAGE)
    parms.setParam('mediaType', 'documentation')
    oGui.addFolder(cGuiElement('Dokumentationen', SITE_IDENTIFIER, 'showDocuMenu'), parms)
    parms.setParam('sUrl', URL_SEARCH)
    parms.setParam('mediaType', '')
    oGui.addFolder(cGuiElement('Suche', SITE_IDENTIFIER, 'showSearch'), parms)
    oGui.setEndOfDirectory()


def __createMenuEntry(oGui, sFunction, sLabel, dOutputParameter):
    parms = ParameterHandler()
    try:
        for param, value in dOutputParameter.items():
            parms.setParam(param, value)
    except Exception as e:
        logger.error("Can't add parameter to menu entry with label: %s: %s" % (sLabel, e))
    oGuiElement = cGuiElement()
    oGuiElement.setSiteName(SITE_IDENTIFIER)
    oGuiElement.setFunction(sFunction)
    oGuiElement.setTitle(sLabel)
    oGui.addFolder(oGuiElement, parms)


def showMovieMenu():
    oGui = cGui()
    parms = ParameterHandler()
    oGui.addFolder(cGuiElement('Kinofilme', SITE_IDENTIFIER, 'showCinemaMovies'), parms)
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showCharacters'), parms)
    oGui.addFolder(cGuiElement('Genres', SITE_IDENTIFIER, 'showGenres'), parms)
    parms.setParam('sUrl', URL_FAVOURITE_MOVIE_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Filme', SITE_IDENTIFIER, 'showFavItems'), parms)
    oGui.setEndOfDirectory()


def showSeriesMenu():
    oGui = cGui()
    parms = ParameterHandler()
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showCharacters'), parms)
    parms.setParam('sUrl', URL_FAVOURITE_SERIE_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Serien', SITE_IDENTIFIER, 'showFavItems'), parms)
    parms.setParam('sUrl', URL_LATEST_SERIE_PAGE)
    oGui.addFolder(cGuiElement('Neuste Serien', SITE_IDENTIFIER, 'showFavItems'), parms)
    oGui.setEndOfDirectory()


def showDocuMenu():
    oGui = cGui()
    parms = ParameterHandler()
    oGui.addFolder(cGuiElement('A-Z', SITE_IDENTIFIER, 'showCharacters'), parms)
    parms.setParam('sUrl', URL_FAVOURITE_DOCU_PAGE)
    oGui.addFolder(cGuiElement('Beliebteste Dokumentationen', SITE_IDENTIFIER, 'showFavItems'), parms)
    parms.setParam('sUrl', URL_LATEST_DOCU_PAGE)
    oGui.addFolder(cGuiElement('Neuste Dokumentationen', SITE_IDENTIFIER, 'showFavItems'), parms)
    oGui.setEndOfDirectory()


def __createLanguage(sLangID):
    return {'1': 'Deutsch', '2': 'Englisch', '4': 'Chinesisch', '5': 'Spanisch', '6': 'Französisch', '7': 'Türkisch',
            '8': 'Japanisch', '9': 'Arabisch', '11': 'Italienisch', '12': 'Kroatisch', '13': 'Serbisch',
            '14': 'Bosnisch', '15': 'Deutsch / Englisch', '16': 'Niederländisch', '17': 'Koreanisch',
            '24': 'Griechisch', '25': 'Russisch', '26': 'Indisch', }.get(sLangID, sLangID)


def __checkSubLanguage(sTitle):
    if ' subbed*' not in sTitle:
        return [sTitle, '']
    temp = sTitle.split(' *')
    subLang = temp[-1].split('subbed*')[0].strip()
    title = ' '.join(temp[0:-1]).strip()
    return [title, 'de'] if subLang == 'german' else [title, subLang]


def __getHtmlContent(sUrl=None, ignoreErrors=False):
    parms = ParameterHandler()
    if sUrl is None and not parms.exist('sUrl'):
        logger.error('There is no url we can request.')
        return False
    elif sUrl is None:
        sUrl = parms.getValue('sUrl')
    sPrefLang = __getPreferredLanguage()
    oRequest = cRequestHandler(sUrl, ignoreErrors=ignoreErrors)
    oRequest.addHeaderEntry('Cookie', sPrefLang + 'ListDisplayYears=Always;')
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    return oRequest.request()


def __getPreferredLanguage():
    sLanguage = cConfig().getSetting('prefLanguage')
    if sLanguage == '0':
        sPrefLang = 'ListNeededLanguage=25%2C24%2C26%2C2%2C5%2C6%2C7%2C8%2C11%2C15%2C16%2C9%2C12%2C13%2C14%2C17%2C4'
    elif sLanguage == '1':
        sPrefLang = 'ListNeededLanguage=25%2C24%2C26%2C5%2C6%2C7%2C8%2C11%2C15%2C16%2C9%2C12%2C13%2C14%2C17%2C4%2C1'
    else:
        sPrefLang = ''
    return sPrefLang


def __displayItems(sGui, sHtmlContent):
    oGui = sGui if sGui else cGui()
    parms = ParameterHandler()
    pattern = '<td class="Icon"><img width="16" height="11" src="/gr/sys/lng/(\d+).png" alt="language"></td>' + \
              '.*?title="([^\"]+)".*?<td class="Title">.*?<a href="([^\"]+)" onclick="return false;">([^<]+)</a> <span class="Year">([0-9]+)</span>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        logger.error('Could not find an item')
        return
    total = len(aResult[1])
    for aEntry in aResult[1]:
        sTitle = aEntry[3]
        sTitle, subLang = __checkSubLanguage(sTitle)
        sLang = __createLanguage(aEntry[0])
        sUrl = URL_MAIN + aEntry[2]
        if aEntry[1] == 'movie' or aEntry[1] == 'cinema':
            mediaType = 'movie'
        elif aEntry[1] == 'series':
            mediaType = 'series'
        else:
            mediaType = 'documentation'
        oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
        oGuiElement.setLanguage(sLang)
        oGuiElement.setSubLanguage(subLang)
        oGuiElement.setYear(aEntry[4])
        parms.setParam('sUrl', sUrl)
        parms.setParam('mediaType', mediaType)
        if mediaType == 'series':
            oGuiElement.setMediaType('tvshow')
            oGui.addFolder(oGuiElement, parms, total)
        elif mediaType == 'movie':
            oGuiElement.setMediaType('movie')
            oGui.addFolder(oGuiElement, parms, False, total)
        else:
            oGui.addFolder(oGuiElement, parms, False, total)


def showFavItems():
    oGui = cGui()
    sHtmlContent = __getHtmlContent()
    __displayItems(oGui, sHtmlContent)
    oGui.setEndOfDirectory()


def showNews():
    parms = ParameterHandler()
    sUrl = parms.getValue('sUrl')
    pattern = '<div class="Opt leftOpt Headlne"><h1>([a-zA-Z0-9\s.]+)' + \
              '</h1></div>\s*<div class="Opt rightOpt Hint">Insgesamt: (.*?)</div>'
    sHtmlContent = __getHtmlContent(sUrl)
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            sTitle = str(aEntry[0]) + ' (' + str(aEntry[1]) + ')'
            oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'parseNews')
            parms.addParams({'sUrl': URL_NEWS, 'page': 1, 'mediaType': 'news', 'sNewsTitle': aEntry[0]})
            cGui().addFolder(oGuiElement, parms)
    cGui().setEndOfDirectory()


def parseNews():
    oGui = cGui()
    parms = ParameterHandler()
    sUrl = parms.getValue('sUrl')
    sNewsTitle = parms.getValue('sNewsTitle')
    aResult = cParser().parse(sNewsTitle, 'Neue (.*?) online')
    if aResult[0]:
        if str(aResult[1][0]) == 'Serien':
            mediaType = 'series'
        else:
            mediaType = 'movie'
    pattern = '<div class="Opt leftOpt Headlne"><h1>' + sNewsTitle \
              + '</h1></div>(.*?)<div class="ModuleFooter">'
    sHtmlContent = __getHtmlContent(sUrl)
    aResult = cParser().parse(sHtmlContent, pattern)

    if not aResult[0]:
        logger.info("Can't get any news")
        oGui.setEndOfDirectory()
        return
    pattern = '<td class="Icon"><img src="/gr/sys/lng/(\d+).png" alt="language" width="16" ' + \
              'height="11".*?<td class="Title.*?rel="([^"]+)"><a href="([^\"]+)".*?class="OverlayLabel">([^<]+)<' + \
              '(span class="EpisodeDescr">)?([^<]+)'
    aResult = cParser().parse(aResult[1][0], pattern)
    if not aResult[0]:
        logger.info("Can't get any news")
        oGui.setEndOfDirectory()
        return
    total = len(aResult[1])

    for aEntry in aResult[1]:
        sLang = __createLanguage(aEntry[0])
        sTitle = aEntry[3]
        if sTitle.endswith(':'):
            sTitle = sTitle[:-1]
        sTitle, subLang = __checkSubLanguage(sTitle)
        sUrl = aEntry[2]
        aUrl = sUrl.split(',')
        if len(aUrl) > 0:
            sUrl = aUrl[0]
            oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
            oGuiElement.setLanguage(sLang)
            oGuiElement.setSubLanguage(subLang)
            oGuiElement.setThumbnail(URL_MAIN + str(aEntry[1]))
            parms.setParam('sUrl', URL_MAIN + sUrl)
            parms.setParam('mediaType', mediaType)
            if mediaType == 'series':
                oGuiElement.setMediaType('tvshow')
                oGui.addFolder(oGuiElement, parms, total)
                oGui.setView('tvshows')
            else:
                oGuiElement.setMediaType('movie')
                oGui.addFolder(oGuiElement, parms, False, total)
                oGui.setView('movies')
    oGui.setEndOfDirectory()


def showCharacters():
    oGui = cGui()
    parms = ParameterHandler()

    if parms.exist('sUrl') and parms.exist('page') and parms.exist('mediaType'):
        siteUrl = parms.getValue('sUrl')
        sHtmlContent = __getHtmlContent(siteUrl)
        pattern = 'class="LetterMode.*?>([^>]+)</a>'
        aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        for aEntry in aResult[1]:
            oGuiElement = cGuiElement(aEntry, SITE_IDENTIFIER, 'ajaxCall')
            parms.setParam('character', aEntry[0])
            if parms.exist('mediaTypePageId'):
                sMediaTypePageId = parms.getValue('mediaTypePageId')
                parms.setParam('mediaTypePageId', sMediaTypePageId)
            oGui.addFolder(oGuiElement, parms)
    oGui.setEndOfDirectory()


def showGenres():
    logger.info('load displayGenreSite')
    pattern = '<td class="Title"><a.*?href="/Genre/([^"]+)">([^<]+)</a>.*?Tipp-([0-9]+).html">'
    sHtmlContent = __getHtmlContent(URL_GENRE_PAGE)
    aResult = cParser().parse(sHtmlContent, pattern)
    oGui = cGui()
    if aResult[0]:
        for aEntry in aResult[1]:
            iGenreId = aEntry[2]
            __createMenuEntry(oGui, 'showCharacters', aEntry[1], {'page': 1, 'mediaType': 'fGenre', 'mediaTypePageId': iGenreId, 'sUrl': URL_MOVIE_PAGE})
    oGui.setEndOfDirectory()


def showCinemaMovies():
    logger.info('load displayCinemaSite')
    oGui = cGui()
    _cinema(oGui)
    oGui.setView('movies')
    oGui.setEndOfDirectory()


def _cinema(oGui):
    pattern = '<div class="Opt leftOpt Headlne"><a title="(.*?)" href="(.*?)">.*?src="(.*?)".*?class="Descriptor">(.*?)</div.*?/lng/([0-9]+).png".*?IMDb:</b> (.*?) /'
    parms = ParameterHandler()
    sHtmlContent = __getHtmlContent(URL_CINEMA_PAGE)
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]: return
    total = len(aResult[1])
    for aEntry in aResult[1]:
        sMovieTitle = aEntry[0]
        lang = __createLanguage(aEntry[4])
        rating = aEntry[5]
        oGuiElement = cGuiElement()
        oGuiElement.setSiteName(SITE_IDENTIFIER)
        oGuiElement.setFunction('parseMovieEntrySite')
        oGuiElement.setLanguage(lang)
        oGuiElement.setTitle(sMovieTitle)
        oGuiElement.setDescription(aEntry[3])
        oGuiElement.setMediaType('movie')
        oGuiElement.setThumbnail(URL_MAIN + str(aEntry[2]))
        oGuiElement.addItemValue('rating', rating)
        parms.setParam('sUrl', URL_MAIN + str(aEntry[1]))
        oGui.addFolder(oGuiElement, parms, False, total)


def parseMovieEntrySite():
    parms = ParameterHandler()
    if parms.exist('sUrl'):
        sUrl = parms.getValue('sUrl')
        sHtmlContent = __getHtmlContent(sUrl)
        sMovieTitle = __createMovieTitle(sHtmlContent)
        result = cParser().parse(sHtmlContent, '<div class="Grahpics">.*?<img src="([^"]+)"')
        thumbnail = URL_MAIN + str(result[1][0]) if result[0] else False
        bIsSerie = __isSerie(sHtmlContent)
        if bIsSerie:
            oGui = cGui()
            aSeriesItems = parseSerieSite(sHtmlContent)
            if not aSeriesItems[0]: return
            total = len(aSeriesItems)
            for aEntry in aSeriesItems[1]:
                seasonNum = str(aEntry)
                guiElement = cGuiElement('%s - Staffel %s' % (sMovieTitle, seasonNum), SITE_IDENTIFIER, 'showEpisodes')
                guiElement.setMediaType('season')
                guiElement.setSeason(seasonNum)
                guiElement.setTVShowTitle(sMovieTitle)
                parms.setParam('Season', seasonNum)
                if thumbnail:
                    guiElement.setThumbnail(thumbnail)
                oGui.addFolder(guiElement, parms, total)
            oGui.setView('seasons')
            oGui.setEndOfDirectory()
        else:
            logger.info('Movie')
            result = showHosters()
            return result


def showEpisodes():
    oGui = cGui()
    parms = ParameterHandler()
    sUrl = parms.getValue('sUrl')
    seasonNum = parms.getValue('Season')
    sHtmlContent = __getHtmlContent(sUrl)
    sMovieTitle = __createMovieTitle(sHtmlContent)
    result = cParser().parse(sHtmlContent, '<div class="Grahpics">.*?<img src="([^"]+)"')
    thumbnail = URL_MAIN + str(result[1][0]) if result[0] else False
    aSeriesItems = parseSerieEpisodes(sHtmlContent, seasonNum)
    if not aSeriesItems[0]: return
    for item in aSeriesItems:
        oGuiElement = cGuiElement(item['title'], SITE_IDENTIFIER, 'showHosters')
        sShowTitle = sMovieTitle.split('(')[0].split('*')[0]
        oGuiElement.setThumbnail(thumbnail)
        oGuiElement.setMediaType('episode')
        oGuiElement.setSeason(item['season'])
        oGuiElement.setEpisode(item['episode'])
        oGuiElement.setTVShowTitle(sShowTitle)
        parms.addParams({'sUrl': item['url'], 'episode': item['episode'], 'season': item['season']})
        oGui.addFolder(oGuiElement, parms, False, len(aSeriesItems))
    oGui.setView('episodes')
    oGui.setEndOfDirectory()


def __createMovieTitle(sHtmlContent):
    pattern = '<h1><span style="display: inline-block">(.*?)</h1>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        return str(aResult[1][0])
    return False


def parseSerieSite(sHtmlContent):
    pattern = '<option[^>]+value="(\d+)"[^>]+>Staffel.+?</option>'
    return cParser().parse(sHtmlContent, pattern)


def parseSerieEpisodes(sHtmlContent, seasonNum):
    aSeriesItems = []
    pattern = 'id="SeasonSelection" rel="([^"]+)"'
    aResult = cParser().parse(sHtmlContent, pattern)
    if aResult[0]:
        aSeriesUrls = aResult[1][0].split("&")
        sSeriesUrl = '&' + str(aSeriesUrls[0]) + '&' + str(aSeriesUrls[1])
    pattern = '<option.*?value="%d" rel="([^"]+)".*?>Staffel.*?</option>' % int(seasonNum)
    aResult = cParser().parse(sHtmlContent, pattern)
    logger.info(aResult[1])
    if aResult[0]:
        aSeriesIds = aResult[1][0].split(',')
        for iSeriesIds in aSeriesIds:
            aSeries = {}
            iEpisodeNum = iSeriesIds
            sTitel = 'Folge ' + str(iEpisodeNum)
            sUrl = URL_EPISODE_URL + sSeriesUrl + '&Season=' + str(seasonNum) + '&Episode=' + str(iEpisodeNum)
            aSeries['title'] = sTitel
            aSeries['url'] = sUrl
            aSeries['season'] = seasonNum
            aSeries['episode'] = iEpisodeNum
            aSeriesItems.append(aSeries)
    return aSeriesItems


def __isSerie(sHtmlContent):
    pattern = 'id="SeasonSelection" rel="([^"]+)"'
    aResult = cParser().parse(sHtmlContent, pattern)
    return aResult[0] == True


def ajaxCall():
    oGui = cGui()
    metaOn = oGui.isMetaOn
    parms = ParameterHandler()
    if parms.exist('page') and parms.exist('mediaType'):
        iPage = parms.getValue('page')
        sMediaType = parms.getValue('mediaType')
    iMediaTypePageId = False
    if parms.exist('mediaTypePageId'):
        iMediaTypePageId = parms.getValue('mediaTypePageId')
    sCharacter = 'A'
    if parms.exist('character'):
        sCharacter = parms.getValue('character')
    logger.info('MediaType: ' + sMediaType + ' , Page: ' + str(iPage) + ' , iMediaTypePageId: ' + str(
        iMediaTypePageId) + ' , sCharacter: ' + str(sCharacter))
    sHtmlContent = __getAjaxContent(sMediaType, iPage, iMediaTypePageId, metaOn, sCharacter)
    if not sHtmlContent:
        return
    if metaOn and not sMediaType == 'documentation':
        aData = loads(sHtmlContent)['aaData']
        total = len(aData)

        for aEntry in aData:
            pattern = '<a href="([^"]+)".*?onclick="return false;">([^<]+)<.*?>([0-9]{4})<'
            aResult = cParser().parse(aEntry[2], pattern)
            if aResult[0]:
                sYear = str(aResult[1][0][2]).strip()
                sTitle = aResult[1][0][1]
                sLang = aEntry[0]
                sUrl = URL_MAIN + str(aResult[1][0][0])
                oGuiElement = cGuiElement(sTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
                oGuiElement.setYear(sYear)
                oGuiElement.setLanguage(sLang)
                parms.setParam('sUrl', sUrl)
                if sMediaType == 'series':
                    oGuiElement.setMediaType('tvshow')
                    oGui.addFolder(oGuiElement, parms, total)
                else:
                    oGuiElement.setMediaType('movie')
                    oGui.addFolder(oGuiElement, parms, False, total)
        pattern = '"iTotalDisplayRecords":"([^"]+)'
        aResult = cParser().parse(sHtmlContent, pattern)
        if aResult[0]:
            for aEntry in aResult[1]:
                iTotalCount = aEntry[0]
                iNextPage = int(iPage) + 1
                iCurrentDisplayStart = __createDisplayStart(iNextPage)
                if iCurrentDisplayStart < iTotalCount:
                    parms = ParameterHandler()
                    parms.setParam('page', iNextPage)
                    parms.setParam('character', sCharacter)
                    parms.setParam('mediaType', sMediaType)
                if iMediaTypePageId:
                    parms.setParam('mediaTypePageId', iMediaTypePageId)
                oGui.addNextPage(SITE_IDENTIFIER, 'ajaxCall', parms)

    else:
        aData = loads(sHtmlContent)
        pattern = '<div class="Opt leftOpt Headlne"><a title="(.*?)" href="(.*?)">.*?src="(.*?)".*?class="Descriptor">(.*?)</div.*?lng/(.*?).png'
        if sys.version_info[0] == 2:
            aResult = cParser().parse(aData['Content'].encode('utf-8'), pattern)
        else:
            aResult = cParser().parse(aData['Content'], pattern)

        if aResult[0]:
            total = len(aResult[1])
            for aEntry in aResult[1]:
                sMovieTitle, subLang = __checkSubLanguage(aEntry[0])
                lang = __createLanguage(aEntry[4])
                oGuiElement = cGuiElement(sMovieTitle, SITE_IDENTIFIER, 'parseMovieEntrySite')
                oGuiElement.setDescription(aEntry[3])
                oGuiElement.setThumbnail(URL_MAIN + str(aEntry[2]))
                oGuiElement.setLanguage(lang)
                oGuiElement.setSubLanguage(subLang)
                parms.setParam('sUrl', URL_MAIN + str(aEntry[1]))
                if sMediaType == 'series':
                    oGui.addFolder(oGuiElement, parms, total)
                else:
                    oGui.addFolder(oGuiElement, parms, False, total)
            iTotalCount = int(aData['Total'])
            iNextPage = int(iPage) + 1
            if __createDisplayStart(iNextPage) < iTotalCount:
                parms = ParameterHandler()
                parms.setParam('page', iNextPage)
                if iMediaTypePageId:
                    parms.setParam('mediaTypePageId', iMediaTypePageId)
                oGui.addNextPage(SITE_IDENTIFIER, 'ajaxCall', parms)
    if sMediaType == 'series':
        oGui.setView('tvshows')
    else:
        oGui.setView('movies')
    oGui.setEndOfDirectory()


def __createDisplayStart(iPage):
    return (30 * int(iPage)) - 30


def __getAjaxContent(sMediaType, iPage, iMediaTypePageId, metaOn, sCharacter=''):
    iDisplayStart = __createDisplayStart(iPage)
    sPrefLang = __getPreferredLanguage()
    oRequest = cRequestHandler(URL_AJAX)
    if not iMediaTypePageId:
        oRequest.addParameters('additional', '{"fType":"' + str(sMediaType) + '","fLetter":"' + str(sCharacter) + '"}')
    else:
        oRequest.addParameters('additional', '{"foo":"bar","' + str(
            sMediaType) + '":"' + iMediaTypePageId + '","fType":"movie","fLetter":"' + str(sCharacter) + '"}')
    oRequest.addParameters('iDisplayLength', '30')
    oRequest.addParameters('iDisplayStart', iDisplayStart)
    if metaOn and not sMediaType == 'documentation':
        oRequest.addParameters('bSortable_0', 'true')
        oRequest.addParameters('bSortable_1', 'true')
        oRequest.addParameters('bSortable_2', 'true')
        oRequest.addParameters('bSortable_3', 'false')
        oRequest.addParameters('bSortable_4', 'false')
        oRequest.addParameters('bSortable_5', 'false')
        oRequest.addParameters('bSortable_6', 'true')
        oRequest.addParameters('iColumns', '7')
        oRequest.addParameters('iSortCol_0', '2')
        oRequest.addParameters('iSortingCols', '1')
        oRequest.addParameters('sColumns', '')
        oRequest.addParameters('sEcho', iPage)
        oRequest.addParameters('sSortDir_0', 'asc')
        sUrl = oRequest.getRequestUri()
        oRequest = cRequestHandler(sUrl)
    else:
        oRequest.addParameters('ListMode', 'cover')
        oRequest.addParameters('Page', str(iPage))
        oRequest.addParameters('Per_Page', '30')
        oRequest.addParameters('dir', 'desc')
    oRequest.addHeaderEntry('Cookie', sPrefLang + 'ListDisplayYears=Always;')
    return oRequest.request()


def showHosters():
    parms = ParameterHandler()
    if parms.exist('sUrl'):
        sUrl = parms.getValue('sUrl')
    sHtmlContent = __getHtmlContent(sUrl)
    pattern = 'class="MirBtn.*?rel="([^"]+)".*?class="Named">([^<]+)</div>(.*?)</div>'
    aResult = cParser().parse(sHtmlContent, pattern)
    hosters = []
    if aResult[0]:
        for aEntry in aResult[1]:
            sHoster = aEntry[1]
            pattern = '<b>Mirror</b>: [0-9]+/([0-9]+)'
            aResult = cParser().parse(aEntry[2], pattern)
            mirrors = 1
            if aResult[0]:
                mirrors = int(aResult[1][0])
            for i in range(1, mirrors + 1):
                sUrl = URL_MIRROR + cParser().unquotePlus(aEntry[0])
                mirrorName = ''
                if mirrors > 1:
                    mirrorName = ' Mirror ' + str(i)
                    sUrl = cParser().replace(r'Mirror=[0-9]+', 'Mirror=' + str(i), sUrl)
                hoster = {'name': sHoster, 'link': sUrl, 'displayedName': sHoster + mirrorName}
                hosters.append(hoster)
        hosters.append('getHosterUrl')
    return hosters


def getHosterUrl(sUrl=False):
    sHtmlContent = cRequestHandler(sUrl).request()
    oRequest = cRequestHandler(sUrl)
    oRequest.addHeaderEntry('Referer', URL_MAIN)
    sHtmlContent = oRequest.request()
    isMatch, sStreamUrl = cParser.parseSingleResult(sHtmlContent, 'a\shref=\\\\".*?(https?:.*?)\\\\"')
    if not isMatch:
        isMatch, sStreamUrl = cParser.parseSingleResult(sHtmlContent, '<iframe src=[^"]*"([^"]+)')
    if isMatch:
        if sStreamUrl.startswith('//'):
            sStreamUrl = 'https:' + sStreamUrl
        if 'streamcrypt.net' in sStreamUrl:
            oRequest = cRequestHandler(sStreamUrl, caching=False)
            oRequest.request()
            sStreamUrl = oRequest.getRealUrl()
        if 'thevideo' in sStreamUrl:
            sStreamUrl = sStreamUrl.replace('embed-', 'stream').replace('html', 'mp4')
            sUrl = _redirectHoster(sStreamUrl)
            return [{'streamUrl': sUrl, 'resolved': True}]
        return [{'streamUrl': sStreamUrl, 'resolved': False}]


def _redirectHoster(url):
    try:
        from urllib2 import build_opener, HTTPError
    except ImportError:
        from urllib.error import HTTPError
        from urllib.request import build_opener
    opener = build_opener()
    opener.addheaders = [('Referer', url)]
    try:
        resp = opener.open(url)
        if url != resp.geturl():
            return resp.geturl()
        else:
            return url
    except HTTPError as e:
        if e.code == 403:
            if url != e.geturl():
                return e.geturl()
        raise


def showSearch():
    sSearchText = cGui().showKeyBoard()
    if not sSearchText: return
    _search(False, sSearchText)
    cGui().setEndOfDirectory()


def _search(oGui, sSearchText):
    sHtmlContent = __getHtmlContent(URL_SEARCH % cParser().quotePlus(sSearchText), ignoreErrors=(oGui is not False))
    __displayItems(oGui, sHtmlContent)

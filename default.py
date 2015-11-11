import re
import urllib
import urllib2
import xbmcaddon
import xbmcplugin
import xbmcgui
from resources.lib.sourcesList import sourcesList
from resources.lib.router import route, router_process

HANDLE=int(sys.argv[1])
AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
ADDON_NAME = 'plugin.video.animeram'
ADDON = xbmcaddon.Addon(ADDON_NAME)
MENU_ITEMS = [
    ("Latest", "latest"),
    ("List all", "all"),
    ("Search", "search")
]

def post_request(url, data={}):
    data = urllib.urlencode(data)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    response_content = response.read()
    response.close()
    return response_content

def animeram_url(url=''):
    return "http://www.animeram.me/%s" % (url)

def addon_url(url=''):
    return "plugin://%s/%s" % (ADDON_NAME, url)

def get_plugin_url():
    addon_base = addon_url()
    assert sys.argv[0].startswith(addon_base), "something bad happened in here"
    return sys.argv[0][len(addon_base):]

def keyboard(text):
    keyboard = xbmc.Keyboard("", text, False)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    return None

def parse_search_result(res):
    IMAGE_RE = re.compile("<img\ssrc=\"(.+?)\"", re.DOTALL)
    NAME_LINK_RE = re.compile("<h3><a\shref=\"%s(.+?)/\">(.+?)</a></h3>" % animeram_url(), re.DOTALL)
    image = IMAGE_RE.findall(res)[0]
    url, name = NAME_LINK_RE.findall(res)[0]

    return allocate_item(name, "animes/" + url + "/", True, image)

def search_site(search_string):
    RELEVANT_RESULTS_RE = re.compile("<div\sclass=\"popular\sfull\">\s<table.+?>(.+?)</table>", re.DOTALL)
    results = post_request("http://www.animeram.me/anime-list/search/",
            {"cmd_wpa_wgt_anm_sch_sbm": "Search", "txt_wpa_wgt_anm_sch_nme": search_string})
    all_results = []
    for result in RELEVANT_RESULTS_RE.findall(results):
        all_results.append(parse_search_result(result))
    return all_results

def extract_info(anime_ref):
    # TODO: Caching
    IMG_RE = re.compile("<img class=\"cvr\" src=\"(.+?)\"", re.DOTALL)
    info_url = animeram_url("wpa-ajx/anm-det-pop/?anm=" + anime_ref)
    res = {'image': ''}
    info = urllib2.urlopen(info_url).read()
    image = IMG_RE.findall(info)
    if len(image) > 0:
        res['image'] = image[0]
    return res

def extract_links(resp, extract_image):
    if extract_image:
        LINK_RE = re.compile("<a\shref=\"%s([-\w\s\d]+?)/(\d+?)/\".+?rel=\"(\d+)\".+?><strong>(.+?)</strong></a>" % animeram_url(), re.DOTALL)
    else:
        LINK_RE = re.compile("<a\shref=\"%s([-\w\s\d]+?)/(\d+?)/\"><strong>(.+?)</strong></a>\s:\s(.*?)</div>" % animeram_url(), re.DOTALL)

    results = []
    for res in LINK_RE.findall(resp):
        if extract_image:
            info = extract_info(res[2])
            image = info['image']
            name = res[3]
        else:
            image = ''
            ep_name = res[3].strip()
            if len(ep_name):
                name = "%s : %s" % (res[2] , ep_name)
            else:
                name = res[2]

        results.append(allocate_item(name, "play/" + res[0] + "/" + res[1], False, image))
    return results

def extract_episodes(resp, context, extract_image=False):
    LATEST_UL_RE = re.compile("<ul\sclass=\"newmanga\">(.+?)</ul>", re.DOTALL)
    resp_data = resp.read()
    new_manga =  LATEST_UL_RE.findall(resp_data)[0]
    return extract_links(new_manga, extract_image)

def extract_latest_videos(resp, context):
    return extract_episodes(resp, context, True)

def extract_by_letter(resp, context):
    resp_data = resp.read()
    FILTERED_RE = re.compile("<a\sname=\"%s\"></a>\s<div\sclass=\"series_alpha\">(.+?)</div>\s</div>" % context, re.DOTALL)
    filtered = FILTERED_RE.findall(resp_data)[0]
    RESULTS_RE = re.compile("<a\shref=\"%s([-\w\s\d]+?)/\".+?rel=\"(\d+)\".+?>(.+?)</a>" % animeram_url(), re.DOTALL)

    results = []
    for res in RESULTS_RE.findall(filtered):
        info = extract_info(res[1])
        results.append(allocate_item(res[2], "animes/" + res[0] + "/", True, info['image']))

    return results

def grep_from_web(url, extractor, context=''):
    response = urllib2.urlopen(url)
    video_data = extractor(response, context)
    response.close()
    draw_items(video_data)

@route('animes/*')
def ANIMES_PAGE(animeurl):
    return grep_from_web(animeram_url(animeurl), extract_episodes, animeurl)

@route('latest')
def LATEST(payload):
    return grep_from_web(animeram_url(), extract_latest_videos)

@route('play/*')
def PLAY(url):
    s = sourcesList(animeram_url(url))
    link = s.get_video_link()
    if link != -1:
        return xbmc_play_source(s.name, link)

@route('search')
def SEARCH(payload):
    query = keyboard("Search")
    if query:
        return draw_items(search_site(query))
    return False

@route('all')
def LIST_ALL_AB(payload):
    return draw_items([allocate_item(i, "all/%s" % i, True) for i in AB_LIST])

@route('all/*')
def SHOW_AB_LISTING(payload):
    assert payload in AB_LIST, "Bad Param"
    return grep_from_web(animeram_url("anime-list-all"), extract_by_letter, payload)

@route('')
def LIST_MENU(payload):
    return draw_items([allocate_item(name, url, True) for name, url in MENU_ITEMS])

def allocate_item(name, url, is_dir=False, image=''):
    new_res = {}
    new_res['is_dir'] = is_dir
    new_res['image'] = image
    new_res['name'] = name
    new_res['url'] = url
    return new_res

def draw_items(video_data):
    for vid in video_data:
        if vid['is_dir']:
            xbmc_add_dir(vid['name'], vid['url'], vid['image'])
        else:
            xbmc_add_player_item(vid['name'], vid['url'], vid['image'])
    return True

def xbmc_add_player_item(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", ADDON.getAddonInfo('path') + "/fanart.jpg")
    liz.setProperty("Video", "true")
    liz.addContextMenuItems([], replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz, isFolder=False)
    return ok

def xbmc_add_dir(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", ADDON.getAddonInfo('path') + "/fanart.jpg")
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz,isFolder=True)
    return ok

def xbmc_play_source(name, link):
    p = xbmc.Player()
    liz=xbmcgui.ListItem(name)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty('video', "true")
    p.play(link, liz)

router_process(get_plugin_url())
xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

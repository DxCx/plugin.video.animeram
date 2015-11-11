import re
import urllib
import urllib2
import xbmcaddon
import xbmcplugin
import xbmcgui
from resources.lib.sourcesList import sourcesList


addon_name = 'plugin.video.animeram'
my_addon = xbmcaddon.Addon(addon_name)
HANDLE=int(sys.argv[1])
AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]

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
    return "plugin://%s/%s" % (addon_name, url)

def INDEX(url):
    payload = "/".join(url.split("/")[1:])
    if url == '':
        addDir("Latest", "latest")
        addDir("List all", "all")
        addDir("Search", "search")
    elif url == 'search':
        keyboard = xbmc.Keyboard("", 'Search', False)
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            SEARCHVIEW(query)
    elif url.startswith("play"):
        PLAY(payload)
    elif url.startswith("animes"):
        ANIMES_PAGE(payload)
    elif url.startswith("all"):
        if not len(payload):
            LIST_ALL_AB()
        else:
            assert PAYLOAD in AB_LIST, "Bad Param"
            VIDEOLINKS(animeram_url("anime-list-all"), extract_by_letter, payload)
    elif url == 'latest':
        VIDEOLINKS(animeram_url(), extract_latest_videos)

def parse_search_result(res):
    IMAGE_RE = re.compile("<img\ssrc=\"(.+?)\"", re.DOTALL)
    NAME_LINK_RE = re.compile("<h3><a\shref=\"%s(.+?)/\">(.+?)</a></h3>" % animeram_url(), re.DOTALL)
    image = IMAGE_RE.findall(res)[0]
    url, name = NAME_LINK_RE.findall(res)[0]

    new_res = {}
    new_res['is_dir'] = True
    new_res['info'] = {}
    new_res['info']['image'] = image
    new_res['name'] = name
    new_res['url'] = "animes/" + url + "/"
    return new_res

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
        new_res = {}
        new_res['is_dir'] = False
        new_res['info'] = {}
        new_res['info']['image'] = ''
        if extract_image:
            new_res['info'] = extract_info(res[2])
            new_res['name'] = res[3]
        else:
            ep_name = res[3].strip()
            if len(ep_name):
                new_res['name'] = "%s : %s" % (res[2] , ep_name)
            else:
                new_res['name'] = res[2]
        new_res['url'] = "play/" + res[0] + "/" + res[1]
        results.append(new_res)
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
        new_res = {}
        new_res['is_dir'] = True
        new_res['info'] = extract_info(res[1])
        new_res['name'] = res[2]
        new_res['url'] = "animes/" + res[0] + "/"
        results.append(new_res)

    return results

def SEARCHVIEW(search_string):
    results = search_site(search_string)
    draw_items(results)
    return True

def ANIMES_PAGE(animeurl):
    return VIDEOLINKS(animeram_url(animeurl), extract_episodes, animeurl)

def draw_items(video_data):
    for vid in video_data:
        if vid['is_dir']:
            addDir(vid['name'], vid['url'], vid['info']['image'])
        else:
            addLink(vid['name'], vid['url'], vid['info']['image'])
    return True

def play_source(name, link):
    p = xbmc.Player()
    liz=xbmcgui.ListItem(name)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty('video', "true")
    p.play(link, liz)

def PLAY(url):
    s = sourcesList(animeram_url(url))
    link = s.get_video_link()
    if link != -1:
        return play_source(s.name, link)

def LIST_ALL_AB():
    results = []
    for Letter in AB_LIST:
        res = {}
        res['is_dir'] = True
        res['name'] = Letter
        res['url'] = "all/%s" % Letter
        res['info'] = {}
        res['info']['image'] = ''
        results.append(res)
    draw_items(results)

def VIDEOLINKS(url, extractor, context=''):
    response = urllib2.urlopen(url)
    video_data = extractor(response, context)
    response.close()
    draw_items(video_data)

def addLink(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", my_addon.getAddonInfo('path') + "/fanart.jpg")
    liz.setProperty("Video", "true")
    liz.addContextMenuItems([], replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz, isFolder=False)
    return ok

def addDir(name, url, iconimage=''):
    ok=True
    u=addon_url(url)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo('video', infoLabels={ "Title": name })
    liz.setProperty("fanart_image", my_addon.getAddonInfo('path') + "/fanart.jpg")
    ok=xbmcplugin.addDirectoryItem(handle=HANDLE,url=u,listitem=liz,isFolder=True)
    return ok

def get_plugin_url():
    addon_base = addon_url()
    assert sys.argv[0].startswith(addon_base), "something bad happened in here"
    return sys.argv[0][len(addon_base):]

INDEX(get_plugin_url())
xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=True, cacheToDisc=True)

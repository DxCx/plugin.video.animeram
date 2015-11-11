import xbmcaddon
import xbmcplugin
import xbmcgui
from resources.lib.SourcesList import SourcesList
from resources.lib.router import route, router_process
from resources.lib.AnimeramBrowser import AnimeramBrowser

HANDLE=int(sys.argv[1])
AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
ADDON_NAME = 'plugin.video.animeram'
ADDON = xbmcaddon.Addon(ADDON_NAME)
MENU_ITEMS = [
    ("Latest", "latest"),
    ("List all", "all"),
    ("Search", "search")
]

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
    liz.setProperty("IsPlayable", "true")
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

def xbmc_play_source(link):
    if link:
        xbmcplugin.setResolvedUrl(HANDLE, True, xbmcgui.ListItem(path=link))
    else:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())

@route('animes/*')
def ANIMES_PAGE(animeurl):
    return draw_items(AnimeramBrowser().get_anime_episodes(animeurl))

@route('latest')
def LATEST(payload):
    return draw_items(AnimeramBrowser().get_latest())

@route('search')
def SEARCH(payload):
    query = keyboard("Search")
    if query:
        return draw_items(AnimeramBrowser().search_site(query))
    return False

@route('all')
def LIST_ALL_AB(payload):
    return draw_items([allocate_item(i, "all/%s" % i, True) for i in AB_LIST])

@route('all/*')
def SHOW_AB_LISTING(payload):
    assert payload in AB_LIST, "Bad Param"
    return draw_items(AnimeramBrowser().get_anime_list(payload))

@route('play/*')
def PLAY(url):
    s = SourcesList(AnimeramBrowser().get_episode_sources(url))
    return xbmc_play_source(s.get_video_link())

@route('')
def LIST_MENU(payload):
    return draw_items([allocate_item(name, url, True) for name, url in MENU_ITEMS])

router_process(get_plugin_url())
xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

from resources.lib import control
from resources.lib.SourcesList import SourcesList
from resources.lib.router import route, router_process
from resources.lib.AnimeramBrowser import AnimeramBrowser

AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z")+1)]
MENU_ITEMS = [
    (control.lang(30000), "latest"),
    (control.lang(30001), "all"),
    (control.lang(30002), "search")
]

@route('animes/*')
def ANIMES_PAGE(animeurl):
    return control.draw_items(AnimeramBrowser().get_anime_episodes(animeurl))

@route('latest')
def LATEST(payload):
    return control.draw_items(AnimeramBrowser().get_latest())

@route('search')
def SEARCH(payload):
    query = control.keyboard(control.lang(30002))
    if query:
        return control.draw_items(AnimeramBrowser().search_site(query))
    return False

@route('all')
def LIST_ALL_AB(payload):
    return control.draw_items([control.allocate_item(i, "all/%s" % i, True) for i in AB_LIST])

@route('all/*')
def SHOW_AB_LISTING(payload):
    assert payload in AB_LIST, "Bad Param"
    return control.draw_items(AnimeramBrowser().get_anime_list(payload))

@route('play/*')
def PLAY(url):
    s = SourcesList(AnimeramBrowser().get_episode_sources(url))
    return control.play_source(s.get_video_link())

@route('')
def LIST_MENU(payload):
    return control.draw_items([control.allocate_item(name, url, True) for name, url in MENU_ITEMS])

router_process(control.get_plugin_url())

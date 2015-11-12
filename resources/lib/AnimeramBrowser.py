import re
import urllib2
import urllib
from resources.lib import control

class AnimeramBrowser(object):
    _BASE_URL = "http://www.animeram.me"
    _RELEVANT_RESULTS_RE = re.compile("<div\sclass=\"popular\sfull\">\s<table.+?>(.+?)</table>", re.DOTALL)
    _SEARCH_IMAGE_RE = re.compile("<img\ssrc=\"(.+?)\"", re.DOTALL)
    _NAME_LINK_RE = re.compile("<h3><a\shref=\"%s/(.+?)/\">(.+?)</a></h3>" % _BASE_URL, re.DOTALL)
    _LATEST_LINK_RE = re.compile("<a\shref=\"%s/([-\w\s\d]+?)/(\d+?)/\".+?rel=\"(\d+)\".+?><strong>(.+?)</strong></a>" % _BASE_URL, re.DOTALL)
    _EPISODE_LINK_RE = re.compile("<a\shref=\"%s/([-\w\s\d]+?)/(\d+?)/\"><strong>(.+?)</strong></a>\s:\s(.*?)</div>" % _BASE_URL, re.DOTALL)
    _ANIME_LIST_RESULTS_RE = re.compile("<a\shref=\"%s/([-\w\s\d]+?)/\".+?rel=\"(\d+)\".+?>(.+?)</a>" % _BASE_URL, re.DOTALL)
    _NEWMANGA_CONT_RE = re.compile("<ul\sclass=\"newmanga\">(.+?)</ul>", re.DOTALL)
    _INFO_IMG_RE = re.compile("<img class=\"cvr\" src=\"(.+?)\"", re.DOTALL)

    _PLAYER_SOURCES_UL_RE = re.compile("<ul class=\"video.+?\".+?>(.+?)</ul>", re.DOTALL)

    def __init__(self):
        pass

    def _to_url(self, url=''):
        return "%s/%s" % (self._BASE_URL, url)

    def _extract_info(self, anime_ref):
        def f(anime_ref):
            res = {'image': ''}
            info = self._get_request(self._to_url("wpa-ajx/anm-det-pop/?anm=" + anime_ref))
            image = self._INFO_IMG_RE.findall(info)
            if len(image) > 0:
                res['image'] = image[0]
            return res
        return control.cache(f, anime_ref)

    def _post_request(self, url, data={}):
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        response_content = response.read()
        response.close()
        return response_content

    def _get_request(self, url):
        response = urllib2.urlopen(url)
        resp = response.read()
        response.close()
        return resp

    def _parse_search_result(self, res):
        image = self._SEARCH_IMAGE_RE.findall(res)[0]
        url, name = self._NAME_LINK_RE.findall(res)[0]
        return control.allocate_item(name, "animes/" + url + "/", True, image)
    
    def search_site(self, search_string):
        print search_string
        results = self._post_request("http://www.animeram.me/anime-list/search/",
                {"cmd_wpa_wgt_anm_sch_sbm": "Search", "txt_wpa_wgt_anm_sch_nme": search_string})
        all_results = []
        for result in self._RELEVANT_RESULTS_RE.findall(results):
            all_results.append(self._parse_search_result(result))
        return all_results

    def get_latest(self):
        resp = self._get_request(self._to_url())
        resp = self._NEWMANGA_CONT_RE.findall(resp)[0]

        results = []
        for res in self._LATEST_LINK_RE.findall(resp):
            image = self._extract_info(res[2])['image']
            name = res[3]
            results.append(control.allocate_item(name, "play/" + res[0] + "/" + res[1], False, image))
        return results

    def get_anime_episodes(self, anime_url):
        resp = self._get_request(self._to_url(anime_url))
        resp = self._NEWMANGA_CONT_RE.findall(resp)[0]

        results = []
        for res in self._EPISODE_LINK_RE.findall(resp):
            ep_name = res[3].strip()
            if len(ep_name):
                name = "%s : %s" % (res[2] , ep_name)
            else:
                name = res[2]
            print name
            results.append(control.allocate_item(name, "play/" + res[0] + "/" + res[1], False, ''))
        return results

    def get_episode_sources(self, episode_url):
        animeram_url = self._to_url(episode_url)
        resp = self._get_request(animeram_url)
        sources =  self._PLAYER_SOURCES_UL_RE.findall(resp)[1]
        link_regex = re.compile("<a href=\"%s/(\d+)/\">(.+?)</a>" % animeram_url, re.DOTALL)
        return [(res[1], "%s/%s" % (animeram_url, res[0])) for res in link_regex.findall(sources)]

    def get_anime_list(self, letter):
        filter_regx = re.compile("<a\sname=\"%s\"></a>\s<div\sclass=\"series_alpha\">(.+?)</div>\s</div>" % letter, re.DOTALL)
        resp = self._get_request(self._to_url("anime-list-all"))
        filtered = filter_regx.findall(resp)[0]

        results = []
        for res in self._ANIME_LIST_RESULTS_RE.findall(filtered):
            info = self._extract_info(res[1])
            results.append(control.allocate_item(res[2], "animes/" + res[0] + "/", True, info['image']))

        return results


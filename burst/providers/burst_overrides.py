# -*- coding: utf-8 -*-
"""
Default Burst overrides

.. data:: overrides

    Default overrides dictionary
"""

def source():
    """ See source

    Note:
        This just a dummy method for documentation
    """
    return repr(overrides)


overrides = {
    #
    # Public trackers
    #

    # Rutor
    'rutor': {
        'anime_query': "0/10/300/2/QUERYEXTRA",
        'movie_query': "0/0/300/2/QUERYEXTRA",
        'season_query': "0/4/300/2/QUERYEXTRA",
        'show_query': "0/4/300/2/QUERYEXTRA",
        'season_keywords': "{title} {season:2}x01|S{season:2}",
        'season_keywords2': "",
        'tv_keywords': '{title} s{season:2}e{episode:2}',
        'tv_keywords2': '{title} {season:2}x01|S{season:2}',
        'parser': {
            'row': "find_once('table', order=3).find_all('tr', start=2)",
            'seeds': "item(tag='span', order=1, select=('class', 'green'))",
            'peers': "item(tag='span', order=1, select=('class', 'red'))",
            'size': "item.find_all('td', ('align', 'right'))[-1].text()",
            'torrent': "'http://rutor.info%s' % (item(tag='a', order=1, attribute='href').split('.info', 1)[-1])"
        }
    }
}

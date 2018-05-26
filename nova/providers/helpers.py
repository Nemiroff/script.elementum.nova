# -*- coding: utf-8 -*-
"""
Helpers for providers that need special filtering
"""


# T411
def t411season(season):
    real_s = season + 967
    if season == 25:
        real_s = 994
    if 25 < season < 28:
        real_s = season + 966
    return real_s


def t411episode(episode):
    real_ep = 936
    if 8 < episode < 31:
        real_ep = episode + 937
    if 30 < episode < 61:
        real_ep = episode + 1057
    return real_ep

def fix_lf(url):
    url = url.replace('marvel_s_', '')
    url = url.replace('dc_s_', '')
    url = url.replace('s_h_i_e_l_d', 'shield')
    url = url.replace('_s_', 's_')
    return url

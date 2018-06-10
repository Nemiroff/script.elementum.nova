# -*- coding: utf-8 -*-
"""
Helpers for providers that need special filtering
"""

def fix_lf(url):
    url = url.replace('marvel_s_', '')
    url = url.replace('dc_s_', '')
    url = url.replace('s_h_i_e_l_d', 'shield')
    url = url.replace('_s_', 's_')
    url = url.replace('cloak_dagger', 'cloak_and_dagger')
    return url

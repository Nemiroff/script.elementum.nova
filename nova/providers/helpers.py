# -*- coding: utf-8 -*-
"""
Helpers for providers that need special filtering
"""

def fix_lf(url):
    url = url.replace('marvel\'s_', '').replace('dc\'s_', '').replace('s_h_i_e_l_d', 'shield').replace('\'s_', 's_').replace('cloak_dagger', 'cloak_and_dagger')
    return url

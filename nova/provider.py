# -*- coding: utf-8 -*-

"""
Provider thread methods
"""

import os
import re
import urllib
import xbmc
from client import Client
from elementum.provider import log, get_setting
from providers.definitions import definitions, longest
from utils import ADDON_PATH, get_int, clean_size, get_alias, notify, translation, get_icon_path
from providers.helpers import fix_lf

def generate_payload(provider, generator, filtering, verify_name=True, verify_size=True):
    """ Payload formatter to format results the way Elementum expects them

    Args:
        provider        (str): Provider ID
        generator  (function): Generator method, can be either ``extract_torrents`` or ``extract_from_api``
        filtering (Filtering): Filtering class instance
        verify_name    (bool): Whether to double-check the results' names match the query or not
        verify_size    (bool): Whether to check the results' file sizes

    Returns:
        list: Formatted results
    """
    filtering.information(provider)
    results = []

    definition = definitions[provider]
    definition = get_alias(definition, get_setting("%s_alias" % provider))

    for name, info_hash, uri, size, seeds, peers in generator:
        size = clean_size(size)
        v_name = name if verify_name else filtering.title
        v_size = size if verify_size else None
        if filtering.verify(provider, v_name, v_size):
            item = {
                "name": name,
                "uri": uri,
                "info_hash": info_hash,
                "size": size,
                "seeds": get_int(seeds),
                "peers": get_int(peers),
                "language": definition["language"] if 'language' in definition else 'en',
                "provider": '[COLOR %s]%s[/COLOR]' % (definition['color'], definition['name']),
                "icon": os.path.join(ADDON_PATH, 'nova', 'providers', 'icons', '%s.png' % provider),
            }
            if (get_setting("sort_by_resolution", bool)):
                item.update({"resolution": get_int(filtering.determine_resolution(v_name)[7:-1])})
            results.append(item)
        else:
            log.debug(filtering.reason.encode('utf-8'))

    log.debug('>>>>>> %s would send %d torrents to Elementum <<<<<<<' % (provider, len(results)))

    return results


def process(provider, generator, filtering, has_special, verify_name=True, verify_size=True):
    """ Method for processing provider results using its generator and Filtering class instance

    Args:
        provider        (str): Provider ID
        generator  (function): Generator method, can be either ``extract_torrents`` or ``extract_from_api``
        filtering (Filtering): Filtering class instance
        has_special    (bool): Whether title contains special chars
        verify_name    (bool): Whether to double-check the results' names match the query or not
        verify_size    (bool): Whether to check the results' file sizes
    """
    log.debug("execute_process for %s with %s" % (provider, repr(generator)))
    definition = definitions[provider]
    definition = get_alias(definition, get_setting("%s_alias" % provider))

    client = Client(info=filtering.info)
    logged_in = False

    if get_setting('kodi_language', bool):
        kodi_language = xbmc.getLanguage(xbmc.ISO_639_1)
        if kodi_language:
            filtering.kodi_language = kodi_language
        language_exceptions = get_setting('language_exceptions')
        if language_exceptions.strip().lower():
            filtering.language_exceptions = re.split(r',\s?', language_exceptions)

    log.debug("[%s] Queries: %s" % (provider, filtering.queries))
    log.debug("[%s] Extras:  %s" % (provider, filtering.extras))

    for query, extra in zip(filtering.queries, filtering.extras):
        log.debug("[%s] Before keywords - Query: %s - Extra: %s" % (provider, repr(query), repr(extra)))
        if has_special:
            # Removing quotes, surrounding {title*} keywords, when title contains special chars
            query = re.sub("[\"']({title.*?})[\"']", '\\1', query)

        query = filtering.process_keywords(provider, query)
        extra = filtering.process_keywords(provider, extra)
        if 'charset' in definition and 'utf' not in definition['charset'].lower():
            try:
                query = urllib.quote(query.encode(definition['charset']))
                extra = urllib.quote(extra.encode(definition['charset']))
            except:
                pass

        log.debug("[%s] After keywords  - Query: %s - Extra: %s" % (provider, repr(query), repr(extra)))
        if not query:
            return filtering.results

        query = urllib.quote(query.encode('utf-8'))
        url_search = filtering.url.replace('QUERY', query)
        if extra:
            url_search = url_search.replace('EXTRA', extra)
        else:
            url_search = url_search.replace('EXTRA', '')
        url_search = url_search.replace(' ', definition['separator'])

        if 'post_data' in definition and not filtering.post_data:
            filtering.post_data = eval(definition['post_data'])

        # Creating the payload for POST method
        payload = dict()
        for key, value in filtering.post_data.iteritems():
            if 'QUERY' in value:
                payload[key] = filtering.post_data[key].replace('QUERY', query)
            else:
                payload[key] = filtering.post_data[key]

        # Creating the payload for GET method
        data = None
        if filtering.get_data:
            data = dict()
            for key, value in filtering.get_data.iteritems():
                if 'QUERY' in value:
                    data[key] = filtering.get_data[key].replace('QUERY', query)
                else:
                    data[key] = filtering.get_data[key]

        log.debug("-   %s query: %s" % (provider, repr(query)))
        log.debug("--  %s url_search before token: %s" % (provider, repr(url_search)))
        log.debug("--- %s using POST payload: %s" % (provider, repr(payload)))
        log.debug("----%s filtering with post_data: %s" % (provider, repr(filtering.post_data)))

        # Set search's "title" in filtering to double-check results' names
        if 'filter_title' in definition and definition['filter_title']:
            filtering.filter_title = True
            filtering.title = query

        if logged_in:
            log.info("[%s] Reusing previous login" % provider)
        elif 'private' in definition and definition['private']:
            username = get_setting('%s_username' % provider)
            password = get_setting('%s_password' % provider)

            if 'login_object' in definition and definition['login_object']:
                logged_in = False
                try:
                    login_object = definition['login_object'].replace('USERNAME', '"%s"' % username).replace('PASSWORD', '"%s"' % password)
                except Exception, e:
                    log.error("[{0}] Make login_object fail: {1}".format(provider, e))
                    return filtering.results

                # TODO generic flags in definitions for those...
                if provider == 'lostfilm':
                    client.open(definition['root_url'] + '/v_search.php?c=110&s=1&e=1')
                    if u'Вход. – LostFilm.TV.' in client.content:
                        pass
                    else:
                        log.info('[%s] Login successful' % provider)
                        logged_in = True

                if not logged_in and client.login(definition['root_url'] + definition['login_path'], eval(login_object), definition['login_failed']):
                    log.info('[%s] Login successful' % provider)
                    logged_in = True
                elif not logged_in:
                    log.error("[%s] Login failed: %s", provider, client.status)
                    log.debug("[%s] Failed login content: %s", provider, repr(client.content))
                    notify(translation(32089).format(provider), image=get_icon_path())
                    return filtering.results

                if logged_in:
                    if provider == 'lostfilm':
                        log.info('[%s] Search lostfilm serial ID...', provider)
                        url_search = fix_lf(url_search)
                        client.open(url_search.encode('utf-8'), post_data=payload, get_data=data)
                        series_details = re.search(r'"mark-rate-pane" rel="(\d+),(\d+),(\d+)">', client.content)
                        if series_details:
                            client.open(definition['root_url'] + '/v_search.php?a=%s%s%s' % (series_details.group(1), series_details.group(2).zfill(3), series_details.group(3).zfill(3)))
                            redirect_url = re.search(ur'url=(.*?)">', client.content)
                            if redirect_url is not None:
                                url_search = redirect_url.group(1)
                        else:
                            log.info('[%s] Not found ID in %s' % (provider, url_search))
                            return filtering.results

        log.info(">  %s search URL: %s" % (definition['name'].rjust(longest), url_search))

        client.open(url_search, post_data=payload, get_data=data)
        filtering.results.extend(
            generate_payload(provider,
                             generator(provider, client),
                             filtering,
                             verify_name,
                             verify_size))
    return filtering.results

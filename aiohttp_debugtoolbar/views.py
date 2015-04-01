import aiohttp_mako
from .utils import TEMPLATE_KEY, APP_KEY, ROOT_ROUTE_NAME, STATIC_ROUTE_NAME, \
    STATIC_PATH


@aiohttp_mako.template('toolbar.dbtmako', app_key=TEMPLATE_KEY)
def request_view(request):
    settings = request.app[APP_KEY]['settings']
    history = request.app[APP_KEY]['request_history']

    try:
        last_request_pair = history.last(1)[0]
    except IndexError:
        last_request_id = None
    else:
        last_request_id = last_request_pair[0]

    request_id = request.match_info.get('request_id', last_request_id)

    toolbar = history.get(request_id, None)

    panels = toolbar.panels if toolbar else []
    global_panels = toolbar.global_panels if toolbar else []

    static_path = request.app.router[STATIC_ROUTE_NAME].url(filename='')
    root_path = request.app.router[ROOT_ROUTE_NAME].url()

    button_style = settings.get('button_style', '')
    max_visible_requests = settings['max_visible_requests']

    hist_toolbars = history.last(max_visible_requests)

    return {'panels': panels,
            'static_path': static_path,
            'root_path': root_path,
            'button_style': button_style,
            'history': hist_toolbars,
            'global_panels': global_panels,
            'request_id': request_id,
            'request': toolbar.request if toolbar else None
            }

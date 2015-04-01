from urllib.parse import unquote as url_unquote
from .utils import replace_insensitive, STATIC_ROUTE_NAME, APP_KEY


html_types = ('text/html', 'application/xhtml+xml')

class DebugToolbar(object):

    def __init__(self, request, panel_classes, global_panel_classes):
        self.panels = []
        self.global_panels = []
        self.request = request
        self.status = 200

        # Panels can be be activated (more features) (e.g. Performace panel)
        pdtb_active = url_unquote(request.cookies.get('pdtb_active', ''))

        activated = pdtb_active.split(';')
        # XXX
        for key, panel_class in panel_classes.items():
            panel_inst = panel_class(request)
            if panel_inst.dom_id in activated and panel_inst.has_content:
                panel_inst.is_active = True
            self.panels.append(panel_inst)

        for key, panel_class in global_panel_classes.items():
            panel_inst = panel_class(request)
            if panel_inst.dom_id in activated and panel_inst.has_content:
                panel_inst.is_active = True
            self.global_panels.append(panel_inst)

    @property
    def json(self):
        return {'method': self.request.method,
                'path': self.request.path,
                'scheme': 'http',
                'status_code': self.status}

    def process_response(self, request, response):
        # if isinstance(response, WSGIHTTPException):
        #   # the body of a WSGIHTTPException needs to be "prepared"
            # response.prepare(request.environ)
        for panel in self.panels:
            panel.process_response(response)
        for panel in self.global_panels:
            panel.process_response(response)

    def inject(self, request, response):
        """
        Inject the debug toolbar iframe into an HTML response.
        """
        # called in host app
        settings = request.app[APP_KEY]['settings']
        response_html = response.body
        route =  request.app.router['debugtoolbar.request']
        toolbar_url = route.url(parts={'request_id':request['id']})

        button_style = settings['button_style']

        css_path = request.app.router[STATIC_ROUTE_NAME].url(
            filename='css/toolbar_button.css')

        toolbar_html = toolbar_html_template % {
            'button_style': button_style,
            'css_path': css_path,
            'toolbar_url': toolbar_url}

        toolbar_html = toolbar_html.encode(response.charset or 'utf-8')
        response.body = replace_insensitive(
            response_html, b'</body>',
            toolbar_html + b'</body>'
            )

toolbar_html_template = """\
<script type="text/javascript">
    var fileref=document.createElement("link")
    fileref.setAttribute("rel", "stylesheet")
    fileref.setAttribute("type", "text/css")
    fileref.setAttribute("href", "%(css_path)s")
    document.getElementsByTagName("head")[0].appendChild(fileref)
</script>

<div id="pDebug">
    <div style="display: block; %(button_style)s" id="pDebugToolbarHandle">
        <a title="Show Toolbar" id="pShowToolBarButton"
           href="%(toolbar_url)s" target="pDebugToolbar">&#171; FIXME: Debug Toolbar</a>
    </div>
</div>
"""

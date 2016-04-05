from math import ceil

from flask_nav.elements import *
from flask_login import current_user
from hashlib import sha1
from dominate import tags
from flask_bootstrap.nav import BootstrapRenderer
from app.localization import localization


loc = localization()


class Rightbar(Subgroup):
    pass


def top_nav(sfilter='all', ufilter=None):
    navbar = [View(loc['home'], 'index'),
              View(loc['contacts'], 'contacts')]

    if current_user.is_authenticated:
        add = [Separator(), View(loc['fclear'], 'spectras', sfilter=sfilter)] if ufilter else []
        sg = Subgroup(loc['spectras'],
                      View(loc['all'], 'spectras', sfilter='all', user=ufilter or None),
                      View(loc['new'], 'spectras', sfilter='new', user=ufilter or None),
                      View(loc['cmp'], 'spectras', sfilter='cmp', user=ufilter or None),
                      *add)
        rg = Rightbar(current_user.name, View(loc['profile'], 'user', name=current_user.get_login()),
                      View(loc['logout'], 'logout'))
        navbar.append(sg)
        navbar.append(View(loc['newtask'], 'newtask'))

    else:
        rg = Rightbar(loc['anon'], View(loc['login'], 'login'), Separator(), Text(loc['doreg']),
                      View(loc['registration'], 'registration'))
    navbar.append(rg)
    return Navbar(loc['project'], *navbar)


class Customrenderer(BootstrapRenderer):
    def __init__(self, **kwargs):
        BootstrapRenderer.__init__(self)

    def visit_Navbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = 'navbar navbar-default'

        cont = root.add(tags.div(_class='container'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav'))
        right_bar_list = None

        for item in node.items:
            if type(item).__name__ == 'Rightbar':
                if right_bar_list is None:
                    right_bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))
                right_bar_list.add(self.visit(item))
            else:
                bar_list.add(self.visit(item))

        return root


class Pagination(object):
    def __init__(self, page, total_count, pagesize=50):
        self.per_page = pagesize
        self.total_count = total_count or 1
        self.page = page if total_count >= (page - 1) * pagesize else self.pages

    @property
    def pages(self):
        return int(ceil(self.total_count / self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1

    @property
    def offset(self):
        return (self.page - 1) * self.per_page

    def iter_pages(self):
        return range(1, self.pages + 1)

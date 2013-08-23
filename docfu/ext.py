import jinja2
import jinja2.ext

import markdown as md

markd = md.Markdown(extensions=[
    'attr_list', 'fenced_code', 'smart_strong', 'tables', 'codehilite',
    'headerid', 'sane_lists', 'wikilinks', 'smartypants'],
    output_format='html5')

render_markdown = lambda text: markd.convert(text)


def markup(text, *args, **kwargs):
    return render_markdown(text)


class MarkdownJinja(jinja2.ext.Extension):
    """ Add markdown support to Jinja2 templates.

    Usage:

        {% markdown %}
        Hello world
        ===========

        1. One
        2. Two
        3. Three

            public void main(String[] args) {
                // ...
            }
        {% endmarkdown %}
    """

    tags = set(['markdown'])

    def __init__(self, environment):
        super(MarkdownJinja, self).__init__(environment)
        environment.extend(markdowner=markd)
        environment.filters['markdown'] = markup

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(
            ['name:endmarkdown'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_markdown_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _markdown_support(self, caller):
        return self.environment.markdowner.convert(caller()).strip()

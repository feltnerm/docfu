import jinja2
import jinja2.ext

import markdown as md 

render_markdown = lambda text: md.markdown(text, ['extra', 'tables', 
    'codehilite(force_linenos=True)', 'headerid', 'nl2br', 'sane_lists', 
    'wikilinks', 'smartypants'])

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
        environment.extend(
            markdowner=md.Markdown(
                extras=[
                    'extra',
                    'tables', 
                    'codehilite(force_linenos=True)',
                    'headerid',
                    'nl2br',
                    'sane_lists',
                    'wikilinks'
                    'smartypants',
                ]))   

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




=====
docfu
=====

    | Shaolin shadowboxing, and the docfu sword style
    | If what you say is true, the Shaolin and the docfu could be dangerous.*
    | Do you think your docfu sword can defeat me?*
    | En garde, I'll let you try my docfu style.*


docfu will split your docs like a razor. If that razor could let you write documentation in markdown, AND Jinja, AND html.
Basically, it'll treat a folder as Jinaj2 templates (with extensions!) and deep copy it while converting each "template"
to valid HTML. That means you get the decreased verbosity of Markdown and the extensibility of a *real* templating engine.

Another cool feature is that docfu will automatically clone the branch or tag of the repository you give it. This makes it
a great tool for a git post-commit hook or as just a regular ol' documentation generator.

docfu is at most alpha status right now. Please post ideas and bugs to the `issue tracker`_.

.. _issue tracker: https://github.com/feltnerm/docfu/issues

Contributions are welcome as well!

Installation:
-------------

    *DUH-DUH-DUH...enter the docfu zone ...*

::

    % git clone https://github.com/feltnerm/docfu
    % cd docfu
    % python setup.py install

Usage: 
------

   | The game of chess is like a swordfight
   | You must think first before you move
   | Toad style is immensely strong and immune to nearly any weapon
   | When it's properly used it's almost invincible

::

    docfu [-h] [-b BRANCH] [-t TAG] [-s SUB_DIR] uri destination

    positional arguments:
    uri                   A URI pointing to a file path, git repository, or
                          github shortened repo.
    destination           Destination for compiled source.

    optional arguments:
      -h, --help            show this help message and exit
      -b BRANCH, --branch BRANCH
                            A git branch to checkout.
      -t TAG, --tag TAG     A git tag to checkout.
      -s SUB_DIR, --sub-dir SUB_DIR
                            Sub-directory which to compile from.
                            
Examples:
---------

   | Straight from the slums of Shaolin
   | docfu Killa B'z on a swarm

Using a git repository url:
~~~~~~~~~~~~~~~~~~~~~~~
``docfu "https://github.com/feltnerm/docfu" "/home/feltnerm/public_html/docs"```

Using a short GitHub url:
~~~~~~~~~~~~~~~~~~~~~~~~~
``docfu "feltnerm/docfu" "/home/feltnerm/public_html/docs"```

Specify a sub-directory:
~~~~~~~~~~~~~~~~~~~~~~~
``docfu  --sub-dir "docs/src" "feltnerm/docfu" "/home/feltnerm/public_html/docs"``

Docfu a specific tag
~~~~~~~~~~~~~~~~~~~~~~~
``docfu  --tag "0.1" --sub-dir "docs/src" "feltnerm/docfu" "/home/feltnerm/public_html/docs"``

Docfu a specific branch
~~~~~~~~~~~~~~~~~~~~~~~
``docfu  --branch "develop" --sub-dir "docs/src" "feltnerm/docfu" "/home/feltnerm/public_html/docs"``

*From the slums of Shaolin, Wu-Tang Clan strikes again*

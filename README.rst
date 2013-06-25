=====
docfu
=====

    Ruler Zig Zag, Zig-Allah jam is fatal
    
    Quick to stick my docfu sword right through ya navel
    
    Suspenseful, plus bein bought through my utensil
    
    The pencil, I break strong winds up against your
    
    Abbot, that run up through your county like the Maverick
    
    Caps through the tablets, I gots to make the fabrics
    
    
    ~ RZA "Wu-Tang: 7th Chamber"


docfu makes generating documentation from a git repository easy. You might find it useful if you have a git repository
and would like to generate documentation on a per-branch or -tag basis.

Usage: 
------

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

# encoding: latin2
print "ClusterPy: Library of spatially constrained clustering algorithms"

from core import *
from core import contiguity

__all__ = ['rimap','Layer','new','load','importArcData','createGrid',
           'createPoints','importShape','importDBF','importCSV','CPhelp']
__author__ = "Juan C. Duque (Owner), Boris Dev, Alejandro Betancourt, Jose L. Franco, Andres Cano"
__credits__ = "Copyright (c) 2010-11 Juan C. Duque"
__license__ = "New BSD License"
__version__ = "1.0.0"
__maintainer__ = "RiSE Group"
__email__ = "contacto@rise-group.org"

def CPhelp(function = ''):
    """ClusterPy's official help system

    **Callable functions are:**

        * new: creates an empty Layer.
        * load: load a ClusterPy project (<file>.CP).
        * importArcData: creates a new Layer from a shapefile (<file>.shp).
        * createPoints: creates a new Layer with points uniformly distributed on space.
        * createGrid: creates a new Layer with a regular lattice.
        * importShape: reads the geographic information stored on a shapefile.

    For more information about any function just type ''CPhelp('<function>')'' 
    or read the official documentation available on 'documentation <www.rise-group.org>'
    
    **Examples**

    To see the help of a class, in this case ''Layer'', type:
    
    >>> import clusterpy
    >>> clusterpy.CPhelp("Layer")

    For a specific function, just type the name of the function:

    **Example 1**
    
    >>> import clusterpy
    >>> clusterpy.CPhelp("importArcData")

    **Example 2**

    >>> import clusterpy
    >>> clusterpy.CPhelp("new")
    """
    if not function:
        print(CPhelp.__doc__)
    else:
        try:
            exec 'print('+ function + '.__doc__)'
        except:
            print "Invalid Function, to see available functions execute \
            'CPhelp()'"

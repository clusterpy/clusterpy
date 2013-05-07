from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

ALGPATH = "clusterpy/core/toolboxes/cluster/componentsAlg/"
ALGPKG = "clusterpy.core.toolboxes.cluster.componentsAlg."

CLUSPATH = "clusterpy/core/toolboxes/cluster/"
CLUSPKG = "clusterpy.core.toolboxes.cluster."


setup(
        name='clusterPy',
        version='0.9.9',
        description='Library of spatially constrained clustering algorithms',
        long_description="""
        clusterPy is a Python library with algorithms for spatially constrained clustering. clusterPy offers you some of the most cited algorithms for spatial aggregation.""",
        author='RiSE Group',
        author_email='software@rise-group.org',
        url='http://www.rise-group.org/section/Software/clusterPy/',
        packages=['clusterpy','clusterpy.core','clusterpy.core.data',
            'clusterpy.core.geometry','clusterpy.core.toolboxes',
                  'clusterpy.core.toolboxes.cluster',
                  'clusterpy.core.toolboxes.cluster.componentsAlg'],
        
        ext_modules = [Extension(CLUSPKG+"arisel", [CLUSPATH+"arisel.pyx"]),
                       Extension(ALGPKG+"distanceFunctions", [ALGPATH+"distanceFunctions.pyx"]),
		       Extension(ALGPKG+"dist2Regions", [ALGPATH+"dist2Regions.pyx"]),
		       Extension(ALGPKG+"selectionTypeFunctions", [ALGPATH+"selectionTypeFunctions.pyx"]),
                       Extension(ALGPKG+"init", [ALGPATH+"init.pyx"]),
                       Extension(ALGPKG+"objFunctions", [ALGPATH+"objFunctions.pyx"])
                       ],
        cmdclass = {'build_ext': build_ext}
        
        
        )

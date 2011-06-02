from distutils.core import setup

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
            'clusterpy.core.toolboxes.cluster.componentsAlg']
    )

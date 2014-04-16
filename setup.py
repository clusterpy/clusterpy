from distutils.core import setup
import sys

try:
  import numpy
  import scipy
except ImportError:
  sys.exit("install requires: 'numpy', 'scipy'")

# Polygon2 is actually optional
install_requires = ['numpy', 'scipy', 'Polygon2']
test_requires = ['nose']

setup(name = 'clusterpy',
  version = '0.10.0',
  description = 'Library of spatially constrained clustering algorithms',
  long_description = """
  clusterpy is a Python library with algorithms for spatially constrained
  clustering. clusterpy offers you some of the most cited algorithms for
  spatial aggregation.""",
  author = 'RiSE Group',
  author_email = 'software@rise-group.org',
  url = 'http://www.rise-group.org/section/Software/clusterPy/',

  test_suite = 'nose.collector',
  include_package_data = True,
  packages = [
    'clusterpy.core',
    'clusterpy.core.contiguity',
    'clusterpy.core.data',
    'clusterpy.core.geometry',
    'clusterpy.core.toolboxes',
    'clusterpy.core.toolboxes.cluster',
    'clusterpy.core.toolboxes.rimaps',
    'clusterpy.core.toolboxes.sstats',
    'clusterpy.core.toolboxes.cluster.componentsAlg',
    'clusterpy.core.toolboxes.sstats.basic',
    'clusterpy.core.toolboxes.sstats.inequality'
    ]
  )

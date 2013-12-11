ClusterPy
=========

Analytical regionalization is a scientific way to decide how to group of a large
number of geographic areas or points into a smaller number of regions based on
similiarities in one or more variables (e.g. income, ethnicity, or environmental
condition) that the researcher believes are important for the topic at hand.
Conventional conceptions of how areas should be grouped into regions may either
not be relevant to the information one is trying to illustrate (e.g. using
political regions to map air pollution) or may actually be designed in ways to
bias aggregated results.


Current algorithms
==================
 * AZP: Openshaw and Rao (1995)
 * AZP-Simulated Annealing: Openshaw and Rao (1995)
 * AZP-Tabu: Openshaw and Rao (1995)
 * AZP-R-Tabu: Openshaw and Rao (1995)
 * Max-p-regions (Greedy): Duque, Anselin and Rey (2010)
 * Max-p-regions (Tabu): Duque, Anselin and Rey (2010)
 * Max-p-regions (Simulated Annealing): Duque, Anselin and Rey (2010)
 * AMOEBA: Aldstadt and Getis (2006)
 * SOM: Kohonen (1990)
 * geoSOM: Bacao (2004)
 * Random

Special Features
================
 * Customized 'Analytical' Regionalizations based on following user
 specifications/inputs:
  * Key areal attribute to regionalize on: User regionalizes (or clusters) data
  based on different variables she considers important for her problem at hand.
  (i.e. use your own 'analytical' regions versus normative or administrative
  regions)
  * Maximum or minimum number of regions.
  * Threshold conditions of the maximum or minimum value that all regional
  clusters must meet for a given variable (e.g. a minimum threshold for a social
  or business project might be for all regions to have at least 100.000 people,
  or for an ecological project regions should have an area of at least 100
  square miles).
  * Spatial contiguity constraints (W matrix , GAL, GWT formats), or they will
  be created for you based the shared geographic borders of your areal units.
  * Time-series signature clustering: not only can areas by clustered by a
  cross-sectional variable, but also by the correlation of their time-series
  signatures of the variable.
 * Create New ESRI shapefiles:


Related information
===================
  * [Contribution guide](wiki/Contribution)
  * [Installation guide](wiki/Installation)
  * [Documentation](http://www.rise-group.org/risem/clusterpy/index.html)
  * [Development team](wiki/Team)

Citing Clusterpy
================
Please cite ClusterPy when using the software in your work

Duque, J.C.; Dev, B.; Betancourt, A.; Franco, J.L. (2011). ClusterPy: Librar
of spatially constrained clustering algorithms, Version 0.9.9. RiSE-group
(Research in Spatial Economics). EAFIT University. http://www.rise-group.org.

A BibTeX entry for LaTeX users is:
```
@Manual{ClusterPy,
title = {ClusterPy: {Library} of spatially constrained clustering algorithms,
{Version} 0.9.9.},
author = {Juan C. Duque and Boris Dev and Alejandro Betancourt and Jose L. Franco},
organization = {RiSE-group (Research in Spatial Economics). EAFIT University.},
address = {Colombia},
year = {2011},
url = {http://www.rise-group.org}
}
```

License information
===================
See the file "LICENSE.txt" for information on the history of this software, terms
& conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.

def showshape(shape, colorarray=None, colormap=None, alpha=None):
  """
  Creates and displays a firgure for the given shape using Matplotlib
  Parameters:
    [Shape] is a Clusterpy layer.
    [colorarray] is an array, with the same number of elements as areas in the
      layer, that is used to categorize the areas and set the color according to
      the value.
    [colormap] a string representing a Matplotlib's cmap name.
    [alpha] the alpha for the colors.

  Returns:
    A Matplotlib's figure.
  """
  return showshapes([shape], colorarray, colormap, alpha)

def showshapes(shapes, colorarray=None, colormap=None, alpha=None):
  """
  Creates and displays in a grid the group of shapes given.
  Parameters:
    [Shapes] a list of Clusterpy layers.
    [colorarray] is an array, with the same number of elements as areas in the
      layers, that is used to categorize the areas and set the color according to
      the value.
    [colormap] a string representing a Matplotlib's cmap name.
    [alpha] the alpha for the colors.

  Returns:
    A Matplotlib's grid of figures.
  """
  try:
    import matplotlib.patches as pts
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.collections import PatchCollection
  except ImportError:
    print "Matplotlib's pyplot patches and/or collections not found."
    return

  num_figs = len(shapes)
  x, y = 1, 1
  mult = 1
  if num_figs > 1:
    mult = 2
    if num_figs % 2 == 0:
        x, y = 2, max(2, num_figs/2)
    else:
        x, y = 3, max(2, int(np.ceil(num_figs/3.0)))

  fig = plt.figure(figsize=(8*mult, 6*mult), dpi=80)
  for pos, lay in enumerate(shapes):
    ax = plt.subplot(x, y, 1 + pos)
    patches = []
    for vertices in lay.areas:
        polygon = pts.Polygon(vertices[0], closed=True)
        patches.append(polygon)

    xmin, ymin, xmax, ymax = lay.getBbox()
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    cmap = plt.get_cmap('jet') if colormap is None else plt.get_cmap(colormap)
    calpha = 0.4 if alpha is None else alpha
    colors = []
    areas_count = len(patches)

    if colorarray is None:
      colors = 100 * np.random.rand(areas_count)
    else:
      if len(colorarray) != areas_count:
        raise Exception("The colorarray has to specify a value for one and only one area")
      colors = colorarray

    pcoll = PatchCollection(patches, cmap=cmap, alpha=calpha)
    pcoll.set_array(np.array(colors))
    ax.add_collection(pcoll)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
      spine.set_visible(False)
  plt.plot()

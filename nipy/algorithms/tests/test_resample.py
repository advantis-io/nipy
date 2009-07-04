import numpy as np

from nipy.testing import assert_true, assert_array_almost_equal

from nipy.core.api import (AffineTransform, Image,  
                           ArrayCoordMap, compose)
from nipy.core.reference import slices
from nipy.algorithms.resample import resample

# Hackish flag for enabling of pylab plots of resamplingstest_2d_from_3d
gui_review = False

def test_rotate2d():
    # Rotate an image in 2d on a square grid,
    # should result in transposed image
    
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.7,0.5,1]))
    g2 = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.7,1]))

    i = Image(np.ones((100,100)), g)
    i[50:55,40:55] = 3.

    a = np.array([[0,1,0],
                  [1,0,0],
                  [0,0,1]], np.float)

    ir = resample(i, g2, a, (100, 100))
    yield assert_array_almost_equal, np.asarray(ir).T, i


def test_rotate2d2():
    # Rotate an image in 2d on a non-square grid,
    # should result in transposed image
    
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.7,0.5,1]))
    g2 = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.7,1]))

    i = Image(np.ones((100,80)), g)
    i[50:55,40:55] = 3.

    a = np.array([[0,1,0],
                  [1,0,0],
                  [0,0,1]], np.float)

    ir = resample(i, g2, a, (80,100))
    yield assert_array_almost_equal, np.asarray(ir).T, i


def test_rotate2d3():
    # Another way to rotate/transpose the image, similar to
    # test_rotate2d2 and test_rotate2d except the output_coords of the
    # output coordmap are the same as the output_coords of the
    # original image. That is, the data is transposed on disk, but the
    # output coordinates are still 'x,'y' order, not 'y', 'x' order as
    # above

    # this functionality may or may not be used a lot. if data is to
    # be transposed but one wanted to keep the NIFTI order of output
    # coords this would do the trick

    g = AffineTransform.from_params('xy', 'ij', np.diag([0.5,0.7,1]))
    i = Image(np.ones((100,80)), g)
    i[50:55,40:55] = 3.

    a = np.identity(3)
    g2 = AffineTransform.from_params('xy', 'ij', np.array([[0,0.5,0],
                                                  [0.7,0,0],
                                                  [0,0,1]]))
    ir = resample(i, g2, a, (80,100))
    v2v = compose(g.inverse, g2)
    yield assert_array_almost_equal, np.asarray(ir).T, i
    

def test_rotate3d():
    # Rotate / transpose a 3d image on a non-square grid

    g = AffineTransform.from_params('ijk', 'xyz', np.diag([0.5,0.6,0.7,1]))
    g2 = AffineTransform.from_params('ijk', 'xyz', np.diag([0.5,0.7,0.6,1]))

    shape = (100,90,80)
    i = Image(np.ones(shape), g)
    i[50:55,40:55,30:33] = 3.
    
    a = np.array([[1,0,0,0],
                  [0,0,1,0],
                  [0,1,0,0],
                  [0,0,0,1.]])

    ir = resample(i, g2, a, (100,80,90))
    yield assert_array_almost_equal, np.transpose(np.asarray(ir), (0,2,1)), i


def test_resample2d():
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.5,1]))
    i = Image(np.ones((100,90)), g)
    i[50:55,40:55] = 3.
    
    # This mapping describes a mapping from the "target" physical
    # coordinates to the "image" physical coordinates.  The 3x3 matrix
    # below indicates that the "target" physical coordinates are related
    # to the "image" physical coordinates by a shift of -4 in each
    # coordinate.  Or, to find the "image" physical coordinates, given
    # the "target" physical coordinates, we add 4 to each "target
    # coordinate".  The resulting resampled image should show the
    # overall image shifted -8,-8 voxels towards the origin
    a = np.identity(3)
    a[:2,-1] = 4.
    ir = resample(i, i.coordmap, a, (100,90))
    yield assert_array_almost_equal, ir[42:47,32:47], 3.


def test_resample2d1():
    # Tests the same as test_resample2d, only using a callable instead of
    # an AffineTransform instance
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.5,1]))
    i = Image(np.ones((100,90)), g)
    i[50:55,40:55] = 3.
    a = np.identity(3)
    a[:2,-1] = 4.
    A = np.identity(2)
    b = np.ones(2)*4
    def mapper(x):
        return np.dot(x, A.T) + b
    ir = resample(i, i.coordmap, mapper, (100,90))
    yield assert_array_almost_equal, ir[42:47,32:47], 3.


def test_resample2d2():
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.5,1]))
    i = Image(np.ones((100,90)), g)
    i[50:55,40:55] = 3.
    a = np.identity(3)
    a[:2,-1] = 4.
    A = np.identity(2)
    b = np.ones(2)*4
    ir = resample(i, i.coordmap, (A, b), (100,90))
    yield assert_array_almost_equal, ir[42:47,32:47], 3.


def test_resample2d3():
    # Same as test_resample2d, only a different way of specifying
    # the transform: here it is an (A,b) pair
    g = AffineTransform.from_params('ij', 'xy', np.diag([0.5,0.5,1]))
    i = Image(np.ones((100,90)), g)
    i[50:55,40:55] = 3.
    a = np.identity(3)
    a[:2,-1] = 4.
    ir = resample(i, i.coordmap, a, (100,90))
    yield assert_array_almost_equal, ir[42:47,32:47], 3.
    

def test_resample3d():
    g = AffineTransform.from_params('ijk', 'xyz', np.diag([0.5,0.5,0.5,1]))
    shape = (100,90,80)
    i = Image(np.ones(shape), g)
    i[50:55,40:55,30:33] = 3.
    # This mapping describes a mapping from the "target" physical
    # coordinates to the "image" physical coordinates.  The 4x4 matrix
    # below indicates that the "target" physical coordinates are related
    # to the "image" physical coordinates by a shift of -4 in each
    # coordinate.  Or, to find the "image" physical coordinates, given
    # the "target" physical coordinates, we add 4 to each "target
    # coordinate".  The resulting resampled image should show the
    # overall image shifted [-6,-8,-10] voxels towards the origin
    a = np.identity(4)
    a[:3,-1] = [3,4,5]
    ir = resample(i, i.coordmap, a, (100,90,80))
    yield assert_array_almost_equal, ir[44:49,32:47,20:23], 3.


def test_nonaffine():
    # resamples an image along a curve through the image.
    #
    # FIXME: use the reference.evaluate.Grid to perform this nicer
    # FIXME: Remove pylab references
    def curve(x): # function accept N by 1, returns N by 2 
        return (np.vstack([5*np.sin(x.T),5*np.cos(x.T)]).T + [52,47])
    for names in (('xy', 'ij', 't', 'u'),('ij', 'xy', 't', 's')):
        in_names, out_names, tin_names, tout_names = names
        g = AffineTransform.from_params(in_names, out_names, np.identity(3))
        img = Image(np.ones((100,90)), g)
        img[50:55,40:55] = 3.
        tcoordmap = AffineTransform.from_start_step(
            tin_names,
            tout_names,
            [0],
            [np.pi*1.8/100])
        ir = resample(img, tcoordmap, curve, (100,))
    if gui_review:
        import pylab
        pylab.figure(num=3)
        pylab.imshow(img, interpolation='nearest')
        d = curve(np.linspace(0,1.8*np.pi,100))
        pylab.plot(d[0], d[1])
        pylab.gca().set_ylim([0,99])
        pylab.gca().set_xlim([0,89])
        pylab.figure(num=4)
        pylab.plot(np.asarray(ir))


def test_2d_from_3d():
    # Resample a 3d image on a 2d affine grid
    # This example creates a coordmap that coincides with
    # the 10th slice of an image, and checks that
    # resampling agrees with the data in the 10th slice.
    shape = (100,90,80)
    g = AffineTransform.from_params('ijk', 'xyz', np.diag([0.5,0.5,0.5,1]))
    i = Image(np.ones(shape), g)
    i[50:55,40:55,30:33] = 3.
    a = np.identity(4)
    g2 = ArrayCoordMap.from_shape(g, shape)[10]
    ir = resample(i, g2.coordmap, a, g2.shape)
    yield assert_array_almost_equal, np.asarray(ir), np.asarray(i[10])


def test_slice_from_3d():
    # Resample a 3d image, returning a zslice, yslice and xslice
    # 
    # This example creates a coordmap that coincides with
    # the 10th slice of an image, and checks that
    # resampling agrees with the data in the 10th slice.
    shape = (100,90,80)
    g = AffineTransform.from_params('ijk', 'xyz', np.diag([0.5,0.5,0.5,1]))
    i = Image(np.ones(shape), g)
    i[50:55,40:55,30:33] = 3
    a = np.identity(4)
    zsl = slices.zslice(26,
                        (0,44.5), (0,39.5),
                        i.coordmap.output_coords,
                        (90,80))
    ir = resample(i, zsl.coordmap, a, zsl.shape)
    yield assert_true, np.allclose(np.asarray(ir), np.asarray(i[53]))
    ysl = slices.yslice(22, (0,49.5), (0,39.5), i.coordmap.output_coords, (100,80))
    ir = resample(i, ysl.coordmap, a, ysl.shape)
    yield assert_true, np.allclose(np.asarray(ir), np.asarray(i[:,45]))
    xsl = slices.xslice(15.5, (0,49.5), (0,44.5), i.coordmap.output_coords, (100,90))
    ir = resample(i, xsl.coordmap, a, xsl.shape)
    yield assert_true, np.allclose(np.asarray(ir), np.asarray(i[:,:,32]))

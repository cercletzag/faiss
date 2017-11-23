# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD+Patents license found in the
# LICENSE file in the root directory of this source tree.

#! /usr/bin/env python2

import numpy as np

import faiss
import unittest


class TestClustering(unittest.TestCase):

    def test_clustering(self):
        d = 64
        n = 1000
        rs = np.random.RandomState(123)
        x = rs.uniform(size=(n, d)).astype('float32')

        km = faiss.Kmeans(d, 32, niter=10)
        err32 = km.train(x)

        # check that objective is decreasing
        prev = 1e50
        for o in km.obj:
            self.assertGreater(prev, o)
            prev = o

        km = faiss.Kmeans(d, 64, niter=10)
        err64 = km.train(x)

        # check that 64 centroids give a lower quantization error than 32
        self.assertGreater(err32, err64)

    def test_nasty_clustering(self):
        d = 2
        rs = np.random.RandomState(123)
        x = np.zeros((100, d), dtype='float32')
        for i in range(5):
            x[i * 20:i * 20 + 20] = rs.uniform(size=d)

        # we have 5 distinct points but ask for 10 centroids...
        km = faiss.Kmeans(d, 10, niter=10, verbose=True)
        km.train(x)

    def test_redo(self):
        d = 64
        n = 1000

        rs = np.random.RandomState(123)
        x = rs.uniform(size=(n, d)).astype('float32')

        clus = faiss.Clustering(d, 20)
        clus.nredo = 1
        clus.train(x, faiss.IndexFlatL2(d))
        obj1 = faiss.vector_to_array(clus.obj)

        clus = faiss.Clustering(d, 20)
        clus.nredo = 10
        clus.train(x, faiss.IndexFlatL2(d))
        obj10 = faiss.vector_to_array(clus.obj)

        self.assertGreater(obj1[-1], obj10[-1])



class TestPCA(unittest.TestCase):

    def test_pca(self):
        d = 64
        n = 1000
        np.random.seed(123)
        x = np.random.random(size=(n, d)).astype('float32')

        pca = faiss.PCAMatrix(d, 10)
        pca.train(x)
        y = pca.apply_py(x)

        # check that energy per component is decreasing
        column_norm2 = (y**2).sum(0)

        prev = 1e50
        for o in column_norm2:
            self.assertGreater(prev, o)
            prev = o


class TestProductQuantizer(unittest.TestCase):

    def test_pq(self):
        d = 64
        n = 1000
        cs = 4
        np.random.seed(123)
        x = np.random.random(size=(n, d)).astype('float32')
        pq = faiss.ProductQuantizer(d, cs, 8)
        pq.train(x)
        codes = pq.compute_codes(x)
        x2 = pq.decode(codes)
        diff = ((x - x2)**2).sum()

        # print "diff=", diff
        # diff= 1807.98
        self.assertGreater(2500, diff)


class TestRevSwigPtr(unittest.TestCase):

    def test_rev_swig_ptr(self):

        index = faiss.IndexFlatL2(4)
        xb0 = np.vstack([
            i * 10 + np.array([1, 2, 3, 4], dtype='float32')
            for i in range(5)])
        index.add(xb0)
        xb = faiss.rev_swig_ptr(index.xb.data(), 4 * 5).reshape(5, 4)
        self.assertEqual(np.abs(xb0 - xb).sum(), 0)


class TestException(unittest.TestCase):

    def test_exception(self):

        index = faiss.IndexFlatL2(10)

        a = np.zeros((5, 10), dtype='float32')
        b = np.zeros(5, dtype='int64')

        try:
            # an unsupported operation for IndexFlat
            index.add_with_ids(a, b)
        except RuntimeError as e:
            assert 'add_with_ids not implemented' in str(e)
        else:
            assert False, 'exception did not fire???'

    def test_exception_2(self):

        try:
            faiss.index_factory(12, 'IVF256,Flat,PQ8')
        except RuntimeError as e:
            assert 'could not parse' in str(e)
        else:
            assert False, 'exception did not fire???'

class TestMapLong2Long:

    def test_do_it(self):
        keys = np.array([13, 45, 67])
        vals = np.array([3, 8, 2])

        m = faiss.MapLong2Long()
        m.add(keys, vals)

        assert np.all(m.search_multiple(keys) == vals)

        assert m.search(12343) == -1


if __name__ == '__main__':
    unittest.main()

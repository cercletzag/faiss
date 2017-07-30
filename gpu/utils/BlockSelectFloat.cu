/**
 * Copyright (c) 2015-present, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD+Patents license found in the
 * LICENSE file in the root directory of this source tree.
 */

// Copyright 2004-present Facebook. All Rights Reserved.
#include "blockselect/BlockSelectImpl.cuh"

namespace faiss { namespace gpu {

// warp Q to thread Q:
// 1, 1
// 32, 2
// 64, 3
// 128, 3
// 256, 4
// 512, 8
// 1024, 8

BLOCK_SELECT_DECL(float, true, 1);
BLOCK_SELECT_DECL(float, true, 32);
BLOCK_SELECT_DECL(float, true, 64);
BLOCK_SELECT_DECL(float, true, 128);
BLOCK_SELECT_DECL(float, true, 256);
BLOCK_SELECT_DECL(float, true, 512);
BLOCK_SELECT_DECL(float, true, 1024);

BLOCK_SELECT_DECL(float, false, 1);
BLOCK_SELECT_DECL(float, false, 32);
BLOCK_SELECT_DECL(float, false, 64);
BLOCK_SELECT_DECL(float, false, 128);
BLOCK_SELECT_DECL(float, false, 256);
BLOCK_SELECT_DECL(float, false, 512);
BLOCK_SELECT_DECL(float, false, 1024);

void runBlockSelect(Tensor<float, 2, true>& in,
                  Tensor<float, 2, true>& outK,
                  Tensor<int, 2, true>& outV,
                  bool dir, int k, cudaStream_t stream) {
  FAISS_ASSERT(k <= 1024);

  if (dir) {
    if (k == 1) {
      BLOCK_SELECT_CALL(float, true, 1);
    } else if (k <= 32) {
      BLOCK_SELECT_CALL(float, true, 32);
    } else if (k <= 64) {
      BLOCK_SELECT_CALL(float, true, 64);
    } else if (k <= 128) {
      BLOCK_SELECT_CALL(float, true, 128);
    } else if (k <= 256) {
      BLOCK_SELECT_CALL(float, true, 256);
    } else if (k <= 512) {
      BLOCK_SELECT_CALL(float, true, 512);
    } else if (k <= 1024) {
      BLOCK_SELECT_CALL(float, true, 1024);
    }
  } else {
    if (k == 1) {
      BLOCK_SELECT_CALL(float, false, 1);
    } else if (k <= 32) {
      BLOCK_SELECT_CALL(float, false, 32);
    } else if (k <= 64) {
      BLOCK_SELECT_CALL(float, false, 64);
    } else if (k <= 128) {
      BLOCK_SELECT_CALL(float, false, 128);
    } else if (k <= 256) {
      BLOCK_SELECT_CALL(float, false, 256);
    } else if (k <= 512) {
      BLOCK_SELECT_CALL(float, false, 512);
    } else if (k <= 1024) {
      BLOCK_SELECT_CALL(float, false, 1024);
    }
  }
}

} } // namespace

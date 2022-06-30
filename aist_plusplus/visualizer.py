# coding=utf-8
# Copyright 2020 The Google AI Perception Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Visualize the AIST++ Dataset."""

from . import utils
import cv2
import numpy as np
from . import calculate_metric

_COLORS = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0],
           [170, 255, 0], [85, 255, 0], [0, 255, 0], [0, 255, 85],
           [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255],
           [0, 0, 255], [85, 0, 255], [170, 0, 255], [255, 0, 255],
           [255, 0, 170], [255, 0, 85]]


def plot_kpt(keypoint, canvas, color=None):
  for i, (x, y) in enumerate(keypoint[:, 0:2]):
    if np.isnan(x) or np.isnan(y) or x < 0 or y < 0:
      continue
    cv2.circle(canvas, (int(x), int(y)),
               7,
               color if color is not None else _COLORS[i % len(_COLORS)],
               thickness=-1)
  return canvas


def plot_on_video(keypoints2d, video_path, save_path, fps=60):
  assert len(keypoints2d.shape) == 3, (
      f'Input shape is not valid! Got {keypoints2d.shape}')
  video = utils.ffmpeg_video_read(video_path, fps=fps)
  for iframe, keypoint in enumerate(keypoints2d):
    if iframe >= video.shape[0]:
      break
    #video[iframe] = plot_kpt(keypoint, video[iframe])
    video[iframe] = draw_poses(keypoint, video[iframe])
    calculate_metric.angle_left_elbow(keypoint)
  utils.ffmpeg_video_write(video, save_path, fps=fps)


def draw_poses( poses, img, draw_ellipses=False):
    import cv2
    import numpy as np

    skeleton = ((15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11), (6, 12), (5, 6),
    (5, 7), (6, 8), (7, 9), (8, 10), (1, 2), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6))

    colors = (
        (255, 0, 0), (255, 0, 255), (170, 0, 255), (255, 0, 85),
        (255, 0, 170), (85, 255, 0), (255, 170, 0), (0, 255, 0),
        (255, 255, 0), (0, 255, 85), (170, 255, 0), (0, 85, 255),
        (0, 255, 170), (0, 0, 255), (0, 255, 255), (85, 0, 255),
        (0, 170, 255))
    
    if poses.size == 0:
        return img
    stick_width = 4

    img_limbs = np.copy(img)
    poses = poses.astype(int)
    for i, p in enumerate(poses):
        # Draw joints.
        cv2.circle(img, tuple(p), 1, colors[i], 2)
        # Draw limbs.
    for i, j in skeleton:
        if draw_ellipses:
            middle = (poses[i] + poses[j]) // 2
            vec = poses[i] - poses[j]
            length = np.sqrt((vec * vec).sum())
            angle = int(np.arctan2(vec[1], vec[0]) * 180 / np.pi)
            polygon = cv2.ellipse2Poly(tuple(middle), (int(length / 2), min(int(length / 50), stick_width)),
                                        angle, 0, 360, 1)
            cv2.fillConvexPoly(img_limbs, polygon, colors[j])
        else:
            cv2.line(img_limbs, tuple(poses[i]), tuple(poses[j]), color=colors[j], thickness=stick_width)

    for i in range(17):
        if i not in [1,2,3,4]:
            cv2.putText(img_limbs, str(i), tuple(poses[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
   
    cv2.addWeighted(img, 0.4, img_limbs, 0.6, 0, dst=img)
    #cv2.imwrite("test.png", img)
    return img



## test code  ##
# import cv2
# from  calculate_metric import angle_left_hand, angle_left_elbow, angle_right_elbow
# keypoints =[[896.,479.]
#  ,[907., 470.]
#  ,[890., 470.]
#  ,[924., 477.]
#  ,[883. ,475.]
#  ,[942. ,533.]
#  ,[866., 503.]
#  ,[966., 605.]
#  ,[816., 475.]
#  ,[968., 668.]
#  ,[762., 438.]
#  ,[901., 661.]
#  ,[859., 655.]
#  ,[844., 748.]
#  ,[859., 750.]
#  ,[842., 846.]
#  ,[933. ,796.]]
# keypoints = np.array(keypoints)
# angle_left_elbow(keypoints) #8
# angle_right_elbow(keypoints) #7
# angle_left_elbow(keypoints)  #13
# angle_right_elbow(keypoints) #14
# img = cv2.imread("origin.png")
# draw_poses(keypoints,img)

import os

from absl import app
from absl import flags
from aist_plusplus.loader import AISTDataset
import matplotlib.pyplot as plt
import numpy as np
from aist_plusplus import calculate_metric
import pandas as pd

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'anno_dir',
    '/home/ruilongli/data/AIST++/',
    'input local dictionary for AIST++ annotations.')
flags.DEFINE_string(
    'video_dir',
    '/home/ruilongli/data/AIST/videos/10M/',
    'input local dictionary for AIST Dance Videos.')
flags.DEFINE_string(
    'smpl_dir',
    '/home/ruilongli/data/smpl_model/smpl',
    'input local dictionary that stores SMPL data.')
flags.DEFINE_string(
    'video_name',
    'gBR_sBM_c01_d04_mBR0_ch01',
    'input video name to be visualized.')
flags.DEFINE_string(
    'save_dir',
    './',
    'output local dictionary that stores AIST++ visualization.')
flags.DEFINE_enum(
    'mode', '2D', ['2D', '3D', 'SMPL', 'SMPLMesh'],
    'visualize 3D or 2D keypoints, or SMPL joints on image plane.')

skeleton = ((15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11), (6, 12), (5, 6),
            (5, 7), (6, 8), (7, 9), (8, 10), (1, 2), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6))

colors_hex = ['#ff0000', '#ff00ff', '#aa00ff', '#ff0055', '#ff00aa', '#55ff00', '#ffaa00', '#00ff00', '#ffff00',
              '#00ff55', '#aaff00', '#0055ff', '#00ffaa', '#0000ff', '#00ffff', '#5500ff', '#00aaff']

info_color_idx_dict = {'height': 0,
                       'left_arm': 5, 'left_elbow': 7, 'left_leg_to_root': 11, 'left_leg_to_body': 11, 'left_knee': 13,
                       'right_arm': 6, 'right_elbow': 8, 'right_leg_to_root': 12, 'right_leg_to_body': 12,
                       'right_knee': 14,
                       'amplitude': 1,
                       'left_hand': 9, 'left_foot': 15, 'right_hand': 10, 'right_foot': 16}


def main(_):
    # Parsing data info.
    aist_dataset = AISTDataset(FLAGS.anno_dir)
    seq_name, view = AISTDataset.get_seq_name(FLAGS.video_name)

    os.makedirs(FLAGS.save_dir, exist_ok=True)
    save_path = os.path.join(FLAGS.save_dir, f'{FLAGS.video_name}')
    os.makedirs(save_path, exist_ok=True)
    end_frame = 100

    # Get 3D poses
    keypoints3d = AISTDataset.load_keypoint3d(
        aist_dataset.keypoint3d_dir, seq_name, use_optim=True)

    df = None
    for frame_no, keypoint in enumerate(keypoints3d):
        if frame_no >= end_frame:
            break
        pose_info_dict = calculate_metric.cal_pose_info(keypoint)
        df_per_frame = pd.DataFrame(pose_info_dict, index=[frame_no])
        if df is None:
            df = df_per_frame
        else:
            df = pd.concat([df, df_per_frame])
        drawOnePose(keypoints3d[frame_no], frame_no, save_path, pose_info_dict=pose_info_dict)
        print('frame: {}'.format(frame_no))

    pkl_file_path = os.path.join(save_path, 'pose_info_frame_{}.plk'.format(end_frame))
    df.to_pickle(pkl_file_path)
    csv_file_path = os.path.join(save_path, 'pose_info_frame_{}.csv'.format(end_frame))
    df.to_csv(csv_file_path)

    print('Done')


def drawOnePose(pose, frameNo, res_path, pose_info_dict=None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.ion()
    # ax.lines = []
    RADIUS = 100  # space around the subject
    draw3Dpose(pose, ax, radius=RADIUS)

    if pose_info_dict is not None:
        num = len(pose_info_dict)
        text_x = RADIUS
        text_y = range(RADIUS, -RADIUS, int(-2 * RADIUS / num))
        text_z = -RADIUS
        i = 0
        for name in pose_info_dict:
            value = pose_info_dict[name]
            color = colors_hex[info_color_idx_dict[name]]
            ax.text(text_x, text_y[i], text_z, '{}: {:.2f}'.format(name, value), color=color)
            i += 1

    filename = os.path.join(res_path, 'frame_{:03d}.jpg'.format(frameNo))
    plt.savefig(filename)
    # print("drawOnePose save to {}".format(filename))
    # plt.ioff()
    # plt.show()


def draw3Dpose(pose_3d, ax, radius=100):  # blue, orange
    for i, j in skeleton:
        x, y, z = [np.array([pose_3d[i, k], pose_3d[j, k]]) for k in range(3)]
        ax.plot(x, y, z, marker='o', markersize=1, lw=1.0, c=colors_hex[j])

    root_joint_idx = 12
    xroot, yroot, zroot = pose_3d[root_joint_idx, 0], pose_3d[root_joint_idx, 1], pose_3d[root_joint_idx, 2]
    ax.set_xlim3d([-radius + xroot, radius + xroot])
    ax.set_zlim3d([-radius + zroot, radius + zroot])
    ax.set_ylim3d([-radius + yroot, radius + yroot])

    ax.view_init(azim=0, elev=0, vertical_axis='y')

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")


if __name__ == '__main__':
    app.run(main)

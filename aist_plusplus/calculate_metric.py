import cv2
import numpy as np
import math
import os


def angle_between_points(p0, p1, p2):
    dimension = len(p0)
    a = 0
    b = 0
    c = 0
    for i in range(dimension):
        a += (p1[i] - p0[i]) ** 2
        b += (p1[i] - p2[i]) ** 2
        c += (p2[i] - p0[i]) ** 2
    # # 计算角度
    # a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    # b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    # c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
    if a * b == 0:
        return -1.0

    return math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180 / math.pi


def length_between_points(p0, p1):
    # 2点之间的距离
    return math.hypot(p1[0] - p0[0], p1[1] - p0[1])


def get_angle_point(human, pos):
    # 返回各个部位的关键点
    pnts = []

    if pos == 'left_elbow':
        pos_list = (5, 7, 9)
    elif pos == 'left_arm':  ##??
        pos_list = (7, 5, 11)
    elif pos == 'left_knee':
        pos_list = (11, 13, 15)
    elif pos == 'left_leg_to_root':  ##?
        pos_list = (12, 11, 13)
    elif pos == 'left_leg_to_body':  ##?
        pos_list = (5, 11, 13)
    elif pos == 'right_elbow':
        pos_list = (6, 8, 10)
    elif pos == 'right_arm':  # ??
        pos_list = (8, 6, 12)
    elif pos == 'right_knee':
        pos_list = (12, 14, 16)
    elif pos == 'right_leg_to_root':  # ??
        pos_list = (11, 12, 14)
    elif pos == 'right_leg_to_body':  # ??
        pos_list = (6, 12, 14)
    else:
        print('Unknown  [%s]', pos)
        return pnts

    for i in range(3):
        # if human[pos_list[i]][2] <= 0.1:
        #     print('component [%d] incomplete'%(pos_list[i]))
        #     return pnts
        if math.isnan(human[pos_list[i]][0]) or math.isnan(human[pos_list[i]][1]):
            return pnts
        pnts.append((int(human[pos_list[i]][0]), int(human[pos_list[i]][1])))
    return pnts


def cal_angle(human, angle_name):
    pnts = get_angle_point(human, angle_name)
    if len(pnts) != 3:
        print('component incomplete')
        return -1

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        # print('{}: {:.2f}'.format(angle_name, angle))
    return angle


def cal_height(human):
    nose_idx = 0
    y_nose = human[nose_idx][1]
    y_min = np.min(human[:, 1])
    height = y_nose - y_min
    # print('height: {:.2f}'.format(height))
    return height


def cal_distance(human, dis_name):
    if dis_name == 'left_hand':
        pnts = (5, 9)
    elif dis_name == 'left_foot':
        pnts = (11, 15)
    elif dis_name == 'right_hand':
        pnts = (6, 10)
    elif dis_name == 'right_foot':
        pnts = (12, 16)
    else:
        print(f'{dis_name} is not supported!')

    point1 = human[pnts[0]]
    point2 = human[pnts[1]]

    dis = 0
    for i in range(3):
        dis += math.pow((point1[i] - point2[i]), 2)
    dis = math.sqrt(dis)
    return dis


def cal_pose_info(human):
    # info_name_list = ['height',
    #                   'left_arm', 'left_elbow', 'left_leg_to_root', 'left_leg_to_body', 'left_knee',
    #                   'right_arm', 'right_elbow', 'right_leg_to_root', 'right_leg_to_body', 'right_knee', ]
    #
    # pose_info_dict = {}
    # for info_name in info_name_list:
    #     if info_name == 'height':
    #         value = cal_height(human)
    #     else:
    #         value = cal_angle(human, info_name)
    #     pose_info_dict[info_name] = value
    #
    # arm_angle = pose_info_dict['left_arm'] + pose_info_dict['right_arm']
    # elbow_angle = pose_info_dict['left_elbow'] + pose_info_dict['right_elbow']
    # leg_angle_to_root = pose_info_dict['left_leg_to_root'] + pose_info_dict['right_leg_to_root']
    # leg_angle_to_body = pose_info_dict['left_leg_to_body'] + pose_info_dict['right_leg_to_body']
    # knee_angle = pose_info_dict['left_knee'] + pose_info_dict['right_knee']
    # height = pose_info_dict['left_knee']
    #
    # w_arm = 1.0
    # w_elbow = 1.0
    # w_leg = 1.0
    # w_knee = 1.0
    # w_height = 1.0
    #
    # amplitude = w_arm * arm_angle + w_leg * leg_angle_to_root \
    #             + w_elbow * elbow_angle - w_leg * leg_angle_to_body - w_knee * knee_angle - w_height * height
    #
    # pose_info_dict['amplitude'] = amplitude

    angle_name_list = ['left_arm', 'left_leg_to_root', 'left_leg_to_body',
                       'right_arm', 'right_leg_to_root', 'right_leg_to_body']
    dis_name_list = ['left_hand', 'left_foot', 'right_hand', 'right_foot']

    arm_angle_base = 0
    leg_angle_to_root_base = 90
    leg_angle_to_body_base = 180

    pose_info_dict = {}
    for info_name in angle_name_list:
        if info_name == 'height':
            value = cal_height(human)
        else:
            value = cal_angle(human, info_name)
        pose_info_dict[info_name] = value

    for info_name in dis_name_list:
        value = cal_distance(human, info_name)
        pose_info_dict[info_name] = value

    arm_angle = (abs(pose_info_dict['left_arm'] - arm_angle_base) + \
                 abs(pose_info_dict['right_arm'] - arm_angle_base)) / 2
    leg_angle_to_root = (abs(pose_info_dict['left_leg_to_root'] - leg_angle_to_root_base) + \
                         abs(pose_info_dict['right_leg_to_root'] - leg_angle_to_root_base)) / 2
    leg_angle_to_body = (abs(pose_info_dict['left_leg_to_body'] - leg_angle_to_body_base) + \
                         abs(pose_info_dict['right_leg_to_body'] - leg_angle_to_body_base)) / 2
    leg_angle = (leg_angle_to_root + leg_angle_to_body) / 2

    hand_dis = (pose_info_dict['left_hand'] + pose_info_dict['right_hand']) / 2
    foot_dis = (pose_info_dict['left_foot'] + pose_info_dict['right_foot']) / 2

    w_angle_arm = 1.0
    w_angle_leg = 1.0
    w_dis_hand = 1.0
    w_dis_foot = 1.0

    amplitude = w_angle_arm * arm_angle + w_angle_leg * leg_angle \
                + w_dis_hand * hand_dis + w_dis_foot * foot_dis
    pose_info_dict['amplitude'] = amplitude

    return pose_info_dict


def angle_left_hand(human):
    pnts = get_angle_point(human, 'left_hand')
    if len(pnts) != 3:
        print('component incomplete')
        return -1

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left hand angle:%f' % (angle))
    return angle


def angle_left_elbow(human):
    pnts = get_angle_point(human, 'left_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left elbow angle:%f' % (angle))
    return angle


def angle_left_knee(human):
    pnts = get_angle_point(human, 'left_knee')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left knee angle:%f' % (angle))
    return angle


def angle_left_ankle(human):
    pnts = get_angle_point(human, 'left_ankle')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left ankle angle:%f' % (angle))
    return angle


def angle_right_hand(human):
    pnts = get_angle_point(human, 'right_hand')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right hand angle:%f' % (angle))
    return angle


def angle_right_elbow(human):
    pnts = get_angle_point(human, 'right_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right elbow angle:%f' % (angle))
    return angle


def angle_right_knee(human):
    pnts = get_angle_point(human, 'right_knee')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right knee angle:%f' % (angle))
    return angle


def angle_right_ankle(human):
    pnts = get_angle_point(human, 'right_ankle')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right ankle angle:%f' % (angle))
    return angle

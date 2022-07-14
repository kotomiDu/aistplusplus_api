import cv2
import numpy as np
import math
import os
def angle_between_points( p0, p1, p2 ):
    # 计算角度
    a = (p1[0]-p0[0])**2 + (p1[1]-p0[1])**2
    b = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
    c = (p2[0]-p0[0])**2 + (p2[1]-p0[1])**2
    if a * b == 0:
        return -1.0 

    return  math.acos( (a+b-c) / math.sqrt(4*a*b) ) * 180 /math.pi


def length_between_points(p0, p1):
    # 2点之间的距离
    if len(p0) == 2:
        return math.hypot(p1[0]- p0[0], p1[1]-p0[1])
    if len(p0) == 3:
        return (((p1[0]-p0[0])**2)+((p1[1]-p0[1])**2)+((p1[2]-p0[2])**2))**(1/2)

def get_angle_point(human, pos):
    # 返回各个部位的关键点
    pnts = []

    if pos == 'left_elbow':
        pos_list = (5,7,9)
    elif pos == 'left_hand': ##??
        pos_list = (1,5,7)
    elif pos == 'left_knee':
        pos_list = (12,14,15)
    elif pos == 'left_ankle': ##?
        pos_list = (5,12,14)
    elif pos == 'right_elbow':
        pos_list = (6,8,10)
    elif pos == 'right_hand': #??
        pos_list = (1,2,4)
    elif pos == 'right_knee':
        pos_list = (11,13,15)
    elif pos == 'right_ankle':  #??
        pos_list = (2,9,11)
    else:
        print('Unknown  [%s]', pos)
        return pnts

    for i in range(3):
        # if human[pos_list[i]][2] <= 0.1:
        #     print('component [%d] incomplete'%(pos_list[i]))
        #     return pnts
        if math.isnan(human[pos_list[i]][0]) or math.isnan(human[pos_list[i]][1]):
            return pnts
        pnts.append((int( human[pos_list[i]][0]), int( human[pos_list[i]][1])))
    return pnts


def angle_left_hand(human):
    pnts = get_angle_point(human, 'left_hand')
    if len(pnts) != 3:
        print('component incomplete')
        return -1

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left hand angle:%f'%(angle))
    return angle


def angle_left_elbow(human):
    pnts = get_angle_point(human, 'left_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left elbow angle:%f'%(angle))
    return angle


def angle_left_knee(human):
    pnts = get_angle_point(human, 'left_knee')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left knee angle:%f'%(angle))
    return angle


def angle_left_ankle(human):
    pnts = get_angle_point(human, 'left_ankle')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('left ankle angle:%f'%(angle))
    return angle


def angle_right_hand(human):
    pnts = get_angle_point(human, 'right_hand')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right hand angle:%f'%(angle))
    return angle


def angle_right_elbow(human):
    pnts = get_angle_point(human, 'right_elbow')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right elbow angle:%f'%(angle))
    return angle


def angle_right_knee(human):
    pnts = get_angle_point(human, 'right_knee')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right knee angle:%f'%(angle))
    return angle


def angle_right_ankle(human):
    pnts = get_angle_point(human, 'right_ankle')
    if len(pnts) != 3:
        print('component incomplete')
        return

    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
        print('right ankle angle:%f'%(angle))
    return angle

#legacy code by using opencv api
def motion_intensity(next_pose, prvs_pose):
    intensity = np.zeros(17)
    h,w = [1080,1920]
    flow= np.zeros((h,w,2))
    for i in range(17):
        joint_num = i
        pos_x = int(next_pose[joint_num][0])
        pos_y = int(next_pose[joint_num][1])
        if pos_x > w or pos_y > h or pos_x < 0 or pos_y < 0 or pos_x == w or pos_y == h or pos_x == 0 or pos_y == 0:
            print("invalid position: {0:5d}, {0:5d}".format(pos_x,pos_y))
        flow[pos_y,pos_x,:] = next_pose[joint_num] - prvs_pose[joint_num]
        #print(flow[int(next_pose[joint_num][0]),int(next_pose[joint_num][1]),:])

    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    
    for i in range(17):
        joint_num = i
        pos_x = int(next_pose[joint_num][0])
        pos_y = int(next_pose[joint_num][1])
        if pos_x > w or pos_y > h or pos_x < 0 or pos_y < 0 or pos_x == w or pos_y == h or pos_x == 0 or pos_y == 0:
            print("invalid position: {0:5d}, {0:5d}".format(pos_x,pos_y))
            continue
        intensity[i] = mag[pos_y,pos_x]
    
    return intensity

#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from laser_msgs.msg import PointArrayStamped
from mrs_msgs.msg import ReferenceStamped
from mrs_msgs.srv import ReferenceStampedSrv
from mrs_msgs.msg import Reference
import numpy as np
import math

last_reference = ReferenceStamped()
dx = 0
dy = 0
reference_stamped = ReferenceStamped()
flag = 0

def callback(data):
    global dx
    global dy
    global reference_stamped
    global flag

    # rospy.loginfo(rospy.get_caller_id() + "I heard %s", len(data.array))
    if len(data.array) > 0:
        rospy.wait_for_service('/uav1/control_manager/reference')
        try:
            desired_height = rospy.get_param("/uav1/stage_four/desired_height", 3.0)

            reference_srv = rospy.ServiceProxy('/uav1/control_manager/reference', ReferenceStampedSrv)

            if (flag >= 2):
                dx = data.array[0].x - reference_stamped.reference.position.x
                dy = data.array[0].y - reference_stamped.reference.position.y

            reference_stamped.header = data.header
            reference_stamped.reference.position.x = data.array[0].x
            reference_stamped.reference.position.y = data.array[0].y
            reference_stamped.reference.position.z = desired_height
            reference_stamped.reference.heading = 3.1415

            reference_srv(reference_stamped.header, reference_stamped.reference)

            if (flag < 2):
                flag = flag + 1

            angle = np.arctan2(dx, dy)
            print("angle: %.2f" % (math.degrees(angle)))

        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)
    else:

        desired_height = rospy.get_param("/uav1/stage_four/desired_height", 3.0)

        reference_srv = rospy.ServiceProxy('/uav1/control_manager/reference', ReferenceStampedSrv)

        #reference_stamped.header = rospy.get_rostime()
        reference_stamped.reference.position.z = desired_height
        reference_srv(reference_stamped.header, reference_stamped.reference)
        
    
def listener():
    rospy.init_node('platform_follower', anonymous=True)

    rospy.Subscriber("/uav1/lp_detector/detections", PointArrayStamped, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
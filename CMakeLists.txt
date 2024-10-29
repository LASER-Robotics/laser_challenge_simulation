cmake_minimum_required(VERSION 3.0.2)
project(laser_challenge_simulation)

find_package(catkin REQUIRED COMPONENTS
  rospy
  gazebo_ros
  gazebo_msgs
  mrs_gazebo_common_resources
)

catkin_package(
  CATKIN_DEPENDS rospy gazebo_ros
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS scripts/base_spawner.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

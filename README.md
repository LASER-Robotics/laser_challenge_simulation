# The LASER Challenge Simulation repository

This package contains the Gazebo files (models and worlds) related to the LASER UAV challenge.

## Models
- Arena
- Banner
- Barcode Shelf
- Landing Platform
- Measure Gas
- Pipe
- QR-Code Box
- Green Sensor
- Red Sensor
- Unit Box

## Worlds
- Stage One
- Stage Two
- Stage Three
- Stage Four
- Test


# Instructions for stage four tests

Dependencies:

- build and source the laser_challenge_simulation package
- [install turtlebot3 (ROS NOETIC)](https://automaticaddison.com/how-to-launch-the-turtlebot3-simulation-with-ros/) (build and source)
- download and build the [turtlebot3 figure eight package](https://github.com/ctsaitsao/turtlebot3-figure-eight)
- make sure to source and build the packages in the right order to get a proper [ros workspace chain](https://answers.ros.org/question/283343/how-do-i-prevent-workspace-chaining/)
- run the test code:

        roscd laser_challenge_simulation/tmux_scripts/stage_four
        ./start

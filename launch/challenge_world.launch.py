import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare

def _append_env(name, value):
    cur = os.environ.get(name, "")
    if cur:
        os.environ[name] = cur + ":" + value
    else:
        os.environ[name] = value

def generate_launch_description():
    pkg_share = FindPackageShare(package='laser_challenge_simulation').find('laser_challenge_simulation')
    world_gazebo_path = os.path.join(pkg_share, 'worlds/challenge_world.world')
    world_models_path = os.path.join(pkg_share, 'models')
    install_dir = pkg_share

    _append_env('GAZEBO_MODEL_PATH', world_models_path)
    _append_env('GAZEBO_MODEL_PATH', '/usr/share/gazebo-11/models')

    _append_env('GAZEBO_RESOURCE_PATH', '/usr/share/gazebo-11')
    _append_env('GAZEBO_RESOURCE_PATH', pkg_share)

    _append_env('GAZEBO_PLUGIN_PATH', os.path.join(install_dir, 'lib'))

    print("GAZEBO MODELS PATH==" + os.environ.get("GAZEBO_MODEL_PATH", ""))
    print("GAZEBO RESOURCE PATH==" + os.environ.get("GAZEBO_RESOURCE_PATH", ""))
    print("GAZEBO PLUGINS PATH==" + os.environ.get("GAZEBO_PLUGIN_PATH", ""))

    world_gazebo_arg = DeclareLaunchArgument(
        name="world",
        default_value=str(world_gazebo_path)
    )

    gazebo_launch = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            '-s', 'libgazebo_ros_factory.so',
            '-s', 'libgazebo_ros_init.so',
            LaunchConfiguration('world')
        ],
        output='screen'
    )

    return LaunchDescription([
        world_gazebo_arg,
        gazebo_launch,
    ])

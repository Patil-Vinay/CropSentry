import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_pkg = get_package_share_directory('cropsentry_description')
    gz_pkg = get_package_share_directory('cropsentry_gazebo')
    gazebo_ros = get_package_share_directory('gazebo_ros')

    xacro_file = os.path.join(desc_pkg, 'urdf', 'cropsentry.urdf.xacro')
    rviz_file = os.path.join(desc_pkg, 'rviz', 'display.rviz')
    default_world = os.path.join(gz_pkg, 'worlds', 'crop_field.world')

    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('rviz')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world}.items())

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=default_world),
        DeclareLaunchArgument('rviz', default_value='false'),

        gazebo,

        Node(package='robot_state_publisher',
             executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description,
                          'use_sim_time': True}]),

        # start a bit above the ground so the tracks don't spawn inside it
        Node(package='gazebo_ros',
             executable='spawn_entity.py',
             arguments=['-entity', 'cropsentry', '-topic', 'robot_description',
                        '-x', '0', '-y', '0', '-z', '0.02'],
             output='screen'),

        Node(package='rviz2',
             executable='rviz2',
             arguments=['-d', rviz_file],
             parameters=[{'use_sim_time': True}],
             condition=IfCondition(use_rviz)),
    ])

import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

import xacro


def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='test_machine' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                os.path.join(get_package_share_directory(package_name),'description','robot.urdf.xacro')
            ),
            " ",
        ]
    )

    robot_description_content = Command(
    [
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution(
            [FindPackageShare("test_machine"), 'description','robot.urdf.xacro']
        ),
        " ",
    ]
)

    
    robot_description = {"robot_description": robot_description_content}

    # robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])
    # robot_description = os.path.join(get_package_share_directory(package_name),'description','robot.urdf.xacro')

    # controller_params = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("test_machine"),
            "config",
            "my_controllers.yaml",
        ]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diffbot_controller",
            "--controller-manager",
            "/controller_manager",
        ]
    )

    # controller_manager = Node(
    #     package="controller_manager",
    #     executable="ros2_control_node",
    #     parameters=[{'robot_description': robot_description},
    #                 controller_params_file]
    # )



    # Launch them all!
    return LaunchDescription([
        rsp,
        control_node,
        robot_controller_spawner,
    ])
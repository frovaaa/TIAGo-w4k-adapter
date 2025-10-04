from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="dashboard_adapter",
                executable="adapter",
                name="dashboard_adapter",
                output="screen",
                parameters=[
                    {
                        "movement_topic": "/dashboard/movement",  # topic to listen for movement commands
                        "arm_topic": "/dashboard/arm",  # topic to listen for arm commands
                        "gripper_topic": "/dashboard/gripper",  # topic to listen for gripper commands
                        "play_motion_action": "/play_motion2",  # PlayMotion2 action server
                    }
                ],
            )
        ]
    )

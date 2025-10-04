#!/usr/bin/env python3
import rclpy, json
from abc import ABC, abstractmethod
from typing import Dict, Any, Union
from rclpy.node import Node
from rclpy.action import ActionClient

from std_msgs.msg import String
from play_motion2_msgs.action import PlayMotion2


# Action interface and implementations


class Action(ABC):
    """Base class for all dashboard actions"""

    def __init__(self, timestamp: float = 0.0) -> None:
        self.timestamp = timestamp

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """Create action from dictionary data"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Movement(Action):
    """Movement action with motion_name, speed, and timestamp"""

    def __init__(
        self, motion_name: str, speed: float = 0.0, timestamp: float = 0.0
    ) -> None:
        super().__init__(timestamp)
        self.motion_name = motion_name
        self.speed = speed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Movement":
        motion_name = data.get("motion_name", "")
        speed = float(data.get("speed", 0.0))
        timestamp = float(data.get("timestamp", 0.0))
        return cls(motion_name, speed, timestamp)

    def __str__(self) -> str:
        return f'motion_name="{self.motion_name}", speed={self.speed}, timestamp={self.timestamp}'


class Gripper(Action):
    """Gripper action with action, force, and timestamp"""

    def __init__(self, action: str, force: float = 0.0, timestamp: float = 0.0) -> None:
        super().__init__(timestamp)
        self.action = action
        self.force = force

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gripper":
        action = data.get("action", "")
        force = float(data.get("force", 0.0))
        timestamp = float(data.get("timestamp", 0.0))
        return cls(action, force, timestamp)

    def __str__(self) -> str:
        return f'action="{self.action}", force={self.force}, timestamp={self.timestamp}'


class Arm(Action):
    """Arm action with action, params (key-value), and timestamp"""

    def __init__(
        self, action: str, params: Dict[str, Any] | None = None, timestamp: float = 0.0
    ) -> None:
        super().__init__(timestamp)
        self.action = action
        self.params = params or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Arm":
        action = data.get("action", "")
        params = data.get("params", {})
        timestamp = float(data.get("timestamp", 0.0))
        return cls(action, params, timestamp)

    def __str__(self) -> str:
        return (
            f'action="{self.action}", params={self.params}, timestamp={self.timestamp}'
        )


class DashboardAdapter(Node):
    """
    Very simple adapter:
      - subscribes to a String topic (cmds like: 'home', 'pregrasp', ...)
      - sends a PlayMotion2 goal with motion_name=<string>
    """

    def __init__(self) -> None:
        super().__init__("dashboard_adapter")

        # Parameters
        self.declare_parameter("movement_topic", "/dashboard/movement")
        self.declare_parameter("arm_topic", "/dashboard/arm")
        self.declare_parameter("gripper_topic", "/dashboard/gripper")
        self.declare_parameter("play_motion_action", "/play_motion2")

        self.movement_topic: str = (
            self.get_parameter("movement_topic").get_parameter_value().string_value
        )
        self.arm_topic: str = (
            self.get_parameter("arm_topic").get_parameter_value().string_value
        )
        self.gripper_topic: str = (
            self.get_parameter("gripper_topic").get_parameter_value().string_value
        )
        action_name: str = (
            self.get_parameter("play_motion_action").get_parameter_value().string_value
        )

        # Subscribers
        self.movement_sub = self.create_subscription(
            String, self.movement_topic, self._movement_cmd_cb, 10
        )
        self.arm_sub = self.create_subscription(
            String, self.arm_topic, self._arm_cmd_cb, 10
        )
        self.gripper_sub = self.create_subscription(
            String, self.gripper_topic, self._gripper_cmd_cb, 10
        )

        # PlayMotion2 action client
        self.pm_client = ActionClient(self, PlayMotion2, action_name)

        self.get_logger().info(
            f"Listening for movement commands on: {self.movement_topic}"
        )
        self.get_logger().info(f"Listening for arm commands on: {self.arm_topic}")
        self.get_logger().info(
            f"Listening for gripper commands on: {self.gripper_topic}"
        )
        self.get_logger().info(f"PlayMotion2 action server: {action_name}")

    # ---- Callbacks ---------------------------------------------------------

    def _movement_cmd_cb(self, msg: String) -> None:
        action = self._parse_action(msg, Movement, "movement")
        if action and isinstance(action, Movement):
            self.get_logger().info(f'Requested movement: "{action}"')
            self._send_play_motion(action)

    def _arm_cmd_cb(self, msg: String) -> None:
        action = self._parse_action(msg, Arm, "arm")
        if action and isinstance(action, Arm):
            self.get_logger().info(f'Requested arm action: "{action}"')
            self._handle_arm_action(action)

    def _gripper_cmd_cb(self, msg: String) -> None:
        action = self._parse_action(msg, Gripper, "gripper")
        if action and isinstance(action, Gripper):
            self.get_logger().info(f'Requested gripper action: "{action}"')
            self._handle_gripper_action(action)

    def _parse_action(
        self, msg: String, action_class: type, command_type: str
    ) -> Union[Action, None]:
        raw_data = msg.data.strip()
        if not raw_data:
            self.get_logger().warn(f"Received empty {command_type} command; ignoring.")
            return None

        # Try to parse JSON string
        try:
            parsed_data = json.loads(raw_data)
            return action_class.from_dict(parsed_data)
        except json.JSONDecodeError:
            # For movement, assume it's a simple motion name
            if action_class == Movement:
                return Movement(motion_name=raw_data)
            # For arm/gripper, assume it's a simple action name
            elif action_class == Arm:
                return Arm(action=raw_data)
            elif action_class == Gripper:
                return Gripper(action=raw_data)
            else:
                self.get_logger().error(
                    f"Cannot parse {command_type} command: {raw_data}"
                )
                return None

    # ---- PlayMotion2 helpers ----------------------------------------------

    def _send_play_motion(self, movement: Movement) -> None:
        if not self.pm_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("PlayMotion2 server not available.")
            return

        goal = PlayMotion2.Goal()
        goal.motion_name = movement.motion_name
        # Note: speed and timestamp could be used for future PlayMotion2 enhancements

        self.get_logger().info(
            f'Sending PlayMotion2 goal: motion_name="{movement.motion_name}"'
        )
        future = self.pm_client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_cb)

    def _handle_arm_action(self, arm: Arm) -> None:
        # For now, treat arm actions as PlayMotion2 movements
        # In the future, this could be extended to handle more complex arm actions
        if arm.action:
            movement = Movement(motion_name=arm.action, timestamp=arm.timestamp)
            self._send_play_motion(movement)
        else:
            self.get_logger().warn("Arm action has no action name specified")

    def _handle_gripper_action(self, gripper: Gripper) -> None:
        # For now, treat gripper actions as PlayMotion2 movements
        # In the future, this could be extended to handle gripper-specific actions
        if gripper.action:
            movement = Movement(motion_name=gripper.action, timestamp=gripper.timestamp)
            self._send_play_motion(movement)
        else:
            self.get_logger().warn("Gripper action has no action name specified")

    def _goal_response_cb(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().warn("PlayMotion2 goal was rejected.")
            return

        self.get_logger().info("PlayMotion2 goal accepted.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_cb)

    def _result_cb(self, future) -> None:
        try:
            result = future.result().result
            # Different versions may expose fields like error_code / error_string
            self.get_logger().info(f"PlayMotion2 finished. Result: {result}")
        except Exception as e:
            self.get_logger().error(f"Error getting PlayMotion2 result: {e}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DashboardAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

# TIAGo Dashboard Adapter

A ROS 2 adapter package that enables PAL Robotics TIAGo robots to communicate with the XX Dashboard system. This adapter translates semantic dashboard commands into TIAGo-specific actions using the PlayMotion2 framework.

## Overview

The Dashboard Adapter serves as a bridge between the generic dashboard interface and TIAGo's robot-specific capabilities. It subscribes to semantic topics published by the dashboard and converts them into appropriate PlayMotion2 actions that TIAGo can execute.

## Features

- **Semantic Command Translation**: Converts dashboard semantic actions into TIAGo PlayMotion2 commands
- **Multi-Command Support**: Handles movement, arm, and gripper commands
- **JSON Parameter Support**: Accepts both simple string commands and complex JSON parameters

## Architecture

```
Dashboard → ROS Topics → Dashboard Adapter → PlayMotion2 → TIAGo Robot
```

### Supported Topics

| Topic                 | Message Type      | Description               |
| --------------------- | ----------------- | ------------------------- |
| `/dashboard/movement` | `std_msgs/String` | Robot movement commands   |
| `/dashboard/arm`      | `std_msgs/String` | Arm manipulation commands |
| `/dashboard/gripper`  | `std_msgs/String` | Gripper control commands  |

### Supported Action Servers

- `/play_motion2` - PAL Robotics PlayMotion2 action server

## Installation

### Prerequisites

- ROS 2 (Humble or later)
- PAL Robotics TIAGo robot setup
- PlayMotion2 package installed

### Build Instructions

1. Clone the repository into your ROS 2 workspace:

```bash
cd ~/ros2_ws/src
git clone <repository-url>
```

2. Install dependencies:

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

3. Build the package:

```bash
colcon build --packages-select dashboard_adapter
```

4. Source the workspace:

```bash
source install/setup.bash
```

## Usage

### Launch the Adapter

```bash
ros2 launch dashboard_adapter dashboard_adapter.launch.py
```

### Configuration Parameters

The adapter can be configured with the following parameters:

- `movement_topic` (default: `/dashboard/movement`) - Topic for movement commands
- `arm_topic` (default: `/dashboard/arm`) - Topic for arm commands
- `gripper_topic` (default: `/dashboard/gripper`) - Topic for gripper commands
- `play_motion_action` (default: `/play_motion2`) - PlayMotion2 action server name

### Command Format

#### Simple String Commands

```bash
# Simple movement command
ros2 topic pub /dashboard/movement std_msgs/String "data: 'home'"

# Simple arm command
ros2 topic pub /dashboard/arm std_msgs/String "data: 'pregrasp'"

# Simple gripper command
ros2 topic pub /dashboard/gripper std_msgs/String "data: 'open'"
```

#### JSON Commands from Dashboard

The dashboard sends structured JSON commands with the following formats:

```bash
# Movement command with speed and timestamp
ros2 topic pub /dashboard/movement std_msgs/String 'data: "{\"motion_name\": \"home\", \"approach_speed\": 0.5, \"timestamp\": 1697558400000}"'

# Arm action with parameters and timestamp
ros2 topic pub /dashboard/arm std_msgs/String 'data: "{\"action\": \"pregrasp\", \"params\": {\"height\": 0.8}, \"timestamp\": 1697558400000}"'

# Gripper command with force and timestamp
ros2 topic pub /dashboard/gripper std_msgs/String 'data: "{\"action\": \"close\", \"force\": 50.0, \"timestamp\": 1697558400000}"'
```

## Supported TIAGo Motions

The adapter works with any PlayMotion2 motions available on your TIAGo robot. Common examples include:

- `home` - Move to home position
- `pregrasp` - Move to pre-grasp position
- `reach_floor` - Reach down to floor level
- `reach_max` - Reach to maximum height
- `unfold_arm` - Unfold arm from folded position
- `fold_arm` - Fold arm to compact position

## Development

### Project Structure

```
src/dashboard_adapter/
├── dashboard_adapter/
│   ├── __init__.py
│   └── node.py              # Main adapter node
├── launch/
│   └── dashboard_adapter.launch.py
├── resource/
├── test/
├── package.xml
└── setup.py
```

### Adding Custom Actions

To extend the adapter for custom TIAGo actions:

1. Modify the `_handle_arm_action()` or `_handle_gripper_action()` methods in `node.py`
2. Add robot-specific action handling logic
3. Update the command parsing in `_parse_action()` if needed

### Testing

Run the test suite:

```bash
colcon test --packages-select dashboard_adapter
colcon test-result --verbose
```

## Integration with XX Dashboard

This adapter is designed to work with the [Wizard for Kids Dashboard](https://github.com/idsia-robotics/wizard-for-kids).

### Configuration Wizard Integration

The TIAGo robot configuration is already included in the Wizard for Kids Dashboard configuration wizard as an example robot.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](src/dashboard_adapter/LICENSE) file for details.

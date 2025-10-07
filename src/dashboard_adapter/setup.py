from setuptools import find_packages, setup

package_name = "dashboard_adapter"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/dashboard_adapter.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="XX XX",
    maintainer_email="XX@XX.XX",
    description="Adapter package for PAL Robotics TIAGo robot to communicate with XX Dashboard",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "adapter = dashboard_adapter.node:main",
        ],
    },
)

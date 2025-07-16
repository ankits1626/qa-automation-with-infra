from aws_cdk import (
    Stack,
    aws_devicefarm as devicefarm,
)
from constructs import Construct

class DeviceFarmStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Android Device Farm project
        android_project = devicefarm.CfnProject(
            self, "AndroidProject",
            name="android-test-project"
        )

        # iOS Device Farm project
        ios_project = devicefarm.CfnProject(
            self, "IOSProject",
            name="ios-test-project"
        )

        # Android device pool
        android_device_pool = devicefarm.CfnDevicePool(
            self, "AndroidDevicePool",
            name="android-device-pool",
            project_arn=android_project.attr_arn,
            rules=[
                devicefarm.CfnDevicePool.RuleProperty(
                    attribute="OS_VERSION",
                    operator="GREATER_THAN_OR_EQUALS",
                    value='"10"'
                ),
                devicefarm.CfnDevicePool.RuleProperty(
                    attribute="PLATFORM",
                    operator="EQUALS",
                    value='"ANDROID"'
                )
            ]
        )

        # iOS device pool
        ios_device_pool = devicefarm.CfnDevicePool(
            self, "IOSDevicePool",
            name="ios-device-pool",
            project_arn=ios_project.attr_arn,
            rules=[
                devicefarm.CfnDevicePool.RuleProperty(
                    attribute="OS_VERSION",
                    operator="GREATER_THAN_OR_EQUALS",
                    value='"14.0"'
                ),
                devicefarm.CfnDevicePool.RuleProperty(
                    attribute="PLATFORM",
                    operator="EQUALS",
                    value='"IOS"'
                )
            ]
        )

        # Expose project ARNs as properties
        self.android_project_arn = android_project.attr_arn
        self.ios_project_arn = ios_project.attr_arn
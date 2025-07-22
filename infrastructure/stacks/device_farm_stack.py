from aws_cdk import (
   Stack,
   aws_devicefarm as devicefarm,
)
from constructs import Construct

class DeviceFarmStack(Stack):

   def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
       super().__init__(scope, construct_id, **kwargs)

       # Add unique suffix to avoid export conflicts
       stack_suffix = self.region

       # Android Device Farm project
       android_project = devicefarm.CfnProject(
           self, "AndroidProject",
           name=f"android-test-project-{stack_suffix}"
       )

       # iOS Device Farm project
       ios_project = devicefarm.CfnProject(
           self, "IOSProject",
           name=f"ios-test-project-{stack_suffix}"
       )

       # Android device pool
       android_device_pool = devicefarm.CfnDevicePool(
           self, "AndroidDevicePool",
           name=f"android-device-pool-{stack_suffix}",
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
           name=f"ios-device-pool-{stack_suffix}",
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

       # Store ARNs privately first
       self._android_project_arn = android_project.attr_arn
       self._ios_project_arn = ios_project.attr_arn

   @property
   def android_project_arn(self):
       return self._android_project_arn
       
   @property
   def ios_project_arn(self):
       return self._ios_project_arn
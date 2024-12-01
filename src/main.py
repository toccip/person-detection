import asyncio
from typing import Any, ClassVar, Final, Mapping, Optional, Sequence, cast, List, Dict

from typing_extensions import Self
from viam.components.sensor import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading
from viam.utils import struct_to_dict
from viam.logging import getLogger

from viam.services.vision import *
from viam.components.camera import *
from viam.proto.service import *

LOGGER = getLogger(__name__)

class PersonSensor(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("pauldetect", "person-detection"), "person-sensor"
    )


    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        
        return []

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        """
            Expected Attributes are
            vision_name -> string value of a vison service
            camera_name -> string value of a camera associated with the vision service

            The vision name will be used to instantiate the VisionClient passed as a dependency
        """

        if "vision_name" in config.attributes.fields:
            vision_name = config.attributes.fields["vision_name"].string_value
        else:
            vision_name = "vision-default"
        self.vision_service = dependencies[VisionClient.get_resource_name(vision_name)]

        if "camera_name" in config.attributes.fields:
            camera_name = config.attributes.fields["camera_name"].string_value
        else:
            camera_name = "camera-default"
        self.camera_name = camera_name


        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
    
        person_detected = False
        vision_detections = await self.vision_service.get_detections_from_camera(self.camera_name)
        for a_detection in vision_detections:
            if a_detection.class_name == 'Person':
                person_detected = True
                break
                
        return {
            "person_detected": person_detected
        }


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())


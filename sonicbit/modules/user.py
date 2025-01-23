import logging

from sonicbit.base import SonicBitBase
from sonicbit.errors import SonicBitError
from sonicbit.types import UserDetails
from sonicbit.types.storage_details import StorageDetails

logger = logging.getLogger(__name__)


class User(SonicBitBase):
    def get_user_details(self) -> UserDetails:
        logger.debug("Getting user details")
        response = self.call(method="POST", url=self.url("/get/user/details"))

        return UserDetails.from_response(response)

    def get_storage_details(self) -> StorageDetails:
        logger.debug("Getting storage details")
        response = self.call(method="POST", url=self.url("/get/user/storage_details"))

        return StorageDetails.from_response(response)

    def clear_storage(self) -> bool:
        logger.debug("Clearing storage")
        response = self.call(method="POST", url=self.url("/user/drive/clear"))

        json_data = response.json()
        error_message = json_data.get("message")

        if error_message:
            raise SonicBitError(f"Failed to clear storage: {error_message}")

        return json_data["success"]

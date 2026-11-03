import logging

from sonicbit.base import SonicBitBase
from sonicbit.errors import SonicBitError
from sonicbit.models import UserDetails
from sonicbit.models.storage_details import StorageDetails

logger = logging.getLogger(__name__)


class User(SonicBitBase):
    def get_user_details(self) -> UserDetails:
        logger.debug("Fetching user details")
        response = self._request(method="GET", url=self.url("/account/profile"))
        return UserDetails.from_response(response)

    def get_storage_details(self) -> StorageDetails:
        logger.debug("Fetching storage details")
        response = self._request(method="GET", url=self.url("/storage/details"))
        return StorageDetails.from_response(response)

    def clear_storage(self) -> bool:
        logger.debug("Clearing all storage")
        response = self._request(method="POST", url=self.url("/drive/clear"))

        json_data = response.json()
        if msg := json_data.get("msg"):
            raise SonicBitError(f"Failed to clear storage: {msg}")

        return bool(json_data.get("success") or json_data.get("ok"))

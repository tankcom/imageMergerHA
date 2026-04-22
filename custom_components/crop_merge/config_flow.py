from homeassistant import config_entries

from .const import DOMAIN


class CropMergeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Crop Merge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Crop Merge", data={})
        return self.async_show_form(step_id="user")

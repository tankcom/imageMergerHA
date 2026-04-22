import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class CropMergeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Crop Merge", data={})
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors
        )

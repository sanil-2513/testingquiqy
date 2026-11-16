class MenuManagementProxy:
    """Proxy: checks administrator permissions before menu changes."""
    def __init__(self, database):
        self.database = database

    @staticmethod
    def _check_admin(user):
        if not user or user.get("role") != "admin":
            raise PermissionError("Administrator permission is required.")

    def add_item(self, item, user):
        self._check_admin(user)
        return self.database.insert_menu_item(item)

    def delete_item(self, item_id, user):
        self._check_admin(user)
        self.database.delete_menu_item(item_id)

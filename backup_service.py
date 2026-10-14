import os
import shutil
import datetime

class BackupService:
    @staticmethod
    def create_database_backup(db_path: str = "gullycric.db", backup_dir: str = "backups") -> str:
        if not os.path.exists(db_path):
            return ""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"gullycric_{timestamp}.bak")
        shutil.copy2(db_path, backup_path)
        return backup_path

backup_service = BackupService()

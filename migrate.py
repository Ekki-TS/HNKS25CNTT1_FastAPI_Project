"""
Migration script để thêm các cột soft delete vào bảng projects.
Chạy script này để update database schema.
"""
from sqlalchemy import text
from app.db.database import engine


def upgrade():
    """Thêm các cột is_deleted và deleted_at vào bảng projects"""
    with engine.connect() as connection:
        # Kiểm tra nếu cột chưa tồn tại
        try:
            # Thêm cột is_deleted
            connection.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL
            """))
            print("✓ Thêm cột is_deleted thành công")
        except Exception as e:
            print(f"! Cột is_deleted có thể đã tồn tại: {e}")
        
        try:
            # Thêm cột deleted_at
            connection.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN deleted_at DATETIME NULL
            """))
            print("✓ Thêm cột deleted_at thành công")
        except Exception as e:
            print(f"! Cột deleted_at có thể đã tồn tại: {e}")
        
        connection.commit()


def downgrade():
    """Xóa các cột is_deleted và deleted_at khỏi bảng projects (rollback)"""
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                ALTER TABLE projects 
                DROP COLUMN deleted_at
            """))
            print("✓ Xóa cột deleted_at thành công")
        except Exception as e:
            print(f"! Lỗi khi xóa deleted_at: {e}")
        
        try:
            connection.execute(text("""
                ALTER TABLE projects 
                DROP COLUMN is_deleted
            """))
            print("✓ Xóa cột is_deleted thành công")
        except Exception as e:
            print(f"! Lỗi khi xóa is_deleted: {e}")
        
        connection.commit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        print("Chạy downgrade...")
        downgrade()
    else:
        print("Chạy upgrade...")
        upgrade()

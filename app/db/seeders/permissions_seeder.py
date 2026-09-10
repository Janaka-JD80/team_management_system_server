from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.permission import Permission

async def seed_permissions(db: AsyncSession):
    permissions_to_seed = [
        {"name": "create:report", "desc": "Create a new draft report"},
        {"name": "edit:own_report", "desc": "Edit own reports"},
        {"name": "submit:report", "desc": "Submit a draft report"},
        {"name": "view:own_reports", "desc": "View own reports"},
        {"name": "view:all_reports", "desc": "View all team reports"},
        {"name": "review:report", "desc": "Review team reports"},
        {"name": "view:dashboard", "desc": "View analytics dashboard"},
        {"name": "manage:projects", "desc": "Create, edit, delete projects"},
        {"name": "manage:users", "desc": "Manage team members"}
    ]
    
    for perm_data in permissions_to_seed:
        stmt = select(Permission).where(Permission.permission_name == perm_data["name"])
        result = await db.execute(stmt)
        if not result.scalars().first():
            db.add(Permission(permission_name=perm_data["name"], permission_description=perm_data["desc"]))
    
    await db.commit()
    print("Permissions seeded.")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.role import Role
from app.models.permission import Permission

async def seed_roles(db: AsyncSession):
    roles_data = {
        "admin": ["view:dashboard", "manage:projects", "manage:users"],
        "manager": ["view:all_reports", "review:report", "view:dashboard", "manage:projects"],
        "team_member": ["create:report", "edit:own_report", "submit:report", "view:own_reports"]
    }
    
    all_perms_result = await db.execute(select(Permission))
    all_perms = all_perms_result.scalars().all()
    perm_map = {p.permission_name: p for p in all_perms}
    
    for role_name, perm_names in roles_data.items():
        stmt = select(Role).options(selectinload(Role.permissions)).where(Role.role_name == role_name)
        result = await db.execute(stmt)
        role = result.scalars().first()
        
        if not role:
            role = Role(
                role_name=role_name, 
                role_description=f"{role_name.capitalize()} Role",
                permissions=[perm_map[name] for name in perm_names if name in perm_map]
            )
            db.add(role)
        else:
            role.permissions = [perm_map[name] for name in perm_names if name in perm_map]
    
    await db.commit()
    print("Roles seeded.")

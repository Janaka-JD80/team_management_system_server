from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

async def seed_users(db: AsyncSession):
    # Fetch roles
    roles_result = await db.execute(select(Role))
    roles_map = {r.role_name: r for r in roles_result.scalars().all()}
    
    if not roles_map:
        print("No roles found. Seed roles first.")
        return

    users_to_seed = [
        {"email": "admin@example.com", "name": "System Admin", "role": "admin"},
        {"email": "manager1@example.com", "name": "Alice Manager", "role": "manager"},
        {"email": "manager2@example.com", "name": "Bob Manager", "role": "manager"},
        {"email": "manager3@example.com", "name": "Charlie Manager", "role": "manager"},
    ]
    
    # Generate 10 team members
    for i in range(1, 11):
        users_to_seed.append({"email": f"member{i}@example.com", "name": f"Team Member {i}", "role": "team_member"})
        
    pwd_hash = get_password_hash("password123")
    
    for u_data in users_to_seed:
        stmt = select(User).options(selectinload(User.roles)).where(User.user_email == u_data["email"])
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            user = User(
                user_email=u_data["email"], 
                full_name=u_data["name"], 
                hashed_password=pwd_hash,
                roles=[roles_map[u_data["role"]]]
            )
            db.add(user)
        else:
            user.roles = [roles_map[u_data["role"]]]
            
    await db.commit()
    print("Users seeded. Password is 'password123'.")

import asyncio
from app.db.session import AsyncSessionLocal
from app.db.seeders.permissions_seeder import seed_permissions
from app.db.seeders.roles_seeder import seed_roles
from app.db.seeders.status_seeder import seed_statuses
from app.db.seeders.projects_seeder import seed_projects
from app.db.seeders.users_seeder import seed_users
from app.db.seeders.reports_seeder import seed_reports

async def main():
    print("Starting database seeding...")
    async with AsyncSessionLocal() as db:
        await seed_permissions(db)
        await seed_roles(db)
        await seed_statuses(db)
        await seed_projects(db)
        await seed_users(db)
        await seed_reports(db)
    print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())

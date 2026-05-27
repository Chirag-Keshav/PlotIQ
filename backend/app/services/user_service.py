"""User service for Clerk sync."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.listing import User

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_user(self, clerk_user_id: str, email: str, phone: str, display_name: str) -> User:
        stmt = select(User).where(User.clerk_user_id == clerk_user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if user:
            user.email = email
            user.phone = phone
            user.display_name = display_name
        else:
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                phone=phone,
                display_name=display_name,
            )
            self.db.add(user)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user

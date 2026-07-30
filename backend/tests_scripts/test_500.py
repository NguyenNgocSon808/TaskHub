import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.models.schema import User, Workspace, WorkspaceMember, WorkspaceRole
from app.core.config import settings

async def test():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    
    async with session_factory() as session:
        from app.services.workspace_service import WorkspaceService
        ws_service = WorkspaceService(session)
        
        # Get an existing user
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        user = result.scalars().first()
        
        if not user:
            print("No user found.")
            return
            
        print(f"Using user {user.id}")
        
        from app.schemas.workspace import WorkspaceCreate
        data = WorkspaceCreate(name="Debug Workspace")
        try:
            ws = await ws_service.create_workspace(user, data)
            print(f"Created workspace {ws.id}")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

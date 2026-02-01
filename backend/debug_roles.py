
from app.core.database import SessionLocal
from app.models import Room, Role

def check_room_roles(room_id):
    db = SessionLocal()
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            print(f"Room {room_id} not found")
            return
            
        print(f"Room: {room.name} (ID: {room.id})")
        print(f"Roles count: {len(room.roles)}")
        for role in room.roles:
            print(f" - Role: {role.name} (ID: {role.id})")
            print(f"   - Agent ID: {role.agent_id}")
            if role.agent:
                print(f"   - Agent: {role.agent.name} (Provider: {role.agent.provider}, Model: {role.agent.model_name})")
            else:
                print(f"   - Agent: None")

            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_room_roles(7)

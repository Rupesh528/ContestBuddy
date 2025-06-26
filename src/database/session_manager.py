import os
import json
from datetime import datetime, timedelta

class SessionManager:
    """Session management class for handling user authentication state"""
    
    def __init__(self):
        self.session_file = self._get_session_file_path()
        self.session_data = self._load_session()
        
    def _get_session_file_path(self):
        """Get the path to the session file"""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        session_dir = os.path.join(app_dir, "data")
        
        # Create directory if it doesn't exist
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
        return os.path.join(session_dir, "session.json")
    
    def _load_session(self):
        """Load session data from file"""
        if not os.path.exists(self.session_file):
            # Create empty session file if it doesn't exist
            self._save_session({})
            return {}
        
        try:
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
                
                # Check if session is expired
                if self.is_session_expired(session_data):
                    print("Session expired, clearing session data")
                    self._save_session({})
                    return {}
                    
                return session_data
        except Exception as e:
            print(f"Error loading session: {str(e)}")
            return {}
    
    def _save_session(self, session_data):
        """Save session data to file"""
        try:
            print(f"Saving session data: {session_data}")
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            
            with open(self.session_file, "w") as f:
                json.dump(session_data, f)
                
            self.session_data = session_data
            print(f"Session saved successfully to {self.session_file}")
            return True
        except Exception as e:
            print(f"Error saving session: {str(e)}")
            return False
    
    def create_session(self, user_data):
        """Create a new session for a user"""
        session = {
            "user_id": user_data.get("user_id", ""),
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()  # 7-day session
        }
        
        saved = self._save_session(session)
        if saved:
            print(f"Session created successfully for user: {session.get('name')}")
            return session
        else:
            print("Session creation failed")
            return None
    
    def get_current_user(self):
        """Get the currently logged in user"""
        if not self.session_data or self.is_session_expired(self.session_data):
            return None
            
        return {
            "user_id": self.session_data.get("user_id", ""),
            "email": self.session_data.get("email", ""),
            "name": self.session_data.get("name", "")
        }
    
    def is_logged_in(self):
        """Check if user is logged in"""
        # Reload session data to ensure we have the latest data
        self.session_data = self._load_session()
        
        user = self.get_current_user()
        is_logged = user is not None and "user_id" in user and user["user_id"]
        
        print(f"is_logged_in check: {is_logged}")
        if not is_logged:
            print("User session not found or invalid")
        return is_logged
    
    def is_session_expired(self, session_data):
        """Check if the session is expired"""
        if not session_data or "expires_at" not in session_data:
            return True
            
        try:
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            is_expired = datetime.now() > expires_at
            
            if is_expired:
                print(f"Session expired at {expires_at}")
            
            return is_expired
        except Exception as e:
            print(f"Error checking session expiration: {str(e)}")
            return True
    
    def logout(self):
        """End the current user session"""
        print("Logging out: clearing session data")
        self._save_session({})
        return True
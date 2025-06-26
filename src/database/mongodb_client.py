from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, UTC
import bcrypt
import certifi
import os
import json

class MongoDB:
    def __init__(self):
        # Your MongoDB credentials
        username = "sahanirupesh528"
        password = "SkcxdlfF4oHHJWIa"
        cluster = "cluster0.6muby.mongodb.net"
        
        # Use Atlas connection string format
        self.connection_string = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"
        
        self.is_connected = False
        self.client = None
        self.db = None
        self.users = None
        
        try:
            # Use certifi for SSL certificate validation but remove directConnection
            self.client = MongoClient(
                self.connection_string,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.is_connected = True
            
            # Set up database and collections
            self.db = self.client['competitive_programming_app']
            self.users = self.db['users']
            
            # Create index if connected
            if self.is_connected:
                try:
                    self.users.create_index("email", unique=True)
                except Exception as e:
                    print(f"Index creation error: {str(e)}")
            
            print("MongoDB connection successful")
            
        except Exception as e:
            print(f"MongoDB Connection Error: {str(e)}")
            self._setup_local_storage()

    def _setup_local_storage(self):
        """Set up local storage as a fallback"""
        try:
            # Create local storage directory
            app_dir = self._get_app_directory()
            data_dir = os.path.join(app_dir, "data")
            
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            # Check if local user data exists
            self.users_file = os.path.join(data_dir, "users.json")
            if not os.path.exists(self.users_file):
                with open(self.users_file, "w") as f:
                    json.dump([], f)
                    
            print("Local storage setup complete")
        except Exception as e:
            print(f"Local storage setup error: {str(e)}")

    def _get_app_directory(self):
        """Get the app directory"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def _save_users_to_file(self, users):
        """Save users to local file"""
        try:
            with open(self.users_file, "w") as f:
                json.dump(users, f)
        except Exception as e:
            print(f"Error saving users to file: {str(e)}")
            
    def _load_users_from_file(self):
        """Load users from local file"""
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users from file: {str(e)}")
            return []

    def authenticate_user(self, email, password):
        """Authenticate a user with email and password"""
        # Try MongoDB first if connected
        if self.is_connected:
            try:
                user = self.users.find_one({"email": email})
                if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                    return {
                        "user_id": str(user['_id']),
                        "email": user['email'],
                        "name": user.get('name', '')
                    }
            except Exception as e:
                print(f"MongoDB authentication error: {str(e)}")
        
        # Fall back to local file if MongoDB failed or not connected
        try:
            users = self._load_users_from_file()
            for user in users:
                if user["email"] == email:
                    # Check password - stored as string in local file
                    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                        return {
                            "user_id": user.get('user_id', ''),
                            "email": user['email'],
                            "name": user.get('name', '')
                        }
        except Exception as e:
            print(f"Local file authentication error: {str(e)}")
            
        return None

    def create_user(self, email, password, name):
        """Create a new user"""
        # Check if user exists in MongoDB or local file
        existing_user = self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already exists")
            
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Try to create in MongoDB if connected
        user_id = None
        if self.is_connected:
            try:
                user = {
                    "email": email,
                    "password": hashed_password,
                    "name": name,
                    "created_at": datetime.now(UTC)
                }
                
                result = self.users.insert_one(user)
                user_id = str(result.inserted_id)
            except Exception as e:
                print(f"MongoDB user creation error: {str(e)}")
        
        # Always create locally as well or as fallback
        try:
            users = self._load_users_from_file()
            
            # Generate a simple ID if none from MongoDB
            if not user_id:
                import uuid
                user_id = str(uuid.uuid4())
                
            local_user = {
                "user_id": user_id,
                "email": email,
                "password": hashed_password.decode('utf-8'),  # Store as string
                "name": name,
                "created_at": datetime.now(UTC).isoformat()
            }
            
            users.append(local_user)
            self._save_users_to_file(users)
            
            return user_id
        except Exception as e:
            print(f"Local user creation error: {str(e)}")
            if user_id:  # If MongoDB succeeded but local failed
                return user_id
            raise

    def get_user_by_email(self, email):
        """Get user info by email"""
        # Try MongoDB first if connected
        if self.is_connected:
            try:
                user = self.users.find_one({"email": email})
                if user:
                    return {
                        "user_id": str(user['_id']),
                        "email": user['email'],
                        "name": user.get('name', '')
                    }
            except Exception as e:
                print(f"MongoDB get user error: {str(e)}")
        
        # Fall back to local file
        try:
            users = self._load_users_from_file()
            for user in users:
                if user["email"] == email:
                    return {
                        "user_id": user.get('user_id', ''),
                        "email": user['email'],
                        "name": user.get('name', '')
                    }
        except Exception as e:
            print(f"Local file get user error: {str(e)}")
            
        return None
from .mongo import MongoDB
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

class CaseRepository:
    COLLECTION_NAME = "cases"

    @classmethod
    def get_collection(cls):
        db = MongoDB.get_db()
        if db is not None:
            return db[cls.COLLECTION_NAME]
        return None

    @classmethod
    def create_case(cls, case_data: Dict[str, Any]) -> str:
        case_data['_id'] = case_data.get('case_id', str(uuid.uuid4()))
        case_data['created_at'] = datetime.utcnow()
        case_data['updated_at'] = datetime.utcnow()
        
        collection = cls.get_collection()
        if collection is not None:
            collection.insert_one(case_data)
        
        return case_data['_id']

    @classmethod
    def get_case(cls, case_id: str) -> Optional[Dict[str, Any]]:
        collection = cls.get_collection()
        if collection is not None:
            return collection.find_one({"_id": case_id})
        return None

    @classmethod
    def update_case(cls, case_id: str, update_data: Dict[str, Any]) -> bool:
        update_data['updated_at'] = datetime.utcnow()
        collection = cls.get_collection()
        if collection is not None:
            result = collection.update_one({"_id": case_id}, {"$set": update_data})
            return result.modified_count > 0
        return False
        
    @classmethod
    def get_all_cases(cls, filter_query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if filter_query is None:
            filter_query = {}
        collection = cls.get_collection()
        if collection is not None:
            return list(collection.find(filter_query).sort("created_at", -1))
        return []

class AuditRepository:
    COLLECTION_NAME = "audit_logs"

    @classmethod
    def get_collection(cls):
        db = MongoDB.get_db()
        if db is not None:
            return db[cls.COLLECTION_NAME]
        return None

    @classmethod
    def add_log(cls, log_data: Dict[str, Any]) -> str:
        log_data['_id'] = str(uuid.uuid4())
        
        collection = cls.get_collection()
        if collection is not None:
            collection.insert_one(log_data)
            
        return log_data['_id']
        
    @classmethod
    def get_logs_for_case(cls, case_id: str) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        if collection is not None:
            return list(collection.find({"case_id": case_id}).sort("timestamp", 1))
        return []

    @classmethod
    def get_all_logs(cls, limit: int = 100) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        if collection is not None:
            return list(collection.find().sort("timestamp", -1).limit(limit))
        return []

#!/usr/bin/env python3
"""
Database seeding script for Volunteer Matching System
Creates sample users, volunteers, events, and matches for testing
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import connect_to_mongo, get_database
from backend.app.services.auth_service import AuthService
from backend.app.config import settings

# Sample data
SAMPLE_USERS = [
    {
        "email": "alice.volunteer@example.com",
        "username": "alice_volunteer",
        "full_name": "Alice Johnson",
        "phone": "+1-555-0101",
        "role": "volunteer",
        "password": "password123"
    },
    {
        "email": "bob.volunteer@example.com", 
        "username": "bob_volunteer",
        "full_name": "Bob Smith",
        "phone": "+1-555-0102",
        "role": "volunteer",
        "password": "password123"
    },
    {
        "email": "carol.volunteer@example.com",
        "username": "carol_volunteer", 
        "full_name": "Carol Davis",
        "phone": "+1-555-0103",
        "role": "volunteer",
        "password": "password123"
    },
    {
        "email": "greenearth@example.com",
        "username": "green_earth_org",
        "full_name": "Green Earth Organization",
        "phone": "+1-555-0201",
        "role": "organization",
        "password": "password123"
    },
    {
        "email": "helpinghands@example.com",
        "username": "helping_hands",
        "full_name": "Helping Hands Foundation",
        "phone": "+1-555-0202", 
        "role": "organization",
        "password": "password123"
    }
]

SAMPLE_VOLUNTEER_PROFILES = [
    {
        "skills": [
            {"name": "Python", "level": "advanced", "years_experience": 5, "certifications": ["Python Institute Certified"]},
            {"name": "JavaScript", "level": "intermediate", "years_experience": 3, "certifications": []},
            {"name": "Teaching", "level": "expert", "years_experience": 8, "certifications": ["Teaching License"]},
            {"name": "Public Speaking", "level": "advanced", "years_experience": 6, "certifications": []}
        ],
        "availability": [
            {"day": "saturday", "start_time": "09:00", "end_time": "17:00"},
            {"day": "sunday", "start_time": "10:00", "end_time": "16:00"},
            {"day": "wednesday", "start_time": "18:00", "end_time": "21:00"}
        ],
        "location": {
            "address": "123 Main St",
            "city": "San Francisco",
            "state": "California", 
            "country": "USA",
            "postal_code": "94105",
            "coordinates": [-122.4194, 37.7749]
        },
        "profile": {
            "bio": "Passionate software developer and educator with experience in Python, web development, and teaching programming to beginners. Love helping others learn technology skills.",
            "motivation": "I want to use my technical skills to help non-profits leverage technology for social good.",
            "languages": ["English", "Spanish"],
            "transportation": True,
            "emergency_contact": {"name": "John Johnson", "phone": "+1-555-0111"},
            "dietary_restrictions": [],
            "medical_conditions": []
        },
        "preferences": {
            "preferred_event_types": ["education", "technology"],
            "max_distance_km": 25,
            "commitment_level": "high"
        }
    },
    {
        "skills": [
            {"name": "First Aid", "level": "expert", "years_experience": 10, "certifications": ["CPR Certified", "First Aid Certified"]},
            {"name": "Nursing", "level": "expert", "years_experience": 15, "certifications": ["RN License"]},
            {"name": "Spanish", "level": "expert", "years_experience": 20, "certifications": []},
            {"name": "Community Outreach", "level": "advanced", "years_experience": 8, "certifications": []}
        ],
        "availability": [
            {"day": "friday", "start_time": "17:00", "end_time": "21:00"},
            {"day": "saturday", "start_time": "08:00", "end_time": "18:00"},
            {"day": "sunday", "start_time": "08:00", "end_time": "18:00"}
        ],
        "location": {
            "address": "456 Oak Ave",
            "city": "San Francisco", 
            "state": "California",
            "country": "USA",
            "postal_code": "94110",
            "coordinates": [-122.4094, 37.7549]
        },
        "profile": {
            "bio": "Registered nurse with extensive experience in emergency care and community health programs. Bilingual in English and Spanish.",
            "motivation": "Healthcare is a human right. I volunteer to provide medical care to underserved communities.",
            "languages": ["English", "Spanish"],
            "transportation": True,
            "emergency_contact": {"name": "Maria Smith", "phone": "+1-555-0222"},
            "dietary_restrictions": ["Vegetarian"],
            "medical_conditions": []
        },
        "preferences": {
            "preferred_event_types": ["healthcare", "social_services"],
            "max_distance_km": 40,
            "commitment_level": "high"
        }
    },
    {
        "skills": [
            {"name": "Environmental Science", "level": "advanced", "years_experience": 6, "certifications": ["Environmental Science Degree"]},
            {"name": "Photography", "level": "intermediate", "years_experience": 4, "certifications": []},
            {"name": "Social Media", "level": "advanced", "years_experience": 5, "certifications": ["Google Analytics Certified"]},
            {"name": "Writing", "level": "advanced", "years_experience": 7, "certifications": []}
        ],
        "availability": [
            {"day": "monday", "start_time": "18:00", "end_time": "21:00"},
            {"day": "wednesday", "start_time": "18:00", "end_time": "21:00"},
            {"day": "saturday", "start_time": "09:00", "end_time": "15:00"}
        ],
        "location": {
            "address": "789 Pine St",
            "city": "San Francisco",
            "state": "California",
            "country": "USA", 
            "postal_code": "94109",
            "coordinates": [-122.4294, 37.7949]
        },
        "profile": {
            "bio": "Environmental scientist passionate about conservation and sustainability. Experienced in research, writing, and social media advocacy for environmental causes.",
            "motivation": "Climate change is the defining issue of our time. I want to help organizations spread awareness and take action.",
            "languages": ["English", "French"],
            "transportation": False,
            "emergency_contact": {"name": "Robert Davis", "phone": "+1-555-0333"},
            "dietary_restrictions": ["Vegan"],
            "medical_conditions": []
        },
        "preferences": {
            "preferred_event_types": ["environment", "education", "community_development"],
            "max_distance_km": 15,
            "commitment_level": "flexible"
        }
    }
]

SAMPLE_EVENTS = [
    {
        "title": "Community Garden Clean-up",
        "description": "Join us for a weekend community garden clean-up event. We'll be weeding, planting new vegetables, and maintaining the irrigation system. This is a great opportunity to get your hands dirty while helping provide fresh food for local families in need. No experience necessary - we'll provide tools and training.",
        "category": "environment",
        "location": {
            "address": "Golden Gate Park Community Garden",
            "city": "San Francisco",
            "state": "California",
            "country": "USA",
            "postal_code": "94117",
            "coordinates": [-122.4735, 37.7694]
        },
        "schedule": {
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=7)).isoformat(),
            "start_time": "09:00",
            "end_time": "15:00",
            "recurring": False
        },
        "requirements": [
            {
                "skill": {"name": "Gardening", "level": "beginner"},
                "required_volunteers": 8,
                "filled_positions": 0
            },
            {
                "skill": {"name": "Physical Labor", "level": "intermediate"}, 
                "required_volunteers": 5,
                "filled_positions": 0
            }
        ],
        "max_volunteers": 15,
        "registration_deadline": (date.today() + timedelta(days=5)).isoformat(),
        "is_urgent": False,
        "requires_background_check": False,
        "provides_training": True,
        "provides_meals": True,
        "provides_transportation": False,
        "age_requirement": 16
    },
    {
        "title": "Coding Workshop for Kids",
        "description": "Volunteer to teach basic programming concepts to children ages 8-14. We'll be using Scratch and Python to introduce kids to coding in a fun, interactive way. Looking for volunteers with programming experience who are comfortable working with children. Training materials and laptops will be provided.",
        "category": "education",
        "location": {
            "address": "Mission Youth Center",
            "city": "San Francisco", 
            "state": "California",
            "country": "USA",
            "postal_code": "94110",
            "coordinates": [-122.4194, 37.7599]
        },
        "schedule": {
            "start_date": (date.today() + timedelta(days=14)).isoformat(),
            "end_date": (date.today() + timedelta(days=14)).isoformat(),
            "start_time": "13:00",
            "end_time": "17:00",
            "recurring": False
        },
        "requirements": [
            {
                "skill": {"name": "Python", "level": "intermediate"},
                "required_volunteers": 3,
                "filled_positions": 0
            },
            {
                "skill": {"name": "Teaching", "level": "intermediate"},
                "required_volunteers": 4,
                "filled_positions": 0
            },
            {
                "skill": {"name": "Working with Children", "level": "beginner"},
                "required_volunteers": 6,
                "filled_positions": 0
            }
        ],
        "max_volunteers": 8,
        "registration_deadline": (date.today() + timedelta(days=10)).isoformat(),
        "is_urgent": False,
        "requires_background_check": True,
        "provides_training": True,
        "provides_meals": False,
        "provides_transportation": False,
        "age_requirement": 18
    },
    {
        "title": "Free Health Clinic Screening",
        "description": "Support our monthly free health clinic by helping with patient check-ins, basic health screenings, and providing health education. Medical volunteers needed for blood pressure checks, basic health assessments, and health counseling. Non-medical volunteers can help with registration and patient support.",
        "category": "healthcare",
        "location": {
            "address": "Community Health Center",
            "city": "San Francisco",
            "state": "California", 
            "country": "USA",
            "postal_code": "94102",
            "coordinates": [-122.4094, 37.7849]
        },
        "schedule": {
            "start_date": (date.today() + timedelta(days=21)).isoformat(),
            "end_date": (date.today() + timedelta(days=21)).isoformat(),
            "start_time": "08:00",
            "end_time": "16:00",
            "recurring": True,
            "recurring_pattern": "monthly"
        },
        "requirements": [
            {
                "skill": {"name": "Nursing", "level": "expert"},
                "required_volunteers": 2,
                "filled_positions": 0
            },
            {
                "skill": {"name": "First Aid", "level": "advanced"},
                "required_volunteers": 4,
                "filled_positions": 0
            },
            {
                "skill": {"name": "Spanish", "level": "intermediate"},
                "required_volunteers": 3,
                "filled_positions": 0
            },
            {
                "skill": {"name": "Customer Service", "level": "intermediate"},
                "required_volunteers": 5,
                "filled_positions": 0
            }
        ],
        "max_volunteers": 12,
        "registration_deadline": (date.today() + timedelta(days=17)).isoformat(),
        "is_urgent": True,
        "requires_background_check": True,
        "provides_training": True,
        "provides_meals": True,
        "provides_transportation": False,
        "age_requirement": 21
    }
]

async def seed_database():
    """Seed the database with sample data"""
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        auth_service = AuthService()
        
        print("🌱 Starting database seeding...")
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        await db.users.delete_many({})
        await db.volunteers.delete_many({})
        await db.events.delete_many({})
        await db.matches.delete_many({})
        
        # Create users
        print("👥 Creating sample users...")
        created_users = []
        volunteer_users = []
        organization_users = []
        
        for user_data in SAMPLE_USERS:
            try:
                user = await auth_service.create_user(user_data)
                created_users.append(user)
                
                if user.role == "volunteer":
                    volunteer_users.append(user)
                else:
                    organization_users.append(user)
                    
                print(f"✅ Created user: {user.email}")
            except Exception as e:
                print(f"❌ Failed to create user {user_data['email']}: {e}")
        
        # Create volunteer profiles
        print("🤝 Creating volunteer profiles...")
        created_volunteers = []
        
        for i, volunteer_data in enumerate(SAMPLE_VOLUNTEER_PROFILES):
            if i < len(volunteer_users):
                volunteer_data["user_id"] = volunteer_users[i].id
                
                try:
                    result = await db.volunteers.insert_one(volunteer_data)
                    created_volunteers.append(result.inserted_id)
                    print(f"✅ Created volunteer profile for: {volunteer_users[i].email}")
                except Exception as e:
                    print(f"❌ Failed to create volunteer profile: {e}")
        
        # Create events  
        print("📅 Creating sample events...")
        created_events = []
        
        for i, event_data in enumerate(SAMPLE_EVENTS):
            if i < len(organization_users):
                event_data["organization_id"] = organization_users[i % len(organization_users)].id
                event_data["status"] = "active"
                event_data["created_at"] = datetime.utcnow()
                event_data["updated_at"] = datetime.utcnow()
                
                try:
                    result = await db.events.insert_one(event_data)
                    created_events.append(result.inserted_id)
                    print(f"✅ Created event: {event_data['title']}")
                except Exception as e:
                    print(f"❌ Failed to create event {event_data['title']}: {e}")
        
        # Generate some sample matches (optional)
        print("🎯 Generating sample matches...")
        
        if created_volunteers and created_events:
            sample_matches = [
                {
                    "volunteer_id": created_volunteers[0],
                    "event_id": created_events[1],  # Alice -> Coding Workshop
                    "match_score": 0.92,
                    "skill_compatibility": 0.95,
                    "availability_compatibility": 0.85,
                    "location_compatibility": 0.95,
                    "analysis": {
                        "skill_matches": [
                            {
                                "skill_name": "Python",
                                "volunteer_level": "advanced", 
                                "required_level": "intermediate",
                                "match_score": 1.0,
                                "weight": 1.0
                            },
                            {
                                "skill_name": "Teaching",
                                "volunteer_level": "expert",
                                "required_level": "intermediate", 
                                "match_score": 1.0,
                                "weight": 0.8
                            }
                        ],
                        "overall_compatibility": 0.92,
                        "confidence_score": 0.88,
                        "reasoning": "Excellent skill match with strong teaching background",
                        "recommendations": ["Perfect fit for mentoring role", "Could lead advanced sessions"]
                    },
                    "ai_explanation": "This volunteer is an excellent match with advanced Python skills and teaching experience. Highly recommended for the coding workshop.",
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "created_by_agent": "event_matcher",
                    "agent_version": "1.0"
                },
                {
                    "volunteer_id": created_volunteers[1], 
                    "event_id": created_events[2],  # Bob -> Health Clinic
                    "match_score": 0.98,
                    "skill_compatibility": 1.0,
                    "availability_compatibility": 0.95,
                    "location_compatibility": 0.90,
                    "analysis": {
                        "skill_matches": [
                            {
                                "skill_name": "Nursing",
                                "volunteer_level": "expert",
                                "required_level": "expert",
                                "match_score": 1.0,
                                "weight": 1.0
                            },
                            {
                                "skill_name": "First Aid", 
                                "volunteer_level": "expert",
                                "required_level": "advanced",
                                "match_score": 1.0,
                                "weight": 0.9
                            },
                            {
                                "skill_name": "Spanish",
                                "volunteer_level": "expert", 
                                "required_level": "intermediate",
                                "match_score": 1.0,
                                "weight": 0.7
                            }
                        ],
                        "overall_compatibility": 0.98,
                        "confidence_score": 0.95,
                        "reasoning": "Perfect skill alignment with medical expertise and language skills",
                        "recommendations": ["Ideal for lead medical role", "Can supervise other volunteers"]
                    },
                    "ai_explanation": "Outstanding match with expert medical skills and bilingual capabilities. Perfect for the health clinic leadership role.",
                    "status": "accepted",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "volunteer_response": "accepted",
                    "volunteer_responded_at": datetime.utcnow(),
                    "created_by_agent": "event_matcher",
                    "agent_version": "1.0"
                }
            ]
            
            for match_data in sample_matches:
                try:
                    await db.matches.insert_one(match_data)
                    print(f"✅ Created sample match")
                except Exception as e:
                    print(f"❌ Failed to create match: {e}")
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Users created: {len(created_users)}")
        print(f"   • Volunteer profiles: {len(created_volunteers)}")
        print(f"   • Events created: {len(created_events)}")
        print(f"   • Sample matches: 2")
        print("\n🔑 Test Login Credentials:")
        print("   Volunteers:")
        for user in volunteer_users:
            print(f"     • {user.email} / password123")
        print("   Organizations:")
        for user in organization_users:
            print(f"     • {user.email} / password123")
        print("\n🚀 You can now start the application and test with this data!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database()) 
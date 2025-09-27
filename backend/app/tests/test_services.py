import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from ..services.auth_service import AuthService
from ..services.llm_service import LLMService
from ..services.nlp_service import NLPService
from ..services.vector_service import VectorService
from ..services.notification_service import NotificationService

class TestAuthService:
    """Test authentication service"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """Test access token creation"""
        user_data = {"sub": "user123", "role": "volunteer"}
        
        token = auth_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_verify_password(self, auth_service):
        """Test password verification"""
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrongpassword", hashed)
    
    @pytest.mark.asyncio
    async def test_validate_token(self, auth_service):
        """Test token validation"""
        user_data = {"sub": "user123", "role": "volunteer"}
        token = auth_service.create_access_token(user_data)
        
        decoded = auth_service.validate_token(token)
        
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "volunteer"

class TestLLMService:
    """Test LLM service"""
    
    @pytest.fixture
    async def llm_service(self):
        service = LLMService()
        with patch('openai.api_key'):
            await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_generate_response(self, llm_service):
        """Test response generation"""
        prompt = "What is volunteer work?"
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Volunteer work is helping others."
            mock_client.ChatCompletion.create.return_value = mock_response
            
            response = await llm_service.generate_response(prompt)
            
            assert response == "Volunteer work is helping others."
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, llm_service):
        """Test embedding generation"""
        text = "Environmental volunteering"
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_response = Mock()
            mock_response.data = [Mock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3]
            mock_client.Embedding.create.return_value = mock_response
            
            embedding = await llm_service.generate_embedding(text)
            
            assert embedding == [0.1, 0.2, 0.3]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, llm_service):
        """Test error handling in LLM service"""
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.ChatCompletion.create.side_effect = Exception("API Error")
            
            response = await llm_service.generate_response("test prompt")
            
            assert "Error" in response

class TestNLPService:
    """Test NLP service"""
    
    @pytest.fixture
    async def nlp_service(self):
        service = NLPService()
        with patch.object(service, '_download_nltk_data'), \
             patch('spacy.load'):
            await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, nlp_service):
        """Test entity extraction"""
        text = "John Doe works in New York for environmental projects."
        
        with patch.object(nlp_service, 'nlp') as mock_nlp:
            mock_doc = Mock()
            mock_entity = Mock()
            mock_entity.text = "John Doe"
            mock_entity.label_ = "PERSON"
            mock_doc.ents = [mock_entity]
            mock_nlp.return_value = mock_doc
            
            entities = await nlp_service.extract_entities(text)
            
            assert len(entities) == 1
            assert entities[0]["text"] == "John Doe"
            assert entities[0]["label"] == "PERSON"
    
    @pytest.mark.asyncio
    async def test_extract_skills_from_text(self, nlp_service):
        """Test skill extraction"""
        text = "I have experience in Python programming and project management."
        
        with patch.object(nlp_service, '_is_potential_skill', return_value=True):
            skills = await nlp_service.extract_skills_from_text(text)
            
            assert isinstance(skills, list)
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, nlp_service):
        """Test sentiment analysis"""
        positive_text = "I love volunteering and helping others!"
        negative_text = "This event was terrible and poorly organized."
        
        with patch('nltk.sentiment.SentimentIntensityAnalyzer') as mock_analyzer:
            mock_instance = Mock()
            mock_instance.polarity_scores.side_effect = [
                {"compound": 0.8, "pos": 0.7, "neu": 0.2, "neg": 0.1},
                {"compound": -0.6, "pos": 0.1, "neu": 0.3, "neg": 0.6}
            ]
            mock_analyzer.return_value = mock_instance
            
            positive_sentiment = await nlp_service.analyze_sentiment(positive_text)
            negative_sentiment = await nlp_service.analyze_sentiment(negative_text)
            
            assert positive_sentiment["label"] == "positive"
            assert negative_sentiment["label"] == "negative"

class TestVectorService:
    """Test vector service"""
    
    @pytest.fixture
    async def vector_service(self):
        service = VectorService()
        with patch('sentence_transformers.SentenceTransformer'), \
             patch('chromadb.Client'):
            await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, vector_service):
        """Test embedding generation"""
        text = "Environmental volunteering opportunity"
        
        with patch.object(vector_service, 'model') as mock_model:
            mock_model.encode.return_value = Mock()
            mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
            
            embedding = await vector_service.generate_embedding(text)
            
            assert embedding == [0.1, 0.2, 0.3]
    
    @pytest.mark.asyncio
    async def test_add_volunteer_profile(self, vector_service):
        """Test adding volunteer profile"""
        volunteer_id = "vol123"
        volunteer_data = {
            "skills": [{"name": "Event Management"}],
            "profile": {"bio": "Experienced volunteer"}
        }
        
        with patch.object(vector_service, 'collections') as mock_collections:
            mock_collections.__getitem__.return_value.add = Mock()
            
            await vector_service.add_volunteer_profile(volunteer_id, volunteer_data)
            
            mock_collections.__getitem__.return_value.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_similar_volunteers(self, vector_service):
        """Test searching similar volunteers"""
        query_text = "Need volunteers for environmental cleanup"
        
        with patch.object(vector_service, 'collections') as mock_collections, \
             patch.object(vector_service, 'generate_embedding', return_value=[0.1, 0.2, 0.3]):
            
            mock_collections.__getitem__.return_value.query.return_value = {
                'ids': [['vol1', 'vol2']],
                'documents': [['doc1', 'doc2']],
                'metadatas': [[{'vol_id': 'vol1'}, {'vol_id': 'vol2'}]],
                'distances': [[0.1, 0.2]]
            }
            
            results = await vector_service.search_similar_volunteers(query_text)
            
            assert len(results) == 2
            assert results[0]['volunteer_id'] == 'vol1'

class TestNotificationService:
    """Test notification service"""
    
    @pytest.fixture
    async def notification_service(self):
        service = NotificationService()
        with patch.object(service, 'db'):
            await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_send_notification(self, notification_service):
        """Test sending notification"""
        user_id = "user123"
        notification_type = "match_notification"
        data = {"event_title": "Beach Cleanup"}
        
        with patch.object(notification_service, 'db') as mock_db:
            mock_db.users.find_one.return_value = {
                "_id": user_id,
                "email": "test@example.com",
                "full_name": "Test User"
            }
            mock_db.notifications.insert_one.return_value = Mock()
            mock_db.user_notifications.insert_one.return_value = Mock()
            
            result = await notification_service.send_notification(
                user_id, notification_type, data
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_welcome_notification(self, notification_service):
        """Test welcome notification"""
        user_id = "user123"
        user_type = "volunteer"
        
        with patch.object(notification_service, 'db') as mock_db, \
             patch.object(notification_service, 'send_notification', return_value=True) as mock_send:
            
            mock_db.users.find_one.return_value = {
                "_id": user_id,
                "full_name": "Test User"
            }
            
            result = await notification_service.send_welcome_notification(user_id, user_type)
            
            assert result is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_notifications(self, notification_service):
        """Test getting user notifications"""
        user_id = "user123"
        
        with patch.object(notification_service, 'db') as mock_db:
            mock_notifications = [
                {"_id": "notif1", "title": "Test Notification", "read": False},
                {"_id": "notif2", "title": "Another Notification", "read": True}
            ]
            mock_db.user_notifications.find.return_value.sort.return_value.limit.return_value.to_list.return_value = mock_notifications
            
            notifications = await notification_service.get_user_notifications(user_id)
            
            assert len(notifications) == 2
            assert notifications[0]["title"] == "Test Notification"

# Integration tests
class TestServiceIntegration:
    """Integration tests for services working together"""
    
    @pytest.mark.asyncio
    async def test_llm_nlp_integration(self):
        """Test LLM and NLP services working together"""
        # This would test how LLM and NLP services interact
        pass
    
    @pytest.mark.asyncio
    async def test_vector_search_with_nlp(self):
        """Test vector service using NLP-processed data"""
        # This would test vector search with NLP preprocessing
        pass

# Performance tests
class TestServicePerformance:
    """Performance tests for services"""
    
    @pytest.mark.asyncio
    async def test_llm_response_time(self):
        """Test LLM response time"""
        # This would test LLM service performance
        pass
    
    @pytest.mark.asyncio
    async def test_vector_search_performance(self):
        """Test vector search performance"""
        # This would test vector search speed
        pass

# Error handling tests
class TestServiceErrorHandling:
    """Test error handling across services"""
    
    @pytest.mark.asyncio
    async def test_llm_service_timeout(self):
        """Test LLM service timeout handling"""
        service = LLMService()
        
        with patch.object(service, 'client') as mock_client:
            mock_client.ChatCompletion.create.side_effect = TimeoutError("Request timeout")
            
            response = await service.generate_response("test prompt")
            
            assert "Error" in response
    
    @pytest.mark.asyncio
    async def test_vector_service_connection_error(self):
        """Test vector service connection error handling"""
        service = VectorService()
        
        with patch('chromadb.Client', side_effect=ConnectionError("Connection failed")):
            with pytest.raises(Exception):
                await service.initialize()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
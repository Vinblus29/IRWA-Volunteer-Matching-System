import asyncio
import logging
import re
from typing import Dict, Any, List, Tuple, Optional
import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class NLPService:
    """Service for Natural Language Processing tasks"""
    
    def __init__(self):
        self.nlp = None
        self.sia = None
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize NLP components"""
        try:
            # Download required NLTK data
            await self._download_nltk_data()
            
            # Load spaCy model (download if needed)
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Some features may be limited.")
                self.nlp = None
            
            # Initialize sentiment analyzer
            self.sia = SentimentIntensityAnalyzer()
            
            self.is_initialized = True
            logger.info("NLP Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP Service: {e}")
            raise
    
    async def _download_nltk_data(self):
        """Download required NLTK data"""
        required_data = [
            'punkt', 'stopwords', 'vader_lexicon', 
            'averaged_perceptron_tagger', 'maxent_ne_chunker', 
            'words', 'wordnet'
        ]
        
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                nltk.download(data, quiet=True)
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        if not self.is_initialized:
            await self.initialize()
        
        entities = []
        
        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.8  # spaCy doesn't provide confidence scores
                })
        else:
            # Fallback to NLTK
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk])
                    entities.append({
                        "text": entity_text,
                        "label": chunk.label(),
                        "start": -1,  # NLTK doesn't provide char positions easily
                        "end": -1,
                        "confidence": 0.6
                    })
        
        return entities
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not self.is_initialized:
            await self.initialize()
        
        # Use VADER sentiment analyzer
        scores = self.sia.polarity_scores(text)
        
        # Determine overall sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "compound_score": compound,
            "positive": scores['pos'],
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "confidence": abs(compound)
        }
    
    async def extract_keywords(self, text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Extract keywords using TF-IDF"""
        if not self.is_initialized:
            await self.initialize()
        
        # Preprocess text
        processed_text = await self.preprocess_text(text)
        
        try:
            # Fit TF-IDF on the text
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            keywords = []
            for keyword, score in keyword_scores[:top_k]:
                if score > 0:
                    keywords.append({
                        "keyword": keyword,
                        "score": float(score),
                        "importance": "high" if score > 0.5 else "medium" if score > 0.2 else "low"
                    })
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def preprocess_text(self, text: str, 
                            remove_stopwords: bool = True,
                            lemmatize: bool = True,
                            lowercase: bool = True) -> str:
        """Preprocess text for analysis"""
        
        # Convert to lowercase
        if lowercase:
            text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatize
        if lemmatize:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return ' '.join(tokens)
    
    async def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Preprocess texts
            processed_text1 = await self.preprocess_text(text1)
            processed_text2 = await self.preprocess_text(text2)
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_text1, processed_text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    async def extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential skills from text using pattern matching"""
        if not self.is_initialized:
            await self.initialize()
        
        skills = []
        
        # Define skill patterns
        skill_patterns = [
            # Programming languages
            r'\b(python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            # Technologies
            r'\b(react|angular|vue|node\.?js|django|flask|spring|laravel)\b',
            # Databases
            r'\b(mysql|postgresql|mongodb|oracle|sql server|redis|elasticsearch)\b',
            # Cloud platforms
            r'\b(aws|azure|google cloud|gcp|docker|kubernetes|jenkins)\b',
            # Design tools
            r'\b(photoshop|illustrator|figma|sketch|indesign|after effects)\b',
            # General skills
            r'\b(project management|leadership|communication|teamwork|problem solving)\b',
            # Domain-specific
            r'\b(first aid|cpr|teaching|tutoring|counseling|social work|nursing)\b'
        ]
        
        text_lower = text.lower()
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                skill_text = match.group()
                
                # Check if already found
                if not any(s['name'].lower() == skill_text.lower() for s in skills):
                    skills.append({
                        "name": skill_text.title(),
                        "confidence": 0.7,
                        "category": await self._categorize_skill(skill_text),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
        
        # Use spaCy for additional entity extraction if available
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
                    # Check if it might be a skill based on context
                    if await self._is_potential_skill(token.text, token.sent.text):
                        skill_name = token.text.title()
                        if not any(s['name'].lower() == skill_name.lower() for s in skills):
                            skills.append({
                                "name": skill_name,
                                "confidence": 0.5,
                                "category": "unknown",
                                "start_pos": token.idx,
                                "end_pos": token.idx + len(token.text)
                            })
        
        return skills
    
    async def _categorize_skill(self, skill: str) -> str:
        """Categorize a skill based on predefined categories"""
        skill_lower = skill.lower()
        
        categories = {
            "programming": ["python", "java", "javascript", "c++", "c#", "php", "ruby"],
            "web_development": ["react", "angular", "vue", "nodejs", "html", "css"],
            "database": ["mysql", "postgresql", "mongodb", "sql"],
            "design": ["photoshop", "illustrator", "figma", "sketch"],
            "project_management": ["project management", "scrum", "agile"],
            "healthcare": ["first aid", "cpr", "nursing", "medical"],
            "education": ["teaching", "tutoring", "training"],
            "social": ["counseling", "social work", "community outreach"]
        }
        
        for category, skills_list in categories.items():
            if any(s in skill_lower for s in skills_list):
                return category
        
        return "general"
    
    async def _is_potential_skill(self, word: str, context: str) -> bool:
        """Determine if a word might be a skill based on context"""
        skill_contexts = [
            "experience in", "skilled in", "proficient in", "expert in",
            "knowledge of", "familiar with", "trained in", "certified in",
            "background in", "specializing in", "competent in"
        ]
        
        context_lower = context.lower()
        return any(ctx in context_lower for ctx in skill_contexts)
    
    async def extract_phrases(self, text: str, min_length: int = 2, max_length: int = 5) -> List[str]:
        """Extract noun phrases from text"""
        if not self.is_initialized:
            await self.initialize()
        
        phrases = []
        
        if self.nlp:
            doc = self.nlp(text)
            for chunk in doc.noun_chunks:
                if min_length <= len(chunk.text.split()) <= max_length:
                    phrases.append(chunk.text.strip())
        else:
            # Fallback to simple n-gram extraction
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t.isalpha()]
            
            for n in range(min_length, max_length + 1):
                for i in range(len(tokens) - n + 1):
                    phrase = ' '.join(tokens[i:i+n])
                    phrases.append(phrase)
        
        # Remove duplicates and filter
        unique_phrases = list(set(phrases))
        filtered_phrases = [p for p in unique_phrases if len(p) > 3]
        
        return filtered_phrases[:20]  # Limit results
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of text"""
        # Simple language detection based on common words
        # In production, you might want to use a more sophisticated library
        
        english_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        english_word_count = sum(1 for word in words if word in english_words)
        
        total_words = len([w for w in words if w.isalpha()])
        english_ratio = english_word_count / total_words if total_words > 0 else 0
        
        if english_ratio > 0.3:
            return {"language": "en", "confidence": english_ratio}
        else:
            return {"language": "unknown", "confidence": 0.0}
    
    async def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        """Create an extractive summary of text"""
        if not self.is_initialized:
            await self.initialize()
        
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        try:
            # Calculate TF-IDF for sentences
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
            sentence_scores = np.sum(tfidf_matrix.toarray(), axis=1)
            
            # Get top sentences
            top_sentence_indices = sentence_scores.argsort()[-num_sentences:][::-1]
            top_sentence_indices.sort()
            
            summary_sentences = [sentences[i] for i in top_sentence_indices]
            return ' '.join(summary_sentences)
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return ' '.join(sentences[:num_sentences])
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_initialized = False
        logger.info("NLP Service cleaned up") 
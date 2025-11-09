"""
Phase 5: Enhanced Real-time Market Sentiment Analysis & Multi-source Data Ingestion

Implements advanced real-time sentiment analysis, cognitive market synthesis,
and multi-source data ingestion with quality assurance.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import aiohttp
import websockets
import re
from pathlib import Path
import statistics
import time
import random

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources"""
    FINANCIAL_NEWS = "financial_news"
    SOCIAL_MEDIA = "social_media"
    MARKET_DATA = "market_data"
    ECONOMIC_INDICATORS = "economic_indicators"
    ANALYST_REPORTS = "analyst_reports"
    EARNINGS_CALLS = "earnings_calls"
    REGULATORY_FILINGS = "regulatory_filings"
    ALTERNATIVE_DATA = "alternative_data"


class SentimentPolarity(Enum):
    """Sentiment polarity levels"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


class DataQualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


@dataclass
class SentimentData:
    """Structured sentiment data point"""
    data_id: str
    source_type: DataSourceType
    source_name: str
    timestamp: datetime
    content: str
    processed_content: str
    sentiment_polarity: SentimentPolarity
    sentiment_score: float
    confidence: float
    entities: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveSentimentSynthesis:
    """Cognitive synthesis of multiple sentiment sources"""
    synthesis_id: str
    timestamp: datetime
    time_window: timedelta
    source_count: int
    data_points_analyzed: int
    
    # Aggregated sentiment metrics
    overall_sentiment: SentimentPolarity
    confidence: float
    sentiment_momentum: float  # Rate of sentiment change
    sentiment_volatility: float  # Variance in sentiment
    
    # Source-specific analysis
    source_sentiments: Dict[DataSourceType, Dict[str, float]] = field(default_factory=dict)
    entity_sentiments: Dict[str, Dict[str, float]] = field(default_factory=dict)
    topic_sentiments: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Cognitive insights
    market_themes: List[str] = field(default_factory=list)
    emerging_narratives: List[str] = field(default_factory=list)
    sentiment_catalysts: List[str] = field(default_factory=list)
    risk_signals: List[str] = field(default_factory=list)
    
    # Quality and reliability metrics
    data_quality_score: float = 0.0
    source_reliability_scores: Dict[str, float] = field(default_factory=dict)
    
    # Hypergraph connectivity insights
    narrative_connections: Dict[str, List[str]] = field(default_factory=dict)
    cross_source_correlations: Dict[str, float] = field(default_factory=dict)


@dataclass
class DataIngestionMetrics:
    """Data ingestion performance and quality metrics"""
    source_name: str
    timestamp: datetime
    records_ingested: int
    records_processed: int
    records_rejected: int
    ingestion_rate_per_second: float
    processing_latency_ms: float
    error_rate: float
    data_quality_score: float
    uptime_percentage: float
    last_successful_ingestion: datetime
    
    # Quality breakdown
    schema_violations: int = 0
    duplicate_records: int = 0
    incomplete_records: int = 0
    stale_data_count: int = 0


class DataSource:
    """Base class for data sources"""
    
    def __init__(self, source_name: str, source_type: DataSourceType, config: Dict[str, Any]):
        self.source_name = source_name
        self.source_type = source_type
        self.config = config
        self.is_active = False
        self.last_heartbeat = None
        
    async def initialize(self):
        """Initialize the data source"""
        pass
        
    async def start_ingestion(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Start real-time data ingestion"""
        self.is_active = True
        last_heartbeat = time.time()
        
        while self.is_active:
            try:
                # Simulate data ingestion with appropriate delays based on source type
                if self.source_type == DataSourceType.MARKET_DATA:
                    await asyncio.sleep(1)  # High frequency for market data
                elif self.source_type == DataSourceType.SOCIAL_MEDIA:
                    await asyncio.sleep(5)  # Medium frequency for social media
                else:
                    await asyncio.sleep(30)  # Lower frequency for news and other sources
                
                # Generate sample data based on source type
                sample_data = self._generate_sample_data()
                
                if sample_data:
                    # Update heartbeat
                    self.last_heartbeat = datetime.now()
                    last_heartbeat = time.time()
                    
                    yield sample_data
                
                # Check for timeout (simulate connection issues)
                if time.time() - last_heartbeat > 300:  # 5 minutes timeout
                    logger.warning(f"Data source {self.source_name} heartbeat timeout")
                    await asyncio.sleep(60)  # Wait before retry
                    last_heartbeat = time.time()
                    
            except Exception as e:
                logger.error(f"Error in data ingestion for {self.source_name}: {e}")
                await asyncio.sleep(30)  # Wait before retry
        
    async def stop_ingestion(self):
        """Stop data ingestion"""
        self.is_active = False
        
    def _generate_sample_data(self) -> Optional[Dict[str, Any]]:
        """Generate sample data based on source type"""
        base_data = {
            'source_type': self.source_type.value,
            'source_name': self.source_name,
            'timestamp': datetime.now(),
            'metadata': {}
        }
        
        if self.source_type == DataSourceType.FINANCIAL_NEWS:
            news_templates = [
                "Market volatility increases as {entity} reports {metric}",
                "Fed officials signal potential changes to monetary policy framework", 
                "Technology sector shows strength with {entity} leading gains",
                "Energy markets react to geopolitical developments",
                "Inflation concerns weigh on consumer discretionary stocks"
            ]
            entity = random.choice(['Apple', 'Microsoft', 'Tesla', 'Amazon', 'Google'])
            metric = random.choice(['strong earnings', 'revenue growth', 'guidance update'])
            content = random.choice(news_templates).format(entity=entity, metric=metric)
            
            base_data.update({
                'content': content,
                'metadata': {
                    'category': 'market_news',
                    'entities': [entity],
                    'source_url': f'https://financial-news.com/article-{random.randint(1000, 9999)}'
                }
            })
            
        elif self.source_type == DataSourceType.SOCIAL_MEDIA:
            social_templates = [
                "Just bought more ${symbol}. This rally has legs! #bullish",
                "Fed meeting tomorrow. Expecting {tone} tone. ${symbol} looking interesting", 
                "Market volatility is insane. ${symbol} could be a buying opportunity",
                "Earnings season starting strong. Watching ${symbol} closely",
                "Tech rotation continues. ${symbol} still has upside potential"
            ]
            symbol = random.choice(['SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL'])
            tone = random.choice(['dovish', 'hawkish', 'neutral'])
            content = random.choice(social_templates).format(symbol=symbol, tone=tone)
            
            base_data.update({
                'content': content,
                'metadata': {
                    'platform': random.choice(['twitter', 'reddit', 'stocktwits']),
                    'user_id': f'user_{random.randint(1000, 9999)}',
                    'engagement_score': random.uniform(0.1, 1.0),
                    'symbols_mentioned': [symbol]
                }
            })
            
        elif self.source_type == DataSourceType.MARKET_DATA:
            symbol = random.choice(['SPY', 'QQQ', 'TLT', 'GLD', 'VIX'])
            price_change = random.uniform(-2.0, 2.0)
            volume = random.randint(1000000, 50000000)
            
            content = f"Market update: {symbol} ${350 + price_change:.2f} ({price_change:+.2f}%)"
            
            base_data.update({
                'content': content,
                'metadata': {
                    'symbol': symbol,
                    'price_change_percent': price_change,
                    'volume': volume,
                    'market_cap': random.uniform(1e9, 1e12),
                    'sector': random.choice(['technology', 'financials', 'healthcare', 'energy'])
                }
            })
            
        elif self.source_type == DataSourceType.ECONOMIC_INDICATORS:
            indicators = [
                'GDP growth rate reaches {value}% in latest quarter',
                'Unemployment rate {trend} to {value}%', 
                'Consumer confidence index at {value}',
                'Inflation rate {trend} to {value}% year-over-year',
                'Manufacturing PMI shows {value} reading'
            ]
            value = round(random.uniform(2.0, 8.0), 1)
            trend = random.choice(['rises', 'falls', 'holds steady'])
            content = random.choice(indicators).format(value=value, trend=trend)
            
            base_data.update({
                'content': content,
                'metadata': {
                    'indicator_type': random.choice(['employment', 'inflation', 'growth', 'sentiment']),
                    'value': value,
                    'previous_value': value + random.uniform(-0.5, 0.5),
                    'reporting_agency': random.choice(['BLS', 'Fed', 'Commerce', 'Treasury'])
                }
            })
        else:
            # Default generic financial content
            content = "General financial market update and analysis"
            base_data.update({
                'content': content,
                'metadata': {'type': 'general'}
            })
            
        return base_data

    async def health_check(self) -> bool:
        """Check if data source is healthy"""
        return self.is_active


class NewsDataSource(DataSource):
    """Financial news data source"""
    
    def __init__(self, source_name: str, config: Dict[str, Any]):
        super().__init__(source_name, DataSourceType.FINANCIAL_NEWS, config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.symbols = config.get('symbols', [])
        
    async def start_ingestion(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Ingest financial news data"""
        self.is_active = True
        
        while self.is_active:
            try:
                # Mock news data ingestion
                news_items = await self._fetch_news_data()
                
                for item in news_items:
                    yield {
                        'source_type': self.source_type.value,
                        'source_name': self.source_name,
                        'timestamp': datetime.now(),
                        'content': item['title'] + ' ' + item['content'],
                        'metadata': {
                            'url': item.get('url'),
                            'author': item.get('author'),
                            'category': item.get('category'),
                            'symbols_mentioned': item.get('symbols', [])
                        }
                    }
                
                await asyncio.sleep(30)  # Poll every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in news ingestion for {self.source_name}: {e}")
                await asyncio.sleep(60)
    
    async def _fetch_news_data(self) -> List[Dict[str, Any]]:
        """Fetch news data from API (mock implementation)"""
        # Mock financial news data
        mock_news = [
            {
                'title': 'Federal Reserve Signals Potential Rate Changes',
                'content': 'The Federal Reserve indicated today that interest rate adjustments may be necessary to combat inflation while supporting economic growth.',
                'url': 'https://news.example.com/fed-rates',
                'author': 'Financial Reporter',
                'category': 'monetary_policy',
                'symbols': ['SPY', 'TLT', 'DXY']
            },
            {
                'title': 'Tech Stocks Rally on AI Breakthrough',
                'content': 'Technology stocks surged after a major breakthrough in artificial intelligence capabilities, with investors betting on future growth prospects.',
                'url': 'https://news.example.com/tech-ai',
                'author': 'Tech Analyst', 
                'category': 'technology',
                'symbols': ['QQQ', 'NVDA', 'GOOGL']
            },
            {
                'title': 'Oil Prices Fluctuate on Geopolitical Tensions',
                'content': 'Crude oil prices experienced volatility as geopolitical tensions in key oil-producing regions raised supply concerns among traders.',
                'url': 'https://news.example.com/oil-geopolitics',
                'author': 'Energy Correspondent',
                'category': 'commodities',
                'symbols': ['USO', 'XLE', 'CVX']
            }
        ]
        
        return mock_news


class SocialMediaDataSource(DataSource):
    """Social media sentiment data source"""
    
    def __init__(self, source_name: str, config: Dict[str, Any]):
        super().__init__(source_name, DataSourceType.SOCIAL_MEDIA, config)
        self.platforms = config.get('platforms', ['twitter', 'reddit'])
        self.keywords = config.get('keywords', [])
        
    async def start_ingestion(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Ingest social media data"""
        self.is_active = True
        
        while self.is_active:
            try:
                social_posts = await self._fetch_social_data()
                
                for post in social_posts:
                    yield {
                        'source_type': self.source_type.value,
                        'source_name': self.source_name,
                        'timestamp': datetime.now(),
                        'content': post['text'],
                        'metadata': {
                            'platform': post['platform'],
                            'user': post.get('user'),
                            'engagement': post.get('engagement', {}),
                            'hashtags': post.get('hashtags', []),
                            'mentions': post.get('mentions', [])
                        }
                    }
                
                await asyncio.sleep(10)  # Higher frequency for social media
                
            except Exception as e:
                logger.error(f"Error in social media ingestion for {self.source_name}: {e}")
                await asyncio.sleep(30)
    
    async def _fetch_social_data(self) -> List[Dict[str, Any]]:
        """Fetch social media data (mock implementation)"""
        # Mock social media posts
        mock_posts = [
            {
                'text': 'Just bought more $SPY calls. This market rally has legs! #bullish #stocks',
                'platform': 'twitter',
                'user': '@trader_joe123',
                'engagement': {'likes': 45, 'retweets': 12, 'replies': 8},
                'hashtags': ['bullish', 'stocks'],
                'mentions': []
            },
            {
                'text': 'Fed meeting tomorrow. Expecting dovish tone but market already pricing it in. $TLT looking interesting.',
                'platform': 'reddit',
                'user': 'fixed_income_guy',
                'engagement': {'upvotes': 127, 'comments': 23},
                'hashtags': [],
                'mentions': []
            },
            {
                'text': 'Oil volatility is insane right now. Can\'t decide if this is a buying opportunity or a falling knife. $USO',
                'platform': 'twitter',
                'user': '@energy_trader',
                'engagement': {'likes': 78, 'retweets': 34, 'replies': 19},
                'hashtags': [],
                'mentions': []
            }
        ]
        
        return mock_posts


class MarketDataSource(DataSource):
    """Real-time market data source"""
    
    def __init__(self, source_name: str, config: Dict[str, Any]):
        super().__init__(source_name, DataSourceType.MARKET_DATA, config)
        self.symbols = config.get('symbols', [])
        self.data_types = config.get('data_types', ['price', 'volume'])
        
    async def start_ingestion(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Ingest real-time market data"""
        self.is_active = True
        
        while self.is_active:
            try:
                market_data = await self._fetch_market_data()
                
                for data_point in market_data:
                    yield {
                        'source_type': self.source_type.value,
                        'source_name': self.source_name,
                        'timestamp': datetime.now(),
                        'content': f"Market update: {data_point['symbol']} at {data_point['price']}",
                        'metadata': {
                            'symbol': data_point['symbol'],
                            'price': data_point['price'],
                            'volume': data_point['volume'],
                            'change': data_point['change'],
                            'change_percent': data_point['change_percent']
                        }
                    }
                
                await asyncio.sleep(1)  # Real-time updates
                
            except Exception as e:
                logger.error(f"Error in market data ingestion for {self.source_name}: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_market_data(self) -> List[Dict[str, Any]]:
        """Fetch market data (mock implementation)"""
        import random
        
        mock_data = []
        for symbol in self.symbols:
            base_price = {'SPY': 450.0, 'QQQ': 375.0, 'TLT': 95.0}.get(symbol, 100.0)
            change = random.uniform(-2.0, 2.0)
            price = base_price + change
            
            mock_data.append({
                'symbol': symbol,
                'price': price,
                'volume': random.randint(1000000, 10000000),
                'change': change,
                'change_percent': (change / base_price) * 100
            })
        
        return mock_data


class RealTimeSentimentAnalyzer:
    """Advanced real-time sentiment analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_sources: Dict[str, DataSource] = {}
        self.sentiment_models = {}
        self.ingestion_tasks = {}
        self.sentiment_history: Dict[str, List[SentimentData]] = {}
        self.synthesis_history: List[CognitiveSentimentSynthesis] = []
        self.ingestion_metrics: Dict[str, DataIngestionMetrics] = {}
        
        # Initialize directories
        self.base_path = Path(self.config.get('base_path', './sentiment_analysis'))
        self.data_path = self.base_path / 'data'
        self.models_path = self.base_path / 'models'
        self.reports_path = self.base_path / 'reports'
        
        self._ensure_directories()
        self._initialize_sentiment_models()
        
    def _ensure_directories(self):
        """Create necessary directories"""
        for path in [self.base_path, self.data_path, self.models_path, self.reports_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_sentiment_models(self):
        """Initialize sentiment analysis models"""
        # Mock model initialization - in production would load actual NLP models
        self.sentiment_models = {
            'financial_bert': {
                'model_type': 'transformer',
                'accuracy': 0.89,
                'confidence_threshold': 0.7,
                'specialization': 'financial_language'
            },
            'social_media_classifier': {
                'model_type': 'ensemble',
                'accuracy': 0.82,
                'confidence_threshold': 0.6,
                'specialization': 'social_media_language'
            },
            'market_news_analyzer': {
                'model_type': 'lstm_attention',
                'accuracy': 0.85,
                'confidence_threshold': 0.75,
                'specialization': 'market_news'
            }
        }
        
        logger.info(f"Initialized {len(self.sentiment_models)} sentiment models")
    
    async def register_data_source(self, source: DataSource):
        """Register a new data source"""
        await source.initialize()
        self.data_sources[source.source_name] = source
        
        # Initialize metrics tracking
        self.ingestion_metrics[source.source_name] = DataIngestionMetrics(
            source_name=source.source_name,
            timestamp=datetime.now(),
            records_ingested=0,
            records_processed=0,
            records_rejected=0,
            ingestion_rate_per_second=0.0,
            processing_latency_ms=0.0,
            error_rate=0.0,
            data_quality_score=1.0,
            uptime_percentage=100.0,
            last_successful_ingestion=datetime.now()
        )
        
        logger.info(f"Registered data source: {source.source_name} ({source.source_type.value})")
    
    async def start_real_time_ingestion(self):
        """Start real-time data ingestion from all sources"""
        for source_name, source in self.data_sources.items():
            if source_name not in self.ingestion_tasks:
                task = asyncio.create_task(self._ingest_from_source(source))
                self.ingestion_tasks[source_name] = task
                logger.info(f"Started ingestion from {source_name}")
        
        # Start cognitive synthesis task
        synthesis_task = asyncio.create_task(self._cognitive_synthesis_loop())
        self.ingestion_tasks['cognitive_synthesis'] = synthesis_task
        
        logger.info("Started real-time sentiment analysis system")
    
    async def stop_real_time_ingestion(self):
        """Stop real-time data ingestion"""
        for source_name, task in self.ingestion_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.ingestion_tasks.clear()
        
        for source in self.data_sources.values():
            await source.stop_ingestion()
        
        logger.info("Stopped real-time sentiment analysis system")
    
    async def _ingest_from_source(self, source: DataSource):
        """Ingest and process data from a specific source"""
        metrics = self.ingestion_metrics[source.source_name]
        last_update = datetime.now()
        
        try:
            async for raw_data in source.start_ingestion():
                start_time = datetime.now()
                
                try:
                    # Process raw data into sentiment data
                    sentiment_data = await self._process_raw_data(raw_data)
                    
                    if sentiment_data:
                        # Store sentiment data
                        source_key = f"{sentiment_data.source_type.value}_{sentiment_data.source_name}"
                        if source_key not in self.sentiment_history:
                            self.sentiment_history[source_key] = []
                        
                        self.sentiment_history[source_key].append(sentiment_data)
                        
                        # Keep only recent data (last 10000 records)
                        if len(self.sentiment_history[source_key]) > 10000:
                            self.sentiment_history[source_key] = self.sentiment_history[source_key][-10000:]
                        
                        # Update metrics
                        metrics.records_ingested += 1
                        metrics.records_processed += 1
                        metrics.last_successful_ingestion = datetime.now()
                        
                    else:
                        metrics.records_rejected += 1
                        
                    # Calculate processing latency
                    processing_time = (datetime.now() - start_time).total_seconds() * 1000
                    metrics.processing_latency_ms = (
                        metrics.processing_latency_ms * 0.9 + processing_time * 0.1
                    )  # Exponential moving average
                    
                except Exception as e:
                    logger.error(f"Error processing data from {source.source_name}: {e}")
                    metrics.records_rejected += 1
                    
                # Update ingestion rate periodically
                now = datetime.now()
                if (now - last_update).total_seconds() >= 60:  # Every minute
                    time_diff = (now - last_update).total_seconds()
                    rate = metrics.records_processed / time_diff
                    metrics.ingestion_rate_per_second = rate
                    
                    # Reset counters
                    metrics.records_processed = 0
                    last_update = now
                    
                    # Update error rate
                    total_records = metrics.records_ingested + metrics.records_rejected
                    if total_records > 0:
                        metrics.error_rate = metrics.records_rejected / total_records
                    
                    # Save updated metrics
                    await self._save_ingestion_metrics(metrics)
                        
        except asyncio.CancelledError:
            logger.info(f"Ingestion cancelled for {source.source_name}")
        except Exception as e:
            logger.error(f"Fatal error in ingestion for {source.source_name}: {e}")
    
    async def _process_raw_data(self, raw_data: Dict[str, Any]) -> Optional[SentimentData]:
        """Process raw data into structured sentiment data"""
        
        try:
            # Extract basic fields
            source_type = DataSourceType(raw_data['source_type'])
            source_name = raw_data['source_name']
            content = raw_data['content']
            timestamp = raw_data['timestamp']
            metadata = raw_data.get('metadata', {})
            
            # Data quality checks
            if not content or len(content.strip()) < 10:
                return None  # Insufficient content
            
            if not self._is_financial_relevant(content):
                return None  # Not financially relevant
            
            # Clean and preprocess content
            processed_content = self._preprocess_text(content)
            
            # Analyze sentiment
            sentiment_result = await self._analyze_sentiment(processed_content, source_type)
            
            # Extract entities and topics
            entities = self._extract_entities(processed_content)
            topics = self._extract_topics(processed_content)
            keywords = self._extract_keywords(processed_content)
            
            # Generate data ID
            data_id = self._generate_data_id(source_name, timestamp, content)
            
            return SentimentData(
                data_id=data_id,
                source_type=source_type,
                source_name=source_name,
                timestamp=timestamp,
                content=content,
                processed_content=processed_content,
                sentiment_polarity=sentiment_result['polarity'],
                sentiment_score=sentiment_result['score'],
                confidence=sentiment_result['confidence'],
                entities=entities,
                topics=topics,
                keywords=keywords,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing raw data: {e}")
            return None
    
    def _is_financial_relevant(self, content: str) -> bool:
        """Check if content is financially relevant"""
        financial_keywords = [
            'stock', 'market', 'trading', 'investment', 'portfolio', 'price', 'earnings',
            'fed', 'interest', 'rate', 'inflation', 'gdp', 'economy', 'bull', 'bear',
            'buy', 'sell', 'hold', 'crypto', 'bitcoin', 'bond', 'yield', 'dollar'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in financial_keywords)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s!?.,;:]', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def _analyze_sentiment(self, text: str, source_type: DataSourceType) -> Dict[str, Any]:
        """Analyze sentiment using appropriate model"""
        
        # Select model based on source type
        if source_type == DataSourceType.SOCIAL_MEDIA:
            model_name = 'social_media_classifier'
        elif source_type == DataSourceType.FINANCIAL_NEWS:
            model_name = 'market_news_analyzer'
        else:
            model_name = 'financial_bert'
        
        model_config = self.sentiment_models[model_name]
        
        # Mock sentiment analysis - in production would use actual NLP models
        import random
        
        # Generate sentiment based on keywords
        positive_words = ['bullish', 'buy', 'growth', 'profit', 'gain', 'rally', 'surge', 'rise']
        negative_words = ['bearish', 'sell', 'loss', 'decline', 'crash', 'fall', 'drop', 'risk']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score
        if positive_score > negative_score:
            if positive_score >= 3:
                polarity = SentimentPolarity.VERY_POSITIVE
                score = 0.8 + random.uniform(0, 0.2)
            else:
                polarity = SentimentPolarity.POSITIVE
                score = 0.6 + random.uniform(0, 0.2)
        elif negative_score > positive_score:
            if negative_score >= 3:
                polarity = SentimentPolarity.VERY_NEGATIVE
                score = -0.8 - random.uniform(0, 0.2)
            else:
                polarity = SentimentPolarity.NEGATIVE
                score = -0.6 - random.uniform(0, 0.2)
        else:
            polarity = SentimentPolarity.NEUTRAL
            score = random.uniform(-0.1, 0.1)
        
        # Calculate confidence based on model accuracy and text clarity
        base_confidence = model_config['accuracy']
        text_confidence = min(1.0, len(text.split()) / 10)  # Longer text = higher confidence
        confidence = base_confidence * text_confidence
        
        return {
            'polarity': polarity,
            'score': score,
            'confidence': confidence,
            'model_used': model_name
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract financial entities from text"""
        # Mock entity extraction - in production would use NER models
        financial_entities = []
        
        # Stock symbols pattern
        stock_pattern = r'\$[A-Z]{1,5}'
        stocks = re.findall(stock_pattern, text)
        financial_entities.extend(stocks)
        
        # Company names (simplified)
        companies = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla', 'Meta', 'Netflix']
        for company in companies:
            if company.lower() in text.lower():
                financial_entities.append(company)
        
        # Economic indicators
        indicators = ['Fed', 'GDP', 'CPI', 'unemployment', 'inflation']
        for indicator in indicators:
            if indicator.lower() in text.lower():
                financial_entities.append(indicator)
        
        return list(set(financial_entities))
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract financial topics from text"""
        # Mock topic extraction
        topic_keywords = {
            'monetary_policy': ['fed', 'interest rate', 'central bank', 'qe', 'taper'],
            'earnings': ['earnings', 'revenue', 'profit', 'eps', 'guidance'],
            'technology': ['ai', 'artificial intelligence', 'tech', 'software', 'hardware'],
            'energy': ['oil', 'gas', 'renewable', 'energy', 'crude'],
            'crypto': ['bitcoin', 'cryptocurrency', 'crypto', 'blockchain'],
            'geopolitics': ['war', 'trade', 'sanctions', 'tension', 'conflict']
        }
        
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction - in production would use TF-IDF or similar
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return most frequent keywords
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(10)]
    
    def _generate_data_id(self, source_name: str, timestamp: datetime, content: str) -> str:
        """Generate unique data ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        return f"{source_name}_{timestamp_str}_{content_hash}"
    
    async def _cognitive_synthesis_loop(self):
        """Continuous cognitive synthesis of sentiment data"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Perform cognitive synthesis
                synthesis = await self._perform_cognitive_synthesis()
                
                if synthesis:
                    self.synthesis_history.append(synthesis)
                    
                    # Keep only recent synthesis history
                    if len(self.synthesis_history) > 1000:
                        self.synthesis_history = self.synthesis_history[-1000:]
                    
                    # Save synthesis report
                    await self._save_synthesis_report(synthesis)
                    
                    logger.info(f"Generated cognitive synthesis: {synthesis.overall_sentiment.name} "
                              f"(confidence: {synthesis.confidence:.2f})")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cognitive synthesis loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_cognitive_synthesis(self) -> Optional[CognitiveSentimentSynthesis]:
        """Perform cognitive synthesis of recent sentiment data"""
        
        # Collect recent sentiment data from all sources
        time_window = timedelta(minutes=15)  # 15-minute synthesis window
        cutoff_time = datetime.now() - time_window
        
        recent_data = []
        for source_key, data_list in self.sentiment_history.items():
            recent_source_data = [data for data in data_list if data.timestamp >= cutoff_time]
            recent_data.extend(recent_source_data)
        
        if len(recent_data) < 5:  # Need minimum data for synthesis
            return None
        
        # Aggregate sentiment by source type
        source_sentiments = {}
        for source_type in DataSourceType:
            source_data = [data for data in recent_data if data.source_type == source_type]
            if source_data:
                avg_sentiment = sum(data.sentiment_score for data in source_data) / len(source_data)
                avg_confidence = sum(data.confidence for data in source_data) / len(source_data)
                source_sentiments[source_type] = {
                    'score': avg_sentiment,
                    'confidence': avg_confidence,
                    'count': len(source_data)
                }
        
        # Aggregate sentiment by entities
        entity_sentiments = {}
        for data in recent_data:
            for entity in data.entities:
                if entity not in entity_sentiments:
                    entity_sentiments[entity] = []
                entity_sentiments[entity].append(data.sentiment_score)
        
        # Calculate averages for entities
        for entity in entity_sentiments:
            scores = entity_sentiments[entity]
            entity_sentiments[entity] = {
                'score': sum(scores) / len(scores),
                'count': len(scores),
                'volatility': statistics.stdev(scores) if len(scores) > 1 else 0
            }
        
        # Aggregate sentiment by topics
        topic_sentiments = {}
        for data in recent_data:
            for topic in data.topics:
                if topic not in topic_sentiments:
                    topic_sentiments[topic] = []
                topic_sentiments[topic].append(data.sentiment_score)
        
        # Calculate averages for topics
        for topic in topic_sentiments:
            scores = topic_sentiments[topic]
            topic_sentiments[topic] = {
                'score': sum(scores) / len(scores),
                'count': len(scores),
                'volatility': statistics.stdev(scores) if len(scores) > 1 else 0
            }
        
        # Calculate overall metrics
        all_scores = [data.sentiment_score for data in recent_data]
        all_confidences = [data.confidence for data in recent_data]
        
        overall_sentiment_score = statistics.mean(all_scores)
        overall_confidence = statistics.mean(all_confidences)
        sentiment_volatility = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
        
        # Calculate sentiment momentum (trend over time)
        if len(recent_data) >= 10:
            sorted_data = sorted(recent_data, key=lambda x: x.timestamp)
            first_half = sorted_data[:len(sorted_data)//2]
            second_half = sorted_data[len(sorted_data)//2:]
            
            first_avg = statistics.mean([data.sentiment_score for data in first_half])
            second_avg = statistics.mean([data.sentiment_score for data in second_half])
            sentiment_momentum = second_avg - first_avg
        else:
            sentiment_momentum = 0.0
        
        # Determine overall sentiment polarity
        if overall_sentiment_score >= 0.6:
            overall_polarity = SentimentPolarity.VERY_POSITIVE
        elif overall_sentiment_score >= 0.2:
            overall_polarity = SentimentPolarity.POSITIVE
        elif overall_sentiment_score >= -0.2:
            overall_polarity = SentimentPolarity.NEUTRAL
        elif overall_sentiment_score >= -0.6:
            overall_polarity = SentimentPolarity.NEGATIVE
        else:
            overall_polarity = SentimentPolarity.VERY_NEGATIVE
        
        # Extract market themes and narratives
        market_themes = self._extract_market_themes(recent_data)
        emerging_narratives = self._identify_emerging_narratives(recent_data)
        sentiment_catalysts = self._identify_sentiment_catalysts(recent_data)
        risk_signals = self._identify_risk_signals(recent_data)
        
        # Calculate data quality score
        data_quality_score = statistics.mean([data.confidence for data in recent_data])
        
        # Generate synthesis ID
        synthesis_id = f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return CognitiveSentimentSynthesis(
            synthesis_id=synthesis_id,
            timestamp=datetime.now(),
            time_window=time_window,
            source_count=len(set(data.source_name for data in recent_data)),
            data_points_analyzed=len(recent_data),
            overall_sentiment=overall_polarity,
            confidence=overall_confidence,
            sentiment_momentum=sentiment_momentum,
            sentiment_volatility=sentiment_volatility,
            source_sentiments=source_sentiments,
            entity_sentiments=entity_sentiments,
            topic_sentiments=topic_sentiments,
            market_themes=market_themes,
            emerging_narratives=emerging_narratives,
            sentiment_catalysts=sentiment_catalysts,
            risk_signals=risk_signals,
            data_quality_score=data_quality_score
        )
    
    def _extract_market_themes(self, data_list: List[SentimentData]) -> List[str]:
        """Extract dominant market themes"""
        # Count topic occurrences
        topic_counts = {}
        for data in data_list:
            for topic in data.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Return top themes
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:5]]
    
    def _identify_emerging_narratives(self, data_list: List[SentimentData]) -> List[str]:
        """Identify emerging market narratives"""
        # Mock implementation - would use more sophisticated NLP
        narratives = []
        
        # Check for sudden increases in specific entity mentions
        entity_mentions = {}
        for data in data_list:
            for entity in data.entities:
                entity_mentions[entity] = entity_mentions.get(entity, 0) + 1
        
        # Identify entities with high mention rates
        high_mention_entities = [entity for entity, count in entity_mentions.items() if count >= 3]
        
        if 'Fed' in high_mention_entities:
            narratives.append("Increased focus on monetary policy decisions")
        if any('$' in entity for entity in high_mention_entities):
            narratives.append("Heightened individual stock attention")
        
        return narratives[:3]
    
    def _identify_sentiment_catalysts(self, data_list: List[SentimentData]) -> List[str]:
        """Identify key sentiment catalysts"""
        catalysts = []
        
        # Look for high-impact keywords
        catalyst_keywords = {
            'earnings': "Earnings announcements driving sentiment",
            'fed': "Federal Reserve actions/communications",
            'inflation': "Inflation concerns impacting market mood",
            'war': "Geopolitical tensions affecting markets",
            'breakthrough': "Technology/innovation developments"
        }
        
        for data in data_list:
            content_lower = data.content.lower()
            for keyword, catalyst in catalyst_keywords.items():
                if keyword in content_lower and catalyst not in catalysts:
                    catalysts.append(catalyst)
        
        return catalysts[:5]
    
    def _identify_risk_signals(self, data_list: List[SentimentData]) -> List[str]:
        """Identify potential risk signals"""
        risk_signals = []
        
        # High volatility in sentiment
        sentiment_scores = [data.sentiment_score for data in data_list]
        if len(sentiment_scores) > 5 and statistics.stdev(sentiment_scores) > 0.5:
            risk_signals.append("High sentiment volatility detected")
        
        # Sudden negative shift
        if len(sentiment_scores) >= 10:
            recent_avg = statistics.mean(sentiment_scores[-5:])
            earlier_avg = statistics.mean(sentiment_scores[:-5])
            if recent_avg < earlier_avg - 0.3:
                risk_signals.append("Rapid sentiment deterioration")
        
        # Look for risk keywords
        risk_keywords = ['crash', 'collapse', 'crisis', 'bubble', 'correction']
        risk_mentions = 0
        for data in data_list:
            content_lower = data.content.lower()
            risk_mentions += sum(1 for keyword in risk_keywords if keyword in content_lower)
        
        if risk_mentions >= 3:
            risk_signals.append("Increased risk-related language in discussions")
        
        return risk_signals[:5]
    
    async def _save_synthesis_report(self, synthesis: CognitiveSentimentSynthesis):
        """Save cognitive synthesis report"""
        report_file = self.reports_path / f"{synthesis.synthesis_id}.json"
        
        report_dict = {
            'synthesis_id': synthesis.synthesis_id,
            'timestamp': synthesis.timestamp.isoformat(),
            'time_window_minutes': synthesis.time_window.total_seconds() / 60,
            'source_count': synthesis.source_count,
            'data_points_analyzed': synthesis.data_points_analyzed,
            'overall_sentiment': synthesis.overall_sentiment.name,
            'confidence': synthesis.confidence,
            'sentiment_momentum': synthesis.sentiment_momentum,
            'sentiment_volatility': synthesis.sentiment_volatility,
            'source_sentiments': {
                source_type.value: metrics for source_type, metrics in synthesis.source_sentiments.items()
            },
            'entity_sentiments': synthesis.entity_sentiments,
            'topic_sentiments': synthesis.topic_sentiments,
            'market_themes': synthesis.market_themes,
            'emerging_narratives': synthesis.emerging_narratives,
            'sentiment_catalysts': synthesis.sentiment_catalysts,
            'risk_signals': synthesis.risk_signals,
            'data_quality_score': synthesis.data_quality_score
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
    
    async def _save_ingestion_metrics(self, metrics: DataIngestionMetrics):
        """Save ingestion metrics"""
        metrics_file = self.data_path / f"{metrics.source_name}_metrics.json"
        
        metrics_dict = {
            'source_name': metrics.source_name,
            'timestamp': metrics.timestamp.isoformat(),
            'records_ingested': metrics.records_ingested,
            'records_processed': metrics.records_processed,
            'records_rejected': metrics.records_rejected,
            'ingestion_rate_per_second': metrics.ingestion_rate_per_second,
            'processing_latency_ms': metrics.processing_latency_ms,
            'error_rate': metrics.error_rate,
            'data_quality_score': metrics.data_quality_score,
            'uptime_percentage': metrics.uptime_percentage,
            'last_successful_ingestion': metrics.last_successful_ingestion.isoformat(),
            'schema_violations': metrics.schema_violations,
            'duplicate_records': metrics.duplicate_records,
            'incomplete_records': metrics.incomplete_records,
            'stale_data_count': metrics.stale_data_count
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
    
    def get_current_sentiment_synthesis(self) -> Optional[Dict[str, Any]]:
        """Get the most recent cognitive sentiment synthesis"""
        if not self.synthesis_history:
            return None
        
        latest = self.synthesis_history[-1]
        
        return {
            'synthesis_id': latest.synthesis_id,
            'timestamp': latest.timestamp.isoformat(),
            'overall_sentiment': latest.overall_sentiment.name,
            'confidence': latest.confidence,
            'sentiment_momentum': latest.sentiment_momentum,
            'sentiment_volatility': latest.sentiment_volatility,
            'market_themes': latest.market_themes,
            'emerging_narratives': latest.emerging_narratives,
            'sentiment_catalysts': latest.sentiment_catalysts,
            'risk_signals': latest.risk_signals,
            'data_quality_score': latest.data_quality_score,
            'source_count': latest.source_count,
            'data_points_analyzed': latest.data_points_analyzed
        }
    
    def get_source_metrics(self, source_name: Optional[str] = None) -> Dict[str, Any]:
        """Get ingestion metrics for data sources"""
        if source_name and source_name in self.ingestion_metrics:
            metrics = self.ingestion_metrics[source_name]
            return {
                'source_name': metrics.source_name,
                'records_ingested': metrics.records_ingested,
                'ingestion_rate_per_second': metrics.ingestion_rate_per_second,
                'processing_latency_ms': metrics.processing_latency_ms,
                'error_rate': metrics.error_rate,
                'data_quality_score': metrics.data_quality_score,
                'uptime_percentage': metrics.uptime_percentage,
                'last_successful_ingestion': metrics.last_successful_ingestion.isoformat()
            }
        else:
            # Return all sources
            return {
                source_name: {
                    'records_ingested': metrics.records_ingested,
                    'ingestion_rate_per_second': metrics.ingestion_rate_per_second,
                    'error_rate': metrics.error_rate,
                    'data_quality_score': metrics.data_quality_score,
                    'uptime_percentage': metrics.uptime_percentage
                }
                for source_name, metrics in self.ingestion_metrics.items()
            }
    
    def get_sentiment_history(self, hours: int = 24) -> Dict[str, Any]:
        """Get sentiment history for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Collect recent data
        recent_syntheses = [
            synthesis for synthesis in self.synthesis_history
            if synthesis.timestamp >= cutoff_time
        ]
        
        if not recent_syntheses:
            return {'message': 'No sentiment data available for the specified period'}
        
        return {
            'time_period_hours': hours,
            'synthesis_count': len(recent_syntheses),
            'sentiment_timeline': [
                {
                    'timestamp': synthesis.timestamp.isoformat(),
                    'overall_sentiment': synthesis.overall_sentiment.name,
                    'confidence': synthesis.confidence,
                    'sentiment_score': synthesis.sentiment_momentum,
                    'market_themes': synthesis.market_themes
                }
                for synthesis in recent_syntheses
            ]
        }
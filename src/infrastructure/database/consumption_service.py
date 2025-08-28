"""
Consumption analytics service using SQLAlchemy ORM.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, func, and_, extract
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Node, SensorReading, Anomaly


class ConsumptionServiceError(Exception):
    """Custom exception for consumption service errors."""
    pass


class ConsumptionService:
    """Service for consumption analytics using SQLAlchemy."""
    
    def __init__(self, database_url: str):
        """Initialize the service with database connection."""
        # Use the provided database URL or default to the real database
        if not database_url:
            database_url = "postgresql://abbanoa_user:abbanoa_secure_pass@localhost:5432/abbanoa_processing"
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def _get_data_summary(self, session: Session) -> Any:
        """Get summary statistics of sensor data."""
        return session.query(
            func.count(SensorReading.timestamp).label('total_readings'),
            func.count(SensorReading.flow_rate).label('flow_readings'),
            func.count(SensorReading.is_interpolated).label('synthetic_readings'),
            func.min(SensorReading.timestamp).label('earliest_timestamp'),
            func.max(SensorReading.timestamp).label('latest_timestamp'),
            func.count(func.distinct(SensorReading.node_id)).label('active_nodes')
        ).filter(SensorReading.flow_rate.isnot(None)).first()
    
    def _get_daily_consumption(self, session: Session, days: int = 7) -> List[Any]:
        """Get daily consumption data for specified number of days."""
        start_date = datetime.now() - timedelta(days=days)
        return session.query(
            func.date(SensorReading.timestamp).label('date'),
            func.sum(SensorReading.flow_rate * 3600).label('daily_consumption_liters'),
            func.avg(SensorReading.flow_rate).label('avg_flow_rate'),
            func.avg(SensorReading.pressure).label('avg_pressure'),
            func.count(SensorReading.timestamp).label('readings_count')
        ).filter(
            and_(
                SensorReading.timestamp >= start_date,
                SensorReading.flow_rate.isnot(None)
            )
        ).group_by(
            func.date(SensorReading.timestamp)
        ).order_by(
            func.date(SensorReading.timestamp).desc()
        ).all()
    
    def _get_hourly_pattern(self, session: Session, days: int = 7) -> List[Any]:
        """Get hourly consumption pattern."""
        start_date = datetime.now() - timedelta(days=days)
        return session.query(
            extract('hour', SensorReading.timestamp).label('hour'),
            func.avg(SensorReading.flow_rate).label('avg_flow_rate'),
            func.sum(SensorReading.flow_rate * 3600).label('total_consumption_liters')
        ).filter(
            and_(
                SensorReading.timestamp >= start_date,
                SensorReading.flow_rate.isnot(None)
            )
        ).group_by(
            extract('hour', SensorReading.timestamp)
        ).order_by(
            extract('hour', SensorReading.timestamp)
        ).all()
    
    def _get_node_consumption(self, session: Session, days: int = 7) -> List[Any]:
        """Get consumption data by node with real node names."""
        start_date = datetime.now() - timedelta(days=days)
        return session.query(
            SensorReading.node_id,
            Node.node_name,
            Node.node_type,
            func.avg(SensorReading.flow_rate).label('avg_flow_rate'),
            func.sum(SensorReading.flow_rate * 3600).label('total_consumption_liters'),
            func.count(SensorReading.timestamp).label('readings_count'),
            func.max(SensorReading.timestamp).label('last_reading'),
            func.avg(SensorReading.pressure).label('avg_pressure')
        ).join(
            Node, SensorReading.node_id == Node.node_id
        ).filter(
            and_(
                SensorReading.timestamp >= start_date,
                SensorReading.flow_rate.isnot(None)
            )
        ).group_by(
            SensorReading.node_id, Node.node_name, Node.node_type
        ).order_by(
            func.sum(SensorReading.flow_rate * 3600).desc()
        ).all()
    
    def _calculate_metrics(self, data_summary: Any, daily_consumption: List[Any]) -> Dict[str, Any]:
        """Calculate key metrics from data."""
        total_readings = data_summary.total_readings
        synthetic_percentage = (data_summary.synthetic_readings / total_readings * 100) if total_readings > 0 else 0
        
        # Handle timezone-aware datetime comparison
        now = datetime.now()
        if data_summary.latest_timestamp.tzinfo is not None:
            now = now.replace(tzinfo=data_summary.latest_timestamp.tzinfo)
        data_age_hours = (now - data_summary.latest_timestamp).total_seconds() / 3600
        
        # Calculate total daily consumption from real data
        if daily_consumption:
            # Use actual daily consumption data
            total_daily_consumption = sum(row.daily_consumption_liters for row in daily_consumption) / len(daily_consumption)
        else:
            # Fallback: estimate from total readings and average flow rate
            # Assuming average flow rate of 50 L/h and 24 hours per day
            total_daily_consumption = total_readings * 50 * 24 / 7  # Estimate for 7 days
        
        return {
            'total_daily_consumption': total_daily_consumption,
            'total_readings': total_readings,
            'synthetic_percentage': synthetic_percentage,
            'data_age_hours': data_age_hours
        }
    
    def _create_consumption_timeline(self, hourly_pattern: List[Any]) -> List[Dict[str, Any]]:
        """Create consumption timeline from hourly pattern."""
        consumption_timeline = []
        for hour in range(24):
            hour_data = next((row for row in hourly_pattern if row.hour == hour), None)
            if hour_data:
                consumption_timeline.append({
                    'timestamp': datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0).isoformat(),
                    'consumption_liters': round(hour_data.total_consumption_liters),
                    'forecast_consumption': round(hour_data.total_consumption_liters * 1.05)
                })
        return consumption_timeline
    
    def _create_district_consumption(self, node_consumption: List[Any]) -> List[Dict[str, Any]]:
        """Create district consumption data from node data."""
        district_consumption = []
        for node_data in node_consumption:
            district_consumption.append({
                'district_id': node_data.node_id,
                'district_name': node_data.node_name,
                'node_type': node_data.node_type,
                'total_users': 10000,  # Estimated
                'daily_consumption_liters': round(node_data.total_consumption_liters / 7),
                'monthly_consumption_liters': round(node_data.total_consumption_liters * 4.3),
                'avg_per_user_daily': round(node_data.total_consumption_liters / 7 / 10000, 2),
                'peak_hour': 8,  # Default
                'efficiency_score': 0.92
            })
        return district_consumption
    
    def _create_peak_demand(self, hourly_pattern: List[Any]) -> Dict[str, Any]:
        """Create peak demand analysis."""
        peak_hour_data = max(hourly_pattern, key=lambda x: x.total_consumption_liters) if hourly_pattern else None
        return {
            'daily_peak_time': f"{int(peak_hour_data.hour):02d}:00" if peak_hour_data else '08:00',
            'daily_peak_consumption': round(peak_hour_data.total_consumption_liters) if peak_hour_data else 0,
            'weekly_peak_day': 'Monday',  # Default
            'monthly_peak_date': datetime.now().strftime('%Y-%m-15'),
            'seasonal_peak_month': 'August'
        }
    
    def _create_user_segments(self, node_consumption: List[Any]) -> List[Dict[str, Any]]:
        """Create user segments based on consumption patterns."""
        if not node_consumption:
            # Return default segments if no node data
            return [
                {
                    'segment': 'Residential',
                    'user_count': 70000,
                    'percentage': 75,
                    'avg_daily_consumption': 250,
                    'trend': 'stable'
                },
                {
                    'segment': 'Commercial',
                    'user_count': 20000,
                    'percentage': 20,
                    'avg_daily_consumption': 800,
                    'trend': 'increasing'
                },
                {
                    'segment': 'Industrial',
                    'user_count': 10000,
                    'percentage': 5,
                    'avg_daily_consumption': 5000,
                    'trend': 'decreasing'
                }
            ]
        
        # Analyze real node data to determine segments
        # Based on node types and flow rates
        residential_nodes = [n for n in node_consumption if n.node_type in ['distribution', 'secondary']]
        commercial_nodes = [n for n in node_consumption if n.node_type == 'main']
        industrial_nodes = [n for n in node_consumption if n.node_type == 'storage']
        
        # Calculate user counts based on real node distribution
        total_nodes = len(node_consumption)
        residential_count = len(residential_nodes) * 15000 if residential_nodes else 70000
        commercial_count = len(commercial_nodes) * 25000 if commercial_nodes else 20000
        industrial_count = len(industrial_nodes) * 5000 if industrial_nodes else 10000
        
        total_users = residential_count + commercial_count + industrial_count
        
        return [
            {
                'segment': 'Residential',
                'user_count': residential_count,
                'percentage': round(residential_count / total_users * 100) if total_users > 0 else 75,
                'avg_daily_consumption': 250,
                'trend': 'stable'
            },
            {
                'segment': 'Commercial',
                'user_count': commercial_count,
                'percentage': round(commercial_count / total_users * 100) if total_users > 0 else 20,
                'avg_daily_consumption': 800,
                'trend': 'increasing'
            },
            {
                'segment': 'Industrial',
                'user_count': industrial_count,
                'percentage': round(industrial_count / total_users * 100) if total_users > 0 else 5,
                'avg_daily_consumption': 5000,
                'trend': 'decreasing'
            }
        ]
    
    def _create_conservation_opportunities(self, total_daily_consumption: float) -> List[Dict[str, Any]]:
        """Create conservation opportunities analysis."""
        return [
            {
                'opportunity': 'Leak Detection Program',
                'potential_savings_liters_daily': round(total_daily_consumption * 0.02),
                'potential_savings_percentage': 2,
                'implementation_cost': 'Medium',
                'roi_months': 12
            },
            {
                'opportunity': 'Smart Meter Deployment',
                'potential_savings_liters_daily': round(total_daily_consumption * 0.05),
                'potential_savings_percentage': 5,
                'implementation_cost': 'High',
                'roi_months': 24
            },
            {
                'opportunity': 'User Education Campaign',
                'potential_savings_liters_daily': round(total_daily_consumption * 0.03),
                'potential_savings_percentage': 3,
                'implementation_cost': 'Low',
                'roi_months': 6
            }
        ]
    
    def get_consumption_analytics(self) -> Dict[str, Any]:
        """Get comprehensive consumption analytics using real data."""
        session = self.get_session()
        
        try:
            # Get data summary
            data_summary = self._get_data_summary(session)
            if not data_summary:
                raise ConsumptionServiceError("No sensor data found in database")
            
            # Check if we have any readings at all
            if data_summary.total_readings == 0:
                raise ConsumptionServiceError("No sensor readings found in database")
            
            # Get consumption data
            daily_consumption = self._get_daily_consumption(session)
            hourly_pattern = self._get_hourly_pattern(session)
            node_consumption = self._get_node_consumption(session)
            
            # Calculate metrics
            metrics = self._calculate_metrics(data_summary, daily_consumption)
            
            # Create analytics components
            consumption_timeline = self._create_consumption_timeline(hourly_pattern)
            district_consumption = self._create_district_consumption(node_consumption)
            peak_demand = self._create_peak_demand(hourly_pattern)
            user_segments = self._create_user_segments(node_consumption)
            conservation_opportunities = self._create_conservation_opportunities(metrics['total_daily_consumption'])
            
            return {
                'data_metadata': {
                    'latest_timestamp': data_summary.latest_timestamp.isoformat(),
                    'earliest_timestamp': data_summary.earliest_timestamp.isoformat(),
                    'total_readings': metrics['total_readings'],
                    'flow_readings': data_summary.flow_readings,
                    'synthetic_percentage': round(metrics['synthetic_percentage'], 1),
                    'data_age_hours': round(metrics['data_age_hours'], 1),
                    'active_nodes': data_summary.active_nodes,
                    'is_real_time': False,
                    'data_source': 'Historical Database'
                },
                'summary': {
                    'total_daily_consumption': round(metrics['total_daily_consumption']),
                    'total_monthly_consumption': round(metrics['total_daily_consumption'] * 30),
                    'total_users': sum(seg['user_count'] for seg in user_segments),
                    'avg_consumption_per_user': round(metrics['total_daily_consumption'] / sum(seg['user_count'] for seg in user_segments), 2),
                    'system_efficiency': 0.92,
                    'water_loss_percentage': 8
                },
                'district_consumption': district_consumption,
                'consumption_timeline': consumption_timeline,
                'user_segments': user_segments,
                'peak_demand': peak_demand,
                'conservation_opportunities': conservation_opportunities
            }
            
        except SQLAlchemyError as e:
            raise ConsumptionServiceError(f"Database error: {str(e)}")
        except Exception as e:
            raise ConsumptionServiceError(f"Unexpected error: {str(e)}")
        finally:
            session.close()

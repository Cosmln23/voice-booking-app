from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class StatsPeriod(str, Enum):
    """Statistics period enumeration"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class TrendDirection(str, Enum):
    """Trend direction enumeration"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class ChartType(str, Enum):
    """Chart type enumeration"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DONUT = "donut"


class TrendData(BaseModel):
    """Trend data model"""
    direction: TrendDirection
    percentage: float = Field(..., ge=-100, le=100)
    previous_value: Optional[float] = None


class ChartDataPoint(BaseModel):
    """Chart data point model"""
    label: str
    value: float
    date: Optional[date] = None
    color: Optional[str] = None


class ChartData(BaseModel):
    """Chart data model"""
    type: ChartType
    title: str
    data: List[ChartDataPoint]
    metadata: Optional[Dict[str, Any]] = None


class KPIMetric(BaseModel):
    """Key Performance Indicator model"""
    name: str
    value: float
    unit: str = ""  # e.g., "RON", "%", "appointments"
    trend: Optional[TrendData] = None
    target: Optional[float] = None
    description: Optional[str] = None


class PeriodStats(BaseModel):
    """Period statistics model"""
    period: StatsPeriod
    start_date: date
    end_date: date
    total_appointments: int = 0
    total_revenue: float = 0.0
    completion_rate: float = 0.0
    cancellation_rate: float = 0.0
    no_show_rate: float = 0.0
    average_appointment_value: float = 0.0
    new_clients: int = 0
    returning_clients: int = 0
    
    # Trends compared to previous period
    trends: Dict[str, TrendData] = {}


class ServicePopularity(BaseModel):
    """Service popularity model"""
    service_name: str
    appointment_count: int
    revenue: float
    percentage_of_total: float


class RevenueBreakdown(BaseModel):
    """Revenue breakdown model"""
    individual_services: float = 0.0
    package_deals: float = 0.0
    total: float = 0.0
    currency: str = "RON"


class AppointmentDistribution(BaseModel):
    """Appointment distribution by status"""
    completed: int = 0
    cancelled: int = 0
    no_show: int = 0
    pending: int = 0
    confirmed: int = 0
    in_progress: int = 0


class DashboardStats(BaseModel):
    """Complete dashboard statistics"""
    current_period: PeriodStats
    kpi_metrics: List[KPIMetric] = []
    service_popularity: List[ServicePopularity] = []
    revenue_breakdown: RevenueBreakdown
    appointment_distribution: AppointmentDistribution
    charts: List[ChartData] = []
    last_updated: datetime


class StatsResponse(BaseModel):
    """API response wrapper for statistics"""
    success: bool = True
    data: Optional[DashboardStats] = None
    message: Optional[str] = None


class ChartsResponse(BaseModel):
    """API response wrapper for charts"""
    success: bool = True
    data: List[ChartData] = []
    message: Optional[str] = None
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import random

from app.models.statistics import (
    DashboardStats, PeriodStats, StatsPeriod, TrendDirection, TrendData,
    KPIMetric, ServicePopularity, RevenueBreakdown, AppointmentDistribution,
    ChartData, ChartDataPoint, ChartType, StatsResponse, ChartsResponse
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def generate_trend_data(current_value: float, previous_value: float) -> TrendData:
    """Generate trend data based on current and previous values"""
    if previous_value == 0:
        return TrendData(direction=TrendDirection.STABLE, percentage=0.0, previous_value=previous_value)
    
    percentage = ((current_value - previous_value) / previous_value) * 100
    
    if percentage > 5:
        direction = TrendDirection.UP
    elif percentage < -5:
        direction = TrendDirection.DOWN
    else:
        direction = TrendDirection.STABLE
    
    return TrendData(
        direction=direction,
        percentage=round(percentage, 1),
        previous_value=previous_value
    )


def generate_mock_stats(period: StatsPeriod) -> DashboardStats:
    """Generate mock dashboard statistics"""
    
    # Base values based on period
    if period == StatsPeriod.TODAY:
        appointments = 8
        revenue = 680.0
        completion_rate = 87.5
        cancellation_rate = 12.5
        new_clients = 2
        returning_clients = 6
        prev_appointments = 6
        prev_revenue = 590.0
    elif period == StatsPeriod.WEEK:
        appointments = 45
        revenue = 3850.0
        completion_rate = 89.0
        cancellation_rate = 11.0
        new_clients = 8
        returning_clients = 37
        prev_appointments = 38
        prev_revenue = 3200.0
    elif period == StatsPeriod.MONTH:
        appointments = 185
        revenue = 15750.0
        completion_rate = 91.2
        cancellation_rate = 8.8
        new_clients = 23
        returning_clients = 162
        prev_appointments = 165
        prev_revenue = 14200.0
    else:  # YEAR
        appointments = 2100
        revenue = 178500.0
        completion_rate = 88.5
        cancellation_rate = 11.5
        new_clients = 245
        returning_clients = 1855
        prev_appointments = 1950
        prev_revenue = 165000.0
    
    # Calculate period dates
    today = date.today()
    if period == StatsPeriod.TODAY:
        start_date = end_date = today
    elif period == StatsPeriod.WEEK:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == StatsPeriod.MONTH:
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:  # YEAR
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    # Create period stats
    period_stats = PeriodStats(
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_appointments=appointments,
        total_revenue=revenue,
        completion_rate=completion_rate,
        cancellation_rate=cancellation_rate,
        no_show_rate=100 - completion_rate - cancellation_rate,
        average_appointment_value=revenue / appointments if appointments > 0 else 0,
        new_clients=new_clients,
        returning_clients=returning_clients,
        trends={
            "appointments": generate_trend_data(appointments, prev_appointments),
            "revenue": generate_trend_data(revenue, prev_revenue),
            "completion_rate": generate_trend_data(completion_rate, completion_rate - 2),
            "cancellation_rate": generate_trend_data(cancellation_rate, cancellation_rate + 1.5)
        }
    )
    
    # KPI Metrics
    kpi_metrics = [
        KPIMetric(
            name="Programări Totale",
            value=appointments,
            unit="programări",
            trend=period_stats.trends["appointments"],
            target=appointments * 1.2,
            description="Numărul total de programări"
        ),
        KPIMetric(
            name="Venituri",
            value=revenue,
            unit="RON",
            trend=period_stats.trends["revenue"],
            target=revenue * 1.15,
            description="Venituri totale generate"
        ),
        KPIMetric(
            name="Rata Finalizare",
            value=completion_rate,
            unit="%",
            trend=period_stats.trends["completion_rate"],
            target=95.0,
            description="Procentul programărilor finalizate"
        ),
        KPIMetric(
            name="Rata Anulare",
            value=cancellation_rate,
            unit="%",
            trend=period_stats.trends["cancellation_rate"],
            target=5.0,
            description="Procentul programărilor anulate"
        )
    ]
    
    # Service popularity
    service_popularity = [
        ServicePopularity(
            service_name="Pachet Completă",
            appointment_count=int(appointments * 0.35),
            revenue=revenue * 0.45,
            percentage_of_total=35.0
        ),
        ServicePopularity(
            service_name="Tunsoare Clasică",
            appointment_count=int(appointments * 0.30),
            revenue=revenue * 0.25,
            percentage_of_total=30.0
        ),
        ServicePopularity(
            service_name="Barbă Completă",
            appointment_count=int(appointments * 0.25),
            revenue=revenue * 0.20,
            percentage_of_total=25.0
        ),
        ServicePopularity(
            service_name="Pachet Premium",
            appointment_count=int(appointments * 0.10),
            revenue=revenue * 0.10,
            percentage_of_total=10.0
        )
    ]
    
    # Revenue breakdown
    revenue_breakdown = RevenueBreakdown(
        individual_services=revenue * 0.6,
        package_deals=revenue * 0.4,
        total=revenue,
        currency="RON"
    )
    
    # Appointment distribution
    appointment_distribution = AppointmentDistribution(
        completed=int(appointments * completion_rate / 100),
        cancelled=int(appointments * cancellation_rate / 100),
        no_show=int(appointments * (100 - completion_rate - cancellation_rate) / 100),
        pending=int(appointments * 0.1),
        confirmed=int(appointments * 0.7),
        in_progress=int(appointments * 0.05)
    )
    
    # Generate charts
    charts = generate_mock_charts(period, appointments, revenue)
    
    return DashboardStats(
        current_period=period_stats,
        kpi_metrics=kpi_metrics,
        service_popularity=service_popularity,
        revenue_breakdown=revenue_breakdown,
        appointment_distribution=appointment_distribution,
        charts=charts,
        last_updated=datetime.now()
    )


def generate_mock_charts(period: StatsPeriod, appointments: int, revenue: float) -> List[ChartData]:
    """Generate mock chart data"""
    charts = []
    
    # Appointments per day chart
    if period in [StatsPeriod.WEEK, StatsPeriod.MONTH]:
        days = 7 if period == StatsPeriod.WEEK else 30
        appointment_data = []
        for i in range(days):
            day_appointments = random.randint(3, 12)
            appointment_data.append(ChartDataPoint(
                label=f"Ziua {i+1}",
                value=day_appointments,
                date=date.today() - timedelta(days=days-i-1)
            ))
        
        charts.append(ChartData(
            type=ChartType.LINE,
            title="Programări pe Zile",
            data=appointment_data
        ))
    
    # Monthly revenue chart
    if period == StatsPeriod.YEAR:
        revenue_data = []
        for month in range(1, 13):
            month_revenue = random.randint(12000, 18000)
            revenue_data.append(ChartDataPoint(
                label=f"Luna {month}",
                value=month_revenue
            ))
        
        charts.append(ChartData(
            type=ChartType.BAR,
            title="Venituri Lunare",
            data=revenue_data
        ))
    
    # Service popularity pie chart
    service_data = [
        ChartDataPoint(label="Pachet Completă", value=35, color="#3B82F6"),
        ChartDataPoint(label="Tunsoare Clasică", value=30, color="#EF4444"),
        ChartDataPoint(label="Barbă Completă", value=25, color="#10B981"),
        ChartDataPoint(label="Pachet Premium", value=10, color="#F59E0B"),
    ]
    
    charts.append(ChartData(
        type=ChartType.PIE,
        title="Servicii Populare",
        data=service_data
    ))
    
    return charts


@router.get("/stats", response_model=StatsResponse)
async def get_statistics(
    period: StatsPeriod = Query(StatsPeriod.TODAY, description="Statistics period")
):
    """Get dashboard statistics for specified period"""
    try:
        stats = generate_mock_stats(period)
        
        logger.info(f"Generated statistics for period: {period}",
                   extra={"period": period, "appointments": stats.current_period.total_appointments})
        
        return StatsResponse(
            success=True,
            data=stats,
            message=f"Statistics retrieved for {period.value}"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.get("/stats/charts", response_model=ChartsResponse)
async def get_charts(
    period: StatsPeriod = Query(StatsPeriod.WEEK, description="Charts period")
):
    """Get chart data for specified period"""
    try:
        # Generate mock data for charts
        appointments = 45 if period == StatsPeriod.WEEK else 185
        revenue = 3850.0 if period == StatsPeriod.WEEK else 15750.0
        
        charts = generate_mock_charts(period, appointments, revenue)
        
        logger.info(f"Generated {len(charts)} charts for period: {period}",
                   extra={"period": period, "chart_count": len(charts)})
        
        return ChartsResponse(
            success=True,
            data=charts,
            message=f"Charts retrieved for {period.value}"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve charts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve charts")
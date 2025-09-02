from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models.statistics import (
    DashboardStats, PeriodStats, StatsPeriod, TrendDirection, TrendData,
    KPIMetric, ServicePopularity, RevenueBreakdown, AppointmentDistribution,
    ChartData, ChartDataPoint, ChartType, StatsResponse, ChartsResponse
)
from app.core.logging import get_logger
from app.database.crud_statistics import StatisticsCRUD
from app.database import get_database

router = APIRouter()
logger = get_logger(__name__)


async def get_statistics_crud(db = Depends(get_database)) -> StatisticsCRUD:
    """Dependency injection for StatisticsCRUD"""
    return StatisticsCRUD(db.get_client())








@router.get("/stats", response_model=StatsResponse)
async def get_statistics(
    period: StatsPeriod = Query(StatsPeriod.TODAY, description="Statistics period"),
    statistics_crud: StatisticsCRUD = Depends(get_statistics_crud)
):
    """Get dashboard statistics for specified period"""
    try:
        stats = await statistics_crud.get_dashboard_stats(period)
        
        logger.info(f"Retrieved real statistics for period: {period}",
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
    period: StatsPeriod = Query(StatsPeriod.WEEK, description="Charts period"),
    statistics_crud: StatisticsCRUD = Depends(get_statistics_crud)
):
    """Get chart data for specified period"""
    try:
        charts = await statistics_crud.get_charts_data(period)
        
        logger.info(f"Retrieved {len(charts)} real charts for period: {period}",
                   extra={"period": period, "chart_count": len(charts)})
        
        return ChartsResponse(
            success=True,
            data=charts,
            message=f"Charts retrieved for {period.value}"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve charts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve charts")
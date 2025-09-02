from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from supabase import Client
import calendar

from app.models.statistics import (
    DashboardStats, PeriodStats, StatsPeriod, TrendDirection, TrendData,
    KPIMetric, ServicePopularity, RevenueBreakdown, AppointmentDistribution,
    ChartData, ChartDataPoint, ChartType
)
from app.models.appointment import AppointmentStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class StatisticsCRUD:
    """CRUD operations for statistics - aggregates data from other tables"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_dashboard_stats(self, period: StatsPeriod) -> DashboardStats:
        """Get real dashboard statistics for specified period"""
        try:
            # Calculate period dates
            start_date, end_date = self._calculate_period_dates(period)
            
            # Get current period stats
            current_stats = await self._get_period_stats(period, start_date, end_date)
            
            # Get previous period for trends
            prev_start, prev_end = self._calculate_previous_period_dates(period, start_date)
            previous_stats = await self._get_period_stats(period, prev_start, prev_end)
            
            # Calculate trends
            trends = self._calculate_trends(current_stats, previous_stats)
            current_stats.trends = trends
            
            # Get KPI metrics
            kpi_metrics = self._build_kpi_metrics(current_stats, trends)
            
            # Get service popularity
            service_popularity = await self._get_service_popularity(start_date, end_date)
            
            # Get revenue breakdown
            revenue_breakdown = await self._get_revenue_breakdown(start_date, end_date)
            
            # Get appointment distribution
            appointment_distribution = await self._get_appointment_distribution(start_date, end_date)
            
            # Generate charts
            charts = await self._generate_charts(period, start_date, end_date)
            
            dashboard_stats = DashboardStats(
                current_period=current_stats,
                kpi_metrics=kpi_metrics,
                service_popularity=service_popularity,
                revenue_breakdown=revenue_breakdown,
                appointment_distribution=appointment_distribution,
                charts=charts,
                last_updated=datetime.now()
            )
            
            logger.info(f"Generated real statistics for period: {period}",
                       extra={
                           "period": period,
                           "appointments": current_stats.total_appointments,
                           "revenue": current_stats.total_revenue
                       })
            
            return dashboard_stats
            
        except Exception as e:
            logger.error(f"Failed to generate statistics: {e}", exc_info=True)
            raise
    
    async def get_charts_data(self, period: StatsPeriod) -> List[ChartData]:
        """Get chart data for specified period"""
        try:
            start_date, end_date = self._calculate_period_dates(period)
            charts = await self._generate_charts(period, start_date, end_date)
            
            logger.info(f"Generated {len(charts)} real charts for period: {period}",
                       extra={"period": period, "chart_count": len(charts)})
            
            return charts
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}", exc_info=True)
            raise
    
    async def _get_period_stats(self, period: StatsPeriod, start_date: date, end_date: date) -> PeriodStats:
        """Get statistics for a specific period"""
        try:
            # Get appointments in period
            appointments_response = self.client.table("appointments")\
                .select("*")\
                .gte("appointment_date", start_date.isoformat())\
                .lte("appointment_date", end_date.isoformat())\
                .execute()
            
            appointments = appointments_response.data
            total_appointments = len(appointments)
            
            # Calculate completion, cancellation, no-show rates
            completed = len([a for a in appointments if a["status"] == "completed"])
            cancelled = len([a for a in appointments if a["status"] == "cancelled"])
            no_show = len([a for a in appointments if a["status"] == "no-show"])
            
            completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
            cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
            no_show_rate = (no_show / total_appointments * 100) if total_appointments > 0 else 0
            
            # Calculate revenue from completed appointments with prices
            total_revenue = 0.0
            for appointment in appointments:
                if appointment["status"] == "completed" and appointment.get("price"):
                    # Extract numeric value from price string (e.g., "120 RON" -> 120.0)
                    price_str = appointment["price"]
                    if price_str:
                        try:
                            price_num = float(price_str.split()[0])
                            total_revenue += price_num
                        except (ValueError, IndexError):
                            pass
            
            # Calculate average appointment value
            avg_appointment_value = total_revenue / completed if completed > 0 else 0
            
            # Get client statistics for the period
            new_clients = await self._count_new_clients(start_date, end_date)
            returning_clients = total_appointments - new_clients
            
            return PeriodStats(
                period=period,
                start_date=start_date,
                end_date=end_date,
                total_appointments=total_appointments,
                total_revenue=total_revenue,
                completion_rate=round(completion_rate, 1),
                cancellation_rate=round(cancellation_rate, 1),
                no_show_rate=round(no_show_rate, 1),
                average_appointment_value=round(avg_appointment_value, 2),
                new_clients=new_clients,
                returning_clients=returning_clients,
                trends={}  # Will be filled by caller
            )
            
        except Exception as e:
            logger.error(f"Failed to get period stats: {e}", exc_info=True)
            raise
    
    async def _count_new_clients(self, start_date: date, end_date: date) -> int:
        """Count clients that made their first appointment in the period"""
        try:
            # Get unique phones from appointments in period
            appointments_response = self.client.table("appointments")\
                .select("phone")\
                .gte("appointment_date", start_date.isoformat())\
                .lte("appointment_date", end_date.isoformat())\
                .execute()
            
            phones_in_period = set(a["phone"] for a in appointments_response.data)
            new_clients = 0
            
            # For each phone, check if their first appointment was in this period
            for phone in phones_in_period:
                first_appointment = self.client.table("appointments")\
                    .select("appointment_date")\
                    .eq("phone", phone)\
                    .order("appointment_date", desc=False)\
                    .limit(1)\
                    .execute()
                
                if first_appointment.data:
                    first_date = datetime.strptime(first_appointment.data[0]["appointment_date"], "%Y-%m-%d").date()
                    if start_date <= first_date <= end_date:
                        new_clients += 1
            
            return new_clients
            
        except Exception as e:
            logger.error(f"Failed to count new clients: {e}", exc_info=True)
            return 0
    
    async def _get_service_popularity(self, start_date: date, end_date: date) -> List[ServicePopularity]:
        """Get service popularity statistics"""
        try:
            # Get appointments with services in period
            appointments_response = self.client.table("appointments")\
                .select("service_name, price, status")\
                .gte("appointment_date", start_date.isoformat())\
                .lte("appointment_date", end_date.isoformat())\
                .execute()
            
            appointments = appointments_response.data
            total_appointments = len(appointments)
            
            # Count services and calculate revenue
            service_stats = {}
            total_revenue = 0.0
            
            for appointment in appointments:
                service = appointment["service_name"]
                if service not in service_stats:
                    service_stats[service] = {"count": 0, "revenue": 0.0}
                
                service_stats[service]["count"] += 1
                
                # Add revenue if completed and has price
                if appointment["status"] == "completed" and appointment.get("price"):
                    try:
                        price_num = float(appointment["price"].split()[0])
                        service_stats[service]["revenue"] += price_num
                        total_revenue += price_num
                    except (ValueError, IndexError):
                        pass
            
            # Convert to ServicePopularity objects
            popularity_list = []
            for service, stats in service_stats.items():
                percentage = (stats["count"] / total_appointments * 100) if total_appointments > 0 else 0
                popularity_list.append(ServicePopularity(
                    service_name=service,
                    appointment_count=stats["count"],
                    revenue=stats["revenue"],
                    percentage_of_total=round(percentage, 1)
                ))
            
            # Sort by appointment count
            popularity_list.sort(key=lambda x: x.appointment_count, reverse=True)
            
            return popularity_list[:10]  # Top 10 services
            
        except Exception as e:
            logger.error(f"Failed to get service popularity: {e}", exc_info=True)
            return []
    
    async def _get_revenue_breakdown(self, start_date: date, end_date: date) -> RevenueBreakdown:
        """Get revenue breakdown"""
        try:
            # Get completed appointments with prices
            appointments_response = self.client.table("appointments")\
                .select("price, service_name")\
                .eq("status", "completed")\
                .gte("appointment_date", start_date.isoformat())\
                .lte("appointment_date", end_date.isoformat())\
                .execute()
            
            appointments = appointments_response.data
            total_revenue = 0.0
            package_revenue = 0.0
            
            for appointment in appointments:
                if appointment.get("price"):
                    try:
                        price_num = float(appointment["price"].split()[0])
                        total_revenue += price_num
                        
                        # Consider services with "Pachet" as packages
                        if "pachet" in appointment["service_name"].lower():
                            package_revenue += price_num
                    except (ValueError, IndexError):
                        pass
            
            individual_revenue = total_revenue - package_revenue
            
            return RevenueBreakdown(
                individual_services=round(individual_revenue, 2),
                package_deals=round(package_revenue, 2),
                total=round(total_revenue, 2),
                currency="RON"
            )
            
        except Exception as e:
            logger.error(f"Failed to get revenue breakdown: {e}", exc_info=True)
            return RevenueBreakdown(individual_services=0.0, package_deals=0.0, total=0.0, currency="RON")
    
    async def _get_appointment_distribution(self, start_date: date, end_date: date) -> AppointmentDistribution:
        """Get appointment status distribution"""
        try:
            # Get appointments in period
            appointments_response = self.client.table("appointments")\
                .select("status")\
                .gte("appointment_date", start_date.isoformat())\
                .lte("appointment_date", end_date.isoformat())\
                .execute()
            
            appointments = appointments_response.data
            
            # Count by status
            status_counts = {}
            for appointment in appointments:
                status = appointment["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return AppointmentDistribution(
                completed=status_counts.get("completed", 0),
                cancelled=status_counts.get("cancelled", 0),
                no_show=status_counts.get("no-show", 0),
                pending=status_counts.get("pending", 0),
                confirmed=status_counts.get("confirmed", 0),
                in_progress=status_counts.get("in-progress", 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to get appointment distribution: {e}", exc_info=True)
            return AppointmentDistribution(completed=0, cancelled=0, no_show=0, pending=0, confirmed=0, in_progress=0)
    
    async def _generate_charts(self, period: StatsPeriod, start_date: date, end_date: date) -> List[ChartData]:
        """Generate chart data based on real data"""
        try:
            charts = []
            
            # Appointments per day/week/month chart
            if period in [StatsPeriod.WEEK, StatsPeriod.MONTH]:
                chart_data = await self._get_appointments_timeline_chart(period, start_date, end_date)
                if chart_data:
                    charts.append(chart_data)
            
            # Monthly revenue chart for year period
            if period == StatsPeriod.YEAR:
                chart_data = await self._get_monthly_revenue_chart(start_date, end_date)
                if chart_data:
                    charts.append(chart_data)
            
            # Service popularity pie chart
            service_chart = await self._get_service_popularity_chart(start_date, end_date)
            if service_chart:
                charts.append(service_chart)
            
            return charts
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}", exc_info=True)
            return []
    
    async def _get_appointments_timeline_chart(self, period: StatsPeriod, start_date: date, end_date: date) -> Optional[ChartData]:
        """Generate timeline chart for appointments"""
        try:
            chart_data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Count appointments for this date
                appointments_response = self.client.table("appointments")\
                    .select("id", count="exact")\
                    .eq("appointment_date", current_date.isoformat())\
                    .execute()
                
                count = appointments_response.count or 0
                
                chart_data.append(ChartDataPoint(
                    label=current_date.strftime("%d/%m"),
                    value=count,
                    date=current_date
                ))
                
                current_date += timedelta(days=1)
            
            title = "Programări pe Zile" if period == StatsPeriod.WEEK else "Programări pe Zile (Luna)"
            
            return ChartData(
                type=ChartType.LINE,
                title=title,
                data=chart_data
            )
            
        except Exception as e:
            logger.error(f"Failed to generate timeline chart: {e}", exc_info=True)
            return None
    
    async def _get_monthly_revenue_chart(self, start_date: date, end_date: date) -> Optional[ChartData]:
        """Generate monthly revenue chart for year view"""
        try:
            chart_data = []
            
            for month in range(1, 13):
                month_start = date(start_date.year, month, 1)
                month_end = date(start_date.year, month, calendar.monthrange(start_date.year, month)[1])
                
                # Get completed appointments with prices for this month
                appointments_response = self.client.table("appointments")\
                    .select("price")\
                    .eq("status", "completed")\
                    .gte("appointment_date", month_start.isoformat())\
                    .lte("appointment_date", month_end.isoformat())\
                    .execute()
                
                month_revenue = 0.0
                for appointment in appointments_response.data:
                    if appointment.get("price"):
                        try:
                            price_num = float(appointment["price"].split()[0])
                            month_revenue += price_num
                        except (ValueError, IndexError):
                            pass
                
                chart_data.append(ChartDataPoint(
                    label=calendar.month_name[month][:3],  # Jan, Feb, etc.
                    value=round(month_revenue, 2)
                ))
            
            return ChartData(
                type=ChartType.BAR,
                title="Venituri Lunare",
                data=chart_data
            )
            
        except Exception as e:
            logger.error(f"Failed to generate monthly revenue chart: {e}", exc_info=True)
            return None
    
    async def _get_service_popularity_chart(self, start_date: date, end_date: date) -> Optional[ChartData]:
        """Generate service popularity pie chart"""
        try:
            service_popularity = await self._get_service_popularity(start_date, end_date)
            
            chart_data = []
            colors = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4"]
            
            for i, service in enumerate(service_popularity[:6]):  # Top 6 services
                chart_data.append(ChartDataPoint(
                    label=service.service_name,
                    value=service.percentage_of_total,
                    color=colors[i % len(colors)]
                ))
            
            return ChartData(
                type=ChartType.PIE,
                title="Servicii Populare",
                data=chart_data
            )
            
        except Exception as e:
            logger.error(f"Failed to generate service popularity chart: {e}", exc_info=True)
            return None
    
    def _calculate_period_dates(self, period: StatsPeriod) -> tuple[date, date]:
        """Calculate start and end dates for period"""
        today = date.today()
        
        if period == StatsPeriod.TODAY:
            return today, today
        elif period == StatsPeriod.WEEK:
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            return start_date, end_date
        elif period == StatsPeriod.MONTH:
            start_date = today.replace(day=1)
            end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
            return start_date, end_date
        else:  # YEAR
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            return start_date, end_date
    
    def _calculate_previous_period_dates(self, period: StatsPeriod, start_date: date) -> tuple[date, date]:
        """Calculate previous period dates for trend comparison"""
        if period == StatsPeriod.TODAY:
            prev_start = start_date - timedelta(days=1)
            return prev_start, prev_start
        elif period == StatsPeriod.WEEK:
            prev_start = start_date - timedelta(weeks=1)
            prev_end = prev_start + timedelta(days=6)
            return prev_start, prev_end
        elif period == StatsPeriod.MONTH:
            if start_date.month == 1:
                prev_start = date(start_date.year - 1, 12, 1)
                prev_end = date(start_date.year - 1, 12, 31)
            else:
                prev_start = date(start_date.year, start_date.month - 1, 1)
                prev_end = date(start_date.year, start_date.month - 1, 
                              calendar.monthrange(start_date.year, start_date.month - 1)[1])
            return prev_start, prev_end
        else:  # YEAR
            prev_start = date(start_date.year - 1, 1, 1)
            prev_end = date(start_date.year - 1, 12, 31)
            return prev_start, prev_end
    
    def _calculate_trends(self, current: PeriodStats, previous: PeriodStats) -> Dict[str, TrendData]:
        """Calculate trends comparing current vs previous period"""
        trends = {}
        
        # Appointments trend
        trends["appointments"] = self._generate_trend_data(
            current.total_appointments, previous.total_appointments
        )
        
        # Revenue trend  
        trends["revenue"] = self._generate_trend_data(
            current.total_revenue, previous.total_revenue
        )
        
        # Completion rate trend
        trends["completion_rate"] = self._generate_trend_data(
            current.completion_rate, previous.completion_rate
        )
        
        # Cancellation rate trend
        trends["cancellation_rate"] = self._generate_trend_data(
            current.cancellation_rate, previous.cancellation_rate
        )
        
        return trends
    
    def _generate_trend_data(self, current_value: float, previous_value: float) -> TrendData:
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
    
    def _build_kpi_metrics(self, current_stats: PeriodStats, trends: Dict[str, TrendData]) -> List[KPIMetric]:
        """Build KPI metrics from current stats and trends"""
        return [
            KPIMetric(
                name="Programări Totale",
                value=current_stats.total_appointments,
                unit="programări",
                trend=trends["appointments"],
                target=current_stats.total_appointments * 1.2,
                description="Numărul total de programări"
            ),
            KPIMetric(
                name="Venituri",
                value=current_stats.total_revenue,
                unit="RON",
                trend=trends["revenue"],
                target=current_stats.total_revenue * 1.15,
                description="Venituri totale generate"
            ),
            KPIMetric(
                name="Rata Finalizare",
                value=current_stats.completion_rate,
                unit="%",
                trend=trends["completion_rate"],
                target=95.0,
                description="Procentul programărilor finalizate"
            ),
            KPIMetric(
                name="Rata Anulare",
                value=current_stats.cancellation_rate,
                unit="%",
                trend=trends["cancellation_rate"],
                target=5.0,
                description="Procentul programărilor anulate"
            )
        ]
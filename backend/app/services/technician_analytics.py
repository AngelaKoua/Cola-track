"""
Service for technician analytics and statistics.

This service provides functions to query technician activity data from the data warehouse,
including KPIs, activity statistics, and detailed analytics for visualization.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class TechnicianAnalyticsService:
    """Service for technician-related analytics queries."""
    
    @staticmethod
    def get_summary_stats(db: Session, period_days: int = 30) -> Dict[str, Any]:
        """
        Get summary KPIs for all technicians.
        
        Args:
            db: Database session
            period_days: Number of days to look back (default: 30)
        
        Returns:
            Dictionary with KPIs: total, active, inactive, total_entries
        """
        # Count total technicians
        total_query = text("SELECT COUNT(*) FROM users WHERE role = 'technician'")
        total = db.execute(total_query).scalar() or 0
        
        # Count active technicians
        active_query = text("SELECT COUNT(*) FROM users WHERE role = 'technician' AND is_active = true")
        active = db.execute(active_query).scalar() or 0
        
        # Count inactive technicians
        inactive = total - active
        
        # Count total entries in the period
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        total_entries_query = text("""
            SELECT COUNT(*) as total FROM (
                SELECT fact_id FROM dw.fact_osmoseur_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE t.full_timestamp >= :cutoff
                UNION ALL
                SELECT fact_id FROM dw.fact_remplisseuse_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE t.full_timestamp >= :cutoff
            ) combined
        """)
        total_entries = db.execute(total_entries_query, {"cutoff": cutoff_date}).scalar() or 0
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "total_entries": total_entries,
            "period_days": period_days
        }
    
    @staticmethod
    def get_technicians_list(db: Session, period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Get list of all technicians with their activity statistics.
        
        Args:
            db: Database session
            period_days: Number of days to look back (default: 30)
        
        Returns:
            List of dictionaries with technician data and statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        query = text("""
            SELECT 
                u.id,
                u.username,
                u.is_active,
                u.created_at,
                dt.technician_id,
                dt.original_name,
                
                -- Count entries from osmoseur
                COALESCE(osmo.entry_count, 0) as osmo_count,
                COALESCE(osmo.last_entry, NULL) as osmo_last,
                
                -- Count entries from remplisseuse
                COALESCE(remp.entry_count, 0) as remp_count,
                COALESCE(remp.last_entry, NULL) as remp_last
                
            FROM users u
            LEFT JOIN dw.dim_technician dt ON dt.original_name = u.username
            
            -- Osmoseur stats
            LEFT JOIN (
                SELECT 
                    f.technician_id,
                    COUNT(*) as entry_count,
                    MAX(t.full_timestamp) as last_entry
                FROM dw.fact_osmoseur_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE t.full_timestamp >= :cutoff
                GROUP BY f.technician_id
            ) osmo ON osmo.technician_id = dt.technician_id
            
            -- Remplisseuse stats
            LEFT JOIN (
                SELECT 
                    f.technician_id,
                    COUNT(*) as entry_count,
                    MAX(t.full_timestamp) as last_entry
                FROM dw.fact_remplisseuse_hourly f
                JOIN dw.dim_time t ON f.time_id = t.time_id
                WHERE t.full_timestamp >= :cutoff
                GROUP BY f.technician_id
            ) remp ON remp.technician_id = dt.technician_id
            
            WHERE u.role = 'technician'
            ORDER BY u.username
        """)
        
        results = db.execute(query, {"cutoff": cutoff_date}).fetchall()
        
        technicians = []
        for row in results:
            total_entries = row.osmo_count + row.remp_count
            
            # Determine last entry
            last_entry = None
            if row.osmo_last and row.remp_last:
                last_entry = max(row.osmo_last, row.remp_last)
            elif row.osmo_last:
                last_entry = row.osmo_last
            elif row.remp_last:
                last_entry = row.remp_last
            
            # Determine equipment type
            if row.osmo_count > 0 and row.remp_count > 0:
                equipment_type = "Mixte"
            elif row.osmo_count > 0:
                equipment_type = "Osmoseur"
            elif row.remp_count > 0:
                equipment_type = "Remplisseuse"
            else:
                equipment_type = "Aucun"
            
            technicians.append({
                "id": row.id,
                "username": row.username,
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "total_entries": total_entries,
                "last_entry": last_entry.isoformat() if last_entry else None,
                "equipment_type": equipment_type,
                "osmo_entries": row.osmo_count,
                "remp_entries": row.remp_count
            })
        
        return technicians
    
    @staticmethod
    def get_technician_detail(
        db: Session, 
        technician_id: int, 
        period_days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a specific technician.
        
        Args:
            db: Database session
            technician_id: User ID of the technician
            period_days: Number of days to look back (default: 30)
        
        Returns:
            Dictionary with detailed technician data including charts data
        """
        # Get basic user info
        user_query = text("""
            SELECT id, username, is_active, created_at, updated_at
            FROM users 
            WHERE id = :tech_id AND role = 'technician'
        """)
        user = db.execute(user_query, {"tech_id": technician_id}).fetchone()
        
        if not user:
            return None
        
        # Get dim_technician_id
        dim_tech_query = text("""
            SELECT technician_id FROM dw.dim_technician 
            WHERE original_name = :username
        """)
        dim_tech = db.execute(dim_tech_query, {"username": user.username}).fetchone()
        
        if not dim_tech:
            # Technician exists but has no data warehouse entries yet
            return {
                "id": user.id,
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_activity": None,
                "entries_by_day": [],
                "entries_by_equipment": {"Osmoseur": 0, "Remplisseuse": 0},
                "entries_by_hour": [0] * 24
            }
        
        dim_tech_id = dim_tech.technician_id
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        
        # Get entries by day
        entries_by_day_query = text("""
            SELECT 
                t.year, t.month, t.day,
                COUNT(*) as entry_count
            FROM (
                SELECT time_id FROM dw.fact_osmoseur_hourly WHERE technician_id = :tech_id
                UNION ALL
                SELECT time_id FROM dw.fact_remplisseuse_hourly WHERE technician_id = :tech_id
            ) f
            JOIN dw.dim_time t ON f.time_id = t.time_id
            WHERE t.full_timestamp >= :cutoff
            GROUP BY t.year, t.month, t.day
            ORDER BY t.year, t.month, t.day
        """)
        entries_by_day = db.execute(
            entries_by_day_query, 
            {"tech_id": dim_tech_id, "cutoff": cutoff_date}
        ).fetchall()
        
        # Get entries by equipment type
        osmo_count_query = text("""
            SELECT COUNT(*) FROM dw.fact_osmoseur_hourly f
            JOIN dw.dim_time t ON f.time_id = t.time_id
            WHERE f.technician_id = :tech_id AND t.full_timestamp >= :cutoff
        """)
        osmo_count = db.execute(
            osmo_count_query, 
            {"tech_id": dim_tech_id, "cutoff": cutoff_date}
        ).scalar() or 0
        
        remp_count_query = text("""
            SELECT COUNT(*) FROM dw.fact_remplisseuse_hourly f
            JOIN dw.dim_time t ON f.time_id = t.time_id
            WHERE f.technician_id = :tech_id AND t.full_timestamp >= :cutoff
        """)
        remp_count = db.execute(
            remp_count_query, 
            {"tech_id": dim_tech_id, "cutoff": cutoff_date}
        ).scalar() or 0
        
        # Get entries by hour
        entries_by_hour_query = text("""
            SELECT 
                t.hour,
                COUNT(*) as entry_count
            FROM (
                SELECT time_id FROM dw.fact_osmoseur_hourly WHERE technician_id = :tech_id
                UNION ALL
                SELECT time_id FROM dw.fact_remplisseuse_hourly WHERE technician_id = :tech_id
            ) f
            JOIN dw.dim_time t ON f.time_id = t.time_id
            WHERE t.full_timestamp >= :cutoff
            GROUP BY t.hour
            ORDER BY t.hour
        """)
        entries_by_hour = db.execute(
            entries_by_hour_query, 
            {"tech_id": dim_tech_id, "cutoff": cutoff_date}
        ).fetchall()
        
        # Format entries_by_hour to array (0-23 hours)
        hour_counts = [0] * 24
        for row in entries_by_hour:
            hour_counts[row.hour] = row.entry_count
        
        # Get last activity
        last_activity_query = text("""
            SELECT MAX(t.full_timestamp) as last_activity
            FROM (
                SELECT time_id FROM dw.fact_osmoseur_hourly WHERE technician_id = :tech_id
                UNION ALL
                SELECT time_id FROM dw.fact_remplisseuse_hourly WHERE technician_id = :tech_id
            ) f
            JOIN dw.dim_time t ON f.time_id = t.time_id
        """)
        last_activity = db.execute(
            last_activity_query, 
            {"tech_id": dim_tech_id}
        ).scalar()
        
        return {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "entries_by_day": [
                {
                    "date": f"{row.year}-{row.month:02d}-{row.day:02d}",
                    "count": row.entry_count
                }
                for row in entries_by_day
            ],
            "entries_by_equipment": {
                "Osmoseur": osmo_count,
                "Remplisseuse": remp_count
            },
            "entries_by_hour": hour_counts
        }

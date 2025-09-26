import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and reporting operations"""
    
    def get_specialty_experience_data(self, db: Session) -> Dict[str, Any]:
        """Get specialty experience data for box plot visualization"""
        try:
            # Query to get experience distribution by specialty
            query = text("""
                SELECT 
                    primary_specialty,
                    years_in_practice,
                    COUNT(*) as provider_count
                FROM merged_roster 
                WHERE primary_specialty IS NOT NULL 
                AND years_in_practice IS NOT NULL 
                AND years_in_practice >= 0 
                AND years_in_practice <= 60
                GROUP BY primary_specialty, years_in_practice
                ORDER BY primary_specialty, years_in_practice
            """)
            
            result = db.execute(query)
            rows = result.fetchall()
            
            # Group data by specialty
            specialty_data = {}
            for row in rows:
                specialty, years, count = row[0], row[1], row[2]
                if specialty not in specialty_data:
                    specialty_data[specialty] = []
                
                # Add individual years based on provider count
                for _ in range(count):
                    specialty_data[specialty].append(years)
            
            # Calculate statistics for each specialty
            specialty_stats = []
            for specialty, experience_data in specialty_data.items():
                if len(experience_data) > 0:
                    experience_data.sort()
                    stats = {
                        'specialty': specialty,
                        'count': len(experience_data),
                        'min': min(experience_data),
                        'max': max(experience_data),
                        'q1': experience_data[len(experience_data) // 4] if len(experience_data) >= 4 else min(experience_data),
                        'median': experience_data[len(experience_data) // 2],
                        'q3': experience_data[3 * len(experience_data) // 4] if len(experience_data) >= 4 else max(experience_data),
                        'mean': sum(experience_data) / len(experience_data),
                        'experience_data': experience_data[:100]  # Limit data points for frontend processing
                    }
                    specialty_stats.append(stats)
            
            # Sort by provider count and take top 15
            specialty_stats.sort(key=lambda x: x['count'], reverse=True)
            top_specialties = specialty_stats[:15]
            
            # Get overall statistics
            all_experience_data = []
            for specialty_info in top_specialties:
                all_experience_data.extend(specialty_info['experience_data'])
            
            overall_stats = {
                'total_providers': len(all_experience_data),
                'specialties_count': len(top_specialties),
                'overall_mean': sum(all_experience_data) / len(all_experience_data) if all_experience_data else 0,
                'overall_min': min(all_experience_data) if all_experience_data else 0,
                'overall_max': max(all_experience_data) if all_experience_data else 0
            }
            
            return {
                'specialty_stats': top_specialties,
                'overall_stats': overall_stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error fetching specialty experience data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching specialty experience data: {str(e)}")
    
    def get_providers_by_specialty(self, db: Session) -> Dict[str, Any]:
        """Get provider categorization data by specialty for pie chart visualization"""
        try:
            # Query to get provider count by specialty
            query = text("""
                SELECT 
                    primary_specialty,
                    COUNT(*) as provider_count,
                    COUNT(CASE WHEN license_expiration IS NOT NULL AND license_expiration != '' 
                              AND STR_TO_DATE(license_expiration, '%Y-%m-%d') < CURDATE() THEN 1 END) as expired_licenses,
                    COUNT(CASE WHEN npi IS NULL OR npi = 0 THEN 1 END) as missing_npi,
                    COUNT(CASE WHEN practice_phone IS NULL OR practice_phone = '' OR 
                              LENGTH(TRIM(practice_phone)) < 10 THEN 1 END) as phone_issues,
                    COUNT(CASE WHEN practice_address_line1 IS NULL OR practice_address_line1 = '' THEN 1 END) as address_issues
                FROM merged_roster 
                WHERE primary_specialty IS NOT NULL AND primary_specialty != ''
                GROUP BY primary_specialty
                ORDER BY provider_count DESC
                LIMIT 20
            """)
            
            result = db.execute(query)
            rows = result.fetchall()
            
            specialty_data = []
            total_providers = 0
            total_issues = 0
            
            for row in rows:
                specialty = row[0]
                count = row[1]
                expired_licenses = row[2]
                missing_npi = row[3]
                phone_issues = row[4]
                address_issues = row[5]
                
                # Calculate total issues for this specialty
                issues_count = expired_licenses + missing_npi + phone_issues + address_issues
                
                specialty_info = {
                    'name': specialty,
                    'value': count,
                    'issues': issues_count,
                    'expired_licenses': expired_licenses,
                    'missing_npi': missing_npi,
                    'phone_issues': phone_issues,
                    'address_issues': address_issues,
                    'percentage': 0  # Will be calculated after we have total
                }
                
                specialty_data.append(specialty_info)
                total_providers += count
                total_issues += issues_count
            
            # Calculate percentages
            for specialty in specialty_data:
                specialty['percentage'] = round((specialty['value'] / total_providers) * 100, 1) if total_providers > 0 else 0
            
            # Get overall statistics
            overall_stats = {
                'total_providers': total_providers,
                'total_specialties': len(specialty_data),
                'total_issues': total_issues,
                'avg_issues_per_specialty': round(total_issues / len(specialty_data), 1) if specialty_data else 0
            }
            
            return {
                'specialty_data': specialty_data,
                'overall_stats': overall_stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error fetching providers by specialty data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching providers by specialty data: {str(e)}")
    
    def get_providers_by_state(self, db: Session) -> Dict[str, Any]:
        """Get provider distribution data by state for bar chart visualization"""
        try:
            # Query to get provider count by state from both practice and license states
            query = text("""
                SELECT 
                    COALESCE(practice_state, license_state, 'Unknown') as state,
                    COUNT(*) as provider_count
                FROM merged_roster 
                WHERE (practice_state IS NOT NULL AND practice_state != '') 
                   OR (license_state IS NOT NULL AND license_state != '')
                GROUP BY COALESCE(practice_state, license_state, 'Unknown')
                HAVING provider_count > 0
                ORDER BY provider_count DESC
                LIMIT 15
            """)
            
            result = db.execute(query)
            rows = result.fetchall()
            
            state_data = []
            total_providers = 0
            
            for row in rows:
                state = row[0] if row[0] and row[0] != 'Unknown' else 'Unknown'
                count = row[1]
                
                state_info = {
                    'state': state,
                    'providers': count,
                    'percentage': 0  # Will be calculated after we have total
                }
                
                state_data.append(state_info)
                total_providers += count
            
            # Calculate percentages
            for state in state_data:
                state['percentage'] = round((state['providers'] / total_providers) * 100, 1) if total_providers > 0 else 0
            
            # Get top states summary
            top_3_states = state_data[:3]
            top_3_count = sum(state['providers'] for state in top_3_states)
            top_3_percentage = round((top_3_count / total_providers) * 100, 1) if total_providers > 0 else 0
            
            overall_stats = {
                'total_providers': total_providers,
                'total_states': len(state_data),
                'top_3_states': [state['state'] for state in top_3_states],
                'top_3_count': top_3_count,
                'top_3_percentage': top_3_percentage
            }
            
            return {
                'state_data': state_data,
                'overall_stats': overall_stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error fetching providers by state data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching providers by state data: {str(e)}")


# Global analytics service instance
analytics_service = AnalyticsService()

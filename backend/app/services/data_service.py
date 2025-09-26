import pandas as pd
import io
import os
import sys
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, UploadFile
from typing import List, Tuple, Dict, Any
from ..models.schemas import Provider, Duplicate, ClusterInfo
from ..config.settings import settings

# Add the parent directory to the path to import pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from pipeline import preprocessing

logger = logging.getLogger(__name__)


class DataService:
    """Service for data processing and database operations"""
    
    async def process_csv_file(self, file: UploadFile, db: Session) -> Dict[str, Any]:
        """Process uploaded CSV file using preprocessing function"""
        try:
            # Read uploaded file into pandas DataFrame
            contents = await file.read()
            
            try:
                df = pd.read_csv(io.BytesIO(contents))
                logger.info("File read successfully using BytesIO")
            except Exception:
                # fallback if file contents are text or encoding causes BytesIO read issues
                df = pd.read_csv(io.StringIO(contents.decode()))
                logger.info("File read successfully using StringIO")
            
            # Use data/ as base path for merge_roster
            base_path = settings.data_path
            
            # If environment variable not set, try relative path
            if base_path == "/app/data" and not os.path.exists(base_path):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                base_path = os.path.join(current_dir, "..", "..", "data")
                base_path = os.path.abspath(base_path)
            
            # Ensure directory exists
            os.makedirs(base_path, exist_ok=True)
            
            logger.info(f"Base path resolved to: {base_path}")
            logger.info(f"Base path exists: {os.path.exists(base_path)}")
            
            dup_df, clusters, summary, merged_df = preprocessing(df, base_path)

            # Save tables to database using the session
            try:
                # Save duplicates
                if not dup_df.empty:
                    dup_df.to_sql("duplicates", con=db.bind, if_exists="replace", index=False)
                
                # Save merged_df
                if not merged_df.empty:
                    merged_df.to_sql("merged_roster", con=db.bind, if_exists="replace", index=False)
                
                # Commit the transaction
                db.commit()
                
            except Exception as db_error:
                db.rollback()
                logger.error(f"Database save error: {str(db_error)}")
                raise HTTPException(status_code=500, detail=f"Database save error: {str(db_error)}")
                
            # Convert results to JSON serializable
            result = {
                "clusters": clusters,
                "summary": summary,
            }
            return result
            
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
    def get_providers_paginated(self, db: Session, page: int = 1, limit: int = 20) -> Tuple[List[Provider], int, int]:
        """Get paginated list of providers"""
        try:
            # Calculate offset
            offset = (page - 1) * limit
            
            # Get total count
            count_query = text("SELECT COUNT(*) FROM merged_roster")
            total_result = db.execute(count_query)
            total = total_result.scalar()
            
            # Get providers with pagination
            query = text("""
                SELECT 
                    provider_id,
                    npi,
                    full_name,
                    primary_specialty,
                    license_number,
                    license_state
                FROM merged_roster 
                ORDER BY provider_id
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.execute(query, {"limit": limit, "offset": offset})
            rows = result.fetchall()
            
            # Convert to Provider objects
            providers = []
            for row in rows:
                provider = Provider(
                    provider_id=row[0],
                    npi=row[1],
                    full_name=row[2],
                    primary_specialty=row[3],
                    license_number=row[4],
                    license_state=row[5]
                )
                providers.append(provider)
            
            # Calculate total pages
            total_pages = (total + limit - 1) // limit
            
            return providers, total, total_pages
            
        except Exception as e:
            logger.error(f"Error fetching providers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")
    
    def get_duplicate_clusters(self, db: Session) -> Tuple[List[ClusterInfo], int, int]:
        """Get duplicate clusters with provider information"""
        try:
            # Get all duplicates from the database
            duplicates_query = text("""
                SELECT 
                    i1, i2, provider_id_1, provider_id_2, name_1, name_2,
                    score, name_score, npi_match, addr_score, phone_match, license_score
                FROM duplicates
                ORDER BY score DESC
            """)
            
            duplicates_result = db.execute(duplicates_query)
            duplicates_rows = duplicates_result.fetchall()
            
            # Build clusters from duplicates
            clusters_map = {}
            processed_pairs = set()
            
            for row in duplicates_rows:
                i1, i2 = row[0], row[1]
                if (i1, i2) in processed_pairs or (i2, i1) in processed_pairs:
                    continue
                    
                processed_pairs.add((i1, i2))
                
                # Find existing cluster or create new one
                cluster_id = None
                for cid, cluster_data in clusters_map.items():
                    if i1 in cluster_data['members'] or i2 in cluster_data['members']:
                        cluster_id = cid
                        break
                
                if cluster_id is None:
                    cluster_id = f"cluster_{min(i1, i2)}"
                    clusters_map[cluster_id] = {
                        'members': set(),
                        'representative': min(i1, i2),
                        'duplicates': []
                    }
                
                clusters_map[cluster_id]['members'].add(i1)
                clusters_map[cluster_id]['members'].add(i2)
                
                duplicate = Duplicate(
                    i1=row[0], i2=row[1], provider_id_1=row[2], provider_id_2=row[3],
                    name_1=row[4], name_2=row[5], score=row[6], name_score=row[7],
                    npi_match=bool(row[8]) if row[8] is not None else None,
                    addr_score=row[9], phone_match=bool(row[10]) if row[10] is not None else None,
                    license_score=row[11]
                )
                clusters_map[cluster_id]['duplicates'].append(duplicate)
            
            # Get provider details for each cluster
            cluster_infos = []
            for cluster_id, cluster_data in clusters_map.items():
                member_ids = list(cluster_data['members'])
                
                # Get provider details for cluster members
                if member_ids:
                    cluster_providers = []
                    
                    for member_id in member_ids:
                        provider_query = text("""
                            SELECT 
                                provider_id, npi, full_name, primary_specialty, license_number, license_state
                            FROM merged_roster 
                            ORDER BY provider_id
                            LIMIT 1 OFFSET :offset
                        """)
                        
                        try:
                            provider_result = db.execute(provider_query, {"offset": member_id})
                            provider_row = provider_result.fetchone()
                            
                            if provider_row:
                                provider = Provider(
                                    provider_id=provider_row[0],
                                    npi=provider_row[1], 
                                    full_name=provider_row[2],
                                    primary_specialty=provider_row[3], 
                                    license_number=provider_row[4], 
                                    license_state=provider_row[5]
                                )
                                cluster_providers.append(provider)
                        except Exception as e:
                            logger.warning(f"Could not fetch provider at index {member_id}: {str(e)}")
                            continue
                    
                    if cluster_providers:  # Only create cluster if we found providers
                        cluster_info = ClusterInfo(
                            cluster_id=cluster_id,
                            members=member_ids,
                            representative=cluster_data['representative'],
                            providers=cluster_providers,
                            duplicates=cluster_data['duplicates']
                        )
                        cluster_infos.append(cluster_info)
            
            return cluster_infos, len(cluster_infos), len(duplicates_rows)
            
        except Exception as e:
            logger.error(f"Error fetching duplicates: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching duplicates: {str(e)}")


# Global data service instance
data_service = DataService()

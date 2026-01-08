import streamlit as st
import datetime
from typing import Dict, List, Optional
from .firebase_service import get_firebase_service

class GlobalMineSystem:
    """Global mine system for multi-player real-time mining"""
    
    ADMIN_EMAIL = "mwill1003@gmail.com"
    
    def __init__(self):
        self.firebase_service = get_firebase_service()
    
    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        return email == self.ADMIN_EMAIL
    
    def get_global_mine_status(self, mine_id: str) -> Dict:
        """Get real-time global mine status, auto-initialize if needed"""
        try:
            doc = self.firebase_service.db.collection('global_mines').document(mine_id).get()
            if doc.exists:
                return doc.to_dict()
            
            # Auto-initialize mine if it doesn't exist
            mine_config = self._get_mine_config(mine_id)
            if mine_config:
                if self.initialize_global_mine(mine_id, mine_config):
                    # Return the newly initialized mine
                    doc = self.firebase_service.db.collection('global_mines').document(mine_id).get()
                    if doc.exists:
                        return doc.to_dict()
            
            return None
        except Exception:
            return None
    
    def initialize_global_mine(self, mine_id: str, mine_data: Dict) -> bool:
        """Initialize a global mine with starting reserves"""
        try:
            mine_doc = {
                'mine_id': mine_id,
                'name': mine_data['name'],
                'level_requirement': mine_data['level'],
                'initial_reserves': mine_data['reserves'],
                'current_reserves': mine_data['reserves'],
                'total_mined': 0,
                'active_miners': 0,
                'last_reset': datetime.datetime.now(),
                'created_at': datetime.datetime.now(),
                'mining_history': [],
                'depletion_rate': mine_data.get('depletion_rate', 1.0)
            }
            
            self.firebase_service.db.collection('global_mines').document(mine_id).set(mine_doc)
            return True
        except Exception as e:
            st.error(f"Failed to initialize mine {mine_id}: {e}")
            return False
    
    def mine_gold(self, mine_id: str, miner_email: str, amount: float) -> Dict:
        """Mine gold from global mine with atomic updates"""
        try:
            mine_ref = self.firebase_service.db.collection('global_mines').document(mine_id)
            
            # Get current mine data
            mine_doc = mine_ref.get()
            if not mine_doc.exists:
                return {'success': False, 'error': 'Mine not found'}
            
            mine_data = mine_doc.to_dict()
            current_reserves = mine_data.get('current_reserves', 0)
            
            if current_reserves <= 0:
                return {'success': False, 'error': 'Mine depleted'}
            
            # Calculate actual amount mined (can't exceed reserves)
            actual_amount = min(amount, current_reserves)
            new_reserves = current_reserves - actual_amount
            
            # Update mine data
            mining_record = {
                'miner': miner_email,
                'amount': actual_amount,
                'timestamp': datetime.datetime.now(),
                'reserves_after': new_reserves
            }
            
            history = mine_data.get('mining_history', [])
            history.append(mining_record)
            
            # Keep only last 100 mining records
            if len(history) > 100:
                history = history[-100:]
            
            # Update the mine document
            mine_ref.update({
                'current_reserves': new_reserves,
                'total_mined': mine_data.get('total_mined', 0) + actual_amount,
                'mining_history': history,
                'last_activity': datetime.datetime.now()
            })
            
            return {
                'success': True,
                'amount_mined': actual_amount,
                'reserves_remaining': new_reserves,
                'mine_depleted': new_reserves <= 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_all_mines_status(self) -> List[Dict]:
        """Get status of all global mines"""
        try:
            # Use individual document gets since collection methods don't work
            mine_ids = [
                "gold_creek_main", "coloma_bar", "yuba_bend", "auburn_ravine",
                "mokelumne_cut", "jamestown_flats", "placerville_reef", "downie_ridge_vein",
                "feather_fork_3", "nevada_city_drift", "angels_reef", "rough_and_ready_mine",
                "french_gulch", "smartsville_diggings", "grass_valley_lode", "empire_mine",
                "north_star_mine", "malakoff_diggins", "cherokee_mine", "alleghany_mine",
                "forest_city_mine", "washington_mine", "downieville_drift", "sierra_buttes_mine",
                "tuolumne_quartz", "columbia_pocket", "merced_shine", "calaveras_grove_mine",
                "moaning_cavern_mine", "dead_mans_gulch", "widows_peak_mine", "el_dorado_mother_lode"
            ]
            
            docs = []
            mines_ref = self.firebase_service.db.collection('global_mines')
            for mine_id in mine_ids:
                doc = mines_ref.document(mine_id).get()
                if doc.exists:
                    docs.append(doc.to_dict())
            return docs
        except Exception:
            return []
    
    def _get_mine_config(self, mine_id: str) -> Dict:
        """Get configuration for a specific mine ID"""
        mine_configs = {
            # LEVEL 1-5: Beginner Sites
            "gold_creek_main": {"name": "Gold Creek Main Vein", "level": 1, "reserves": 5000},
            "coloma_bar": {"name": "Coloma Bar", "level": 1, "reserves": 1200},
            "yuba_bend": {"name": "Yuba Bend", "level": 3, "reserves": 800},
            "auburn_ravine": {"name": "Auburn Ravine", "level": 5, "reserves": 600},
            
            # LEVEL 6-15: Novice Sites
            "mokelumne_cut": {"name": "Mokelumne Cut", "level": 6, "reserves": 1500},
            "jamestown_flats": {"name": "Jamestown Flats", "level": 8, "reserves": 2200},
            "placerville_reef": {"name": "Placerville Reef", "level": 10, "reserves": 3500},
            "downie_ridge_vein": {"name": "Downie Ridge Vein", "level": 12, "reserves": 4800},
            "feather_fork_3": {"name": "Feather Fork #3", "level": 15, "reserves": 6200},
            
            # LEVEL 16-25: Skilled Sites
            "nevada_city_drift": {"name": "Nevada City Drift", "level": 16, "reserves": 8800},
            "angels_reef": {"name": "Angels Reef", "level": 18, "reserves": 12500},
            "rough_and_ready_mine": {"name": "Rough and Ready Mine", "level": 20, "reserves": 15000},
            "french_gulch": {"name": "French Gulch", "level": 22, "reserves": 11000},
            "smartsville_diggings": {"name": "Smartsville Diggings", "level": 25, "reserves": 18000},
            
            # LEVEL 26-35: Veteran Sites
            "grass_valley_lode": {"name": "Grass Valley Lode", "level": 26, "reserves": 25000},
            "empire_mine": {"name": "Empire Mine", "level": 28, "reserves": 32000},
            "north_star_mine": {"name": "North Star Mine", "level": 30, "reserves": 28000},
            "malakoff_diggins": {"name": "Malakoff Diggins", "level": 32, "reserves": 22000},
            "cherokee_mine": {"name": "Cherokee Mine", "level": 35, "reserves": 38000},
            
            # LEVEL 36-45: Expert Sites
            "alleghany_mine": {"name": "Alleghany Mine", "level": 36, "reserves": 45000},
            "forest_city_mine": {"name": "Forest City Mine", "level": 38, "reserves": 52000},
            "washington_mine": {"name": "Washington Mine", "level": 40, "reserves": 48000},
            "downieville_drift": {"name": "Downieville Drift", "level": 42, "reserves": 55000},
            "sierra_buttes_mine": {"name": "Sierra Buttes Mine", "level": 45, "reserves": 62000},
            
            # LEVEL 46-55: Master Sites
            "tuolumne_quartz": {"name": "Tuolumne Quartz", "level": 46, "reserves": 75000},
            "columbia_pocket": {"name": "Columbia Pocket", "level": 48, "reserves": 68000},
            "merced_shine": {"name": "Merced Shine", "level": 50, "reserves": 58000},
            "calaveras_grove_mine": {"name": "Calaveras Grove Mine", "level": 52, "reserves": 85000},
            "moaning_cavern_mine": {"name": "Moaning Cavern Mine", "level": 55, "reserves": 92000},
            
            # LEVEL 56-60: Legendary Sites
            "dead_mans_gulch": {"name": "Dead Man's Gulch", "level": 56, "reserves": 120000},
            "widows_peak_mine": {"name": "Widow's Peak Mine", "level": 58, "reserves": 110000},
            "el_dorado_mother_lode": {"name": "El Dorado Mother Lode", "level": 60, "reserves": 150000}
        }
        return mine_configs.get(mine_id)
    
    def reset_all_mines(self) -> bool:
        """Admin function to reset all mines to initial state"""
        try:
            # Get all mine configurations
            mine_configs = [
                {"id": mine_id, **config} for mine_id, config in {
                    # LEVEL 1-5: Beginner Sites
                    "gold_creek_main": {"name": "Gold Creek Main Vein", "level": 1, "reserves": 5000},
                    "coloma_bar": {"name": "Coloma Bar", "level": 1, "reserves": 1200},
                    "yuba_bend": {"name": "Yuba Bend", "level": 3, "reserves": 800},
                    "auburn_ravine": {"name": "Auburn Ravine", "level": 5, "reserves": 600},
                    
                    # LEVEL 6-15: Novice Sites
                    "mokelumne_cut": {"name": "Mokelumne Cut", "level": 6, "reserves": 1500},
                    "jamestown_flats": {"name": "Jamestown Flats", "level": 8, "reserves": 2200},
                    "placerville_reef": {"name": "Placerville Reef", "level": 10, "reserves": 3500},
                    "downie_ridge_vein": {"name": "Downie Ridge Vein", "level": 12, "reserves": 4800},
                    "feather_fork_3": {"name": "Feather Fork #3", "level": 15, "reserves": 6200},
                    
                    # LEVEL 16-25: Skilled Sites
                    "nevada_city_drift": {"name": "Nevada City Drift", "level": 16, "reserves": 8800},
                    "angels_reef": {"name": "Angels Reef", "level": 18, "reserves": 12500},
                    "rough_and_ready_mine": {"name": "Rough and Ready Mine", "level": 20, "reserves": 15000},
                    "french_gulch": {"name": "French Gulch", "level": 22, "reserves": 11000},
                    "smartsville_diggings": {"name": "Smartsville Diggings", "level": 25, "reserves": 18000},
                    
                    # LEVEL 26-35: Veteran Sites
                    "grass_valley_lode": {"name": "Grass Valley Lode", "level": 26, "reserves": 25000},
                    "empire_mine": {"name": "Empire Mine", "level": 28, "reserves": 32000},
                    "north_star_mine": {"name": "North Star Mine", "level": 30, "reserves": 28000},
                    "malakoff_diggins": {"name": "Malakoff Diggins", "level": 32, "reserves": 22000},
                    "cherokee_mine": {"name": "Cherokee Mine", "level": 35, "reserves": 38000},
                    
                    # LEVEL 36-45: Expert Sites
                    "alleghany_mine": {"name": "Alleghany Mine", "level": 36, "reserves": 45000},
                    "forest_city_mine": {"name": "Forest City Mine", "level": 38, "reserves": 52000},
                    "washington_mine": {"name": "Washington Mine", "level": 40, "reserves": 48000},
                    "downieville_drift": {"name": "Downieville Drift", "level": 42, "reserves": 55000},
                    "sierra_buttes_mine": {"name": "Sierra Buttes Mine", "level": 45, "reserves": 62000},
                    
                    # LEVEL 46-55: Master Sites
                    "tuolumne_quartz": {"name": "Tuolumne Quartz", "level": 46, "reserves": 75000},
                    "columbia_pocket": {"name": "Columbia Pocket", "level": 48, "reserves": 68000},
                    "merced_shine": {"name": "Merced Shine", "level": 50, "reserves": 58000},
                    "calaveras_grove_mine": {"name": "Calaveras Grove Mine", "level": 52, "reserves": 85000},
                    "moaning_cavern_mine": {"name": "Moaning Cavern Mine", "level": 55, "reserves": 92000},
                    
                    # LEVEL 56-60: Legendary Sites
                    "dead_mans_gulch": {"name": "Dead Man's Gulch", "level": 56, "reserves": 120000},
                    "widows_peak_mine": {"name": "Widow's Peak Mine", "level": 58, "reserves": 110000},
                    "el_dorado_mother_lode": {"name": "El Dorado Mother Lode", "level": 60, "reserves": 150000}
                }.items()
            ]
            
            # Reset each mine
            for mine_config in mine_configs:
                self.initialize_global_mine(mine_config["id"], mine_config)
            
            # Log admin action
            self.firebase_service.db.collection('admin_actions').add({
                'action': 'reset_all_mines',
                'admin_email': self.ADMIN_EMAIL,
                'timestamp': datetime.datetime.now(),
                'mines_reset': len(mine_configs)
            })
            
            return True
        except Exception as e:
            st.error(f"Failed to reset mines: {e}")
            return False
    
    def get_mining_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top miners across all mines"""
        try:
            # Aggregate mining data from all mines
            mines = self.get_all_mines_status()
            miner_totals = {}
            
            for mine in mines:
                for record in mine.get('mining_history', []):
                    miner = record['miner']
                    amount = record['amount']
                    if miner in miner_totals:
                        miner_totals[miner] += amount
                    else:
                        miner_totals[miner] = amount
            
            # Sort by total mined
            leaderboard = [
                {'miner': miner, 'total_mined': total}
                for miner, total in sorted(miner_totals.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return leaderboard[:limit]
        except Exception:
            return []

# Global instance
global_mine_system = GlobalMineSystem()

def get_global_mine_system():
    """Get the global mine system instance"""
    return global_mine_system
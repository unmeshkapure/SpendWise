from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from ..config.database import SessionLocal
from ..models.saving_goal import SavingsGoal

logger = logging.getLogger(__name__)

class GoalScheduler:
    """Background job scheduler for timed-lock goals"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Check for expired goals every hour
        self.scheduler.add_job(
            self.check_expired_goals,
            IntervalTrigger(hours=1),
            id='check_expired_goals',
            name='Check for expired savings goals',
            replace_existing=True
        )
        
        logger.info("Scheduled jobs set up successfully")
    
    def check_expired_goals(self):
        """Check for savings goals that have reached their target date"""
        logger.info("Checking for expired savings goals...")
        
        # Create a new database session
        db: Session = SessionLocal()
        
        try:
            # Find goals that are locked and have reached their target date
            expired_goals = db.query(SavingsGoal).filter(
                SavingsGoal.is_locked == True,
                SavingsGoal.target_date <= datetime.now(),
                SavingsGoal.is_completed == False
            ).all()
            
            updated_count = 0
            for goal in expired_goals:
                goal.is_locked = False
                goal.unlocked_at = datetime.now()
                
                # Check if goal is completed
                if goal.current_amount >= goal.target_amount:
                    goal.is_completed = True
                
                updated_count += 1
            
            if updated_count > 0:
                db.commit()
                logger.info(f"Unlocked {updated_count} savings goals")
            else:
                logger.info("No goals to unlock")
                
        except Exception as e:
            logger.error(f"Error in scheduled job: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down")